#!/usr/bin/env python3
"""Generate Jekyll posts from author-friendly Markdown sources."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

PIPELINE_VERSION = 1
ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "content" / "blog"
POSTS_DIR = ROOT / "_posts"
MANIFEST_PATH = ROOT / ".blog-pipeline-manifest.json"
MARKER = "<!-- AUTO-GENERATED: blog-pipeline"
REQUIRED_META_FIELDS = ("title", "date")


class PipelineError(RuntimeError):
    """Raised when the pipeline cannot safely generate output."""


@dataclass
class SourceDocument:
    source_key: str
    source_path: Path
    slug: str
    metadata: Dict[str, object]
    body: str
    post_path: Path
    source_sha256: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").lstrip("\ufeff")
    except UnicodeDecodeError as exc:
        raise PipelineError(f"{path} must be UTF-8 encoded") from exc


def parse_quoted(value: str) -> str:
    if len(value) < 2:
        return value
    quote = value[0]
    if quote not in {"'", '"'} or value[-1] != quote:
        return value
    inner = value[1:-1]
    inner = inner.replace(r"\\", "\\")
    inner = inner.replace(r"\'", "'")
    inner = inner.replace(r"\"", '"')
    return inner


def parse_list(value: str) -> List[str]:
    inner = value[1:-1].strip()
    if not inner:
        return []
    items = [part.strip() for part in inner.split(",")]
    parsed = [parse_quoted(item) for item in items if item]
    return [item for item in parsed if item]


def parse_meta_value(raw: str) -> object:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        return parse_list(value)
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return parse_quoted(value)
    return value


def parse_date(value: str) -> datetime:
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(candidate)
    except ValueError:
        pass

    formats = (
        "%Y-%m-%d %H:%M:%S %z",
        "%Y-%m-%d %H:%M %z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    )
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise PipelineError(f"Unsupported date format: {value}")


def parse_front_matter(path: Path) -> Tuple[Dict[str, object], str]:
    raw = read_text(path)
    match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)\Z", raw, re.S)
    if not match:
        raise PipelineError(f"{path} must begin with YAML front matter")

    metadata_block, body = match.groups()
    metadata: Dict[str, object] = {}
    for raw_line in metadata_block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise PipelineError(f"{path} front matter line must contain ':'")
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise PipelineError(f"{path} contains an empty front matter key")
        metadata[key] = parse_meta_value(value)

    for field in REQUIRED_META_FIELDS:
        if field not in metadata or str(metadata[field]).strip() == "":
            raise PipelineError(f"{path} missing required field: {field}")

    parse_date(str(metadata["date"]))
    return metadata, body


def normalize_tag_list(metadata: Dict[str, object], key: str) -> List[str]:
    if key not in metadata:
        return []
    raw = metadata[key]
    if isinstance(raw, list):
        values = [str(item).strip() for item in raw]
    else:
        values = [part.strip() for part in str(raw).split(",")]
    return [item for item in values if item]


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_list(values: List[str]) -> str:
    return "[" + ", ".join(yaml_quote(item) for item in values) + "]"


def rel_posix(path: Path) -> str:
    return path.as_posix()


def source_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def slugify(stem: str) -> str:
    normalized = unicodedata.normalize("NFKC", stem).strip().lower()
    normalized = re.sub(r"[\s_]+", "-", normalized)
    normalized = re.sub(r"[^\w\-]+", "-", normalized, flags=re.UNICODE)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    if not normalized:
        raise PipelineError(f"Cannot derive slug from filename: {stem}")
    return normalized


def protect_segments(text: str) -> Tuple[str, Dict[str, str]]:
    placeholders: Dict[str, str] = {}
    counter = 0

    def stash(pattern: re.Pattern[str], content: str) -> str:
        nonlocal counter

        def replacer(match: re.Match[str]) -> str:
            nonlocal counter
            token = f"@@BLOG_PLACEHOLDER_{counter}@@"
            counter += 1
            placeholders[token] = match.group(0)
            return token

        return pattern.sub(replacer, content)

    fenced_patterns = (
        re.compile(r"(?ms)^[ \t]*```.*?^[ \t]*```[ \t]*\r?\n?"),
        re.compile(r"(?ms)^[ \t]*~~~.*?^[ \t]*~~~[ \t]*\r?\n?"),
    )
    inline_code_pattern = re.compile(r"`[^`\n]+`")

    protected = text
    for pattern in fenced_patterns:
        protected = stash(pattern, protected)
    protected = stash(inline_code_pattern, protected)
    return protected, placeholders


def restore_segments(text: str, placeholders: Dict[str, str]) -> str:
    restored = text
    for token, original in placeholders.items():
        restored = restored.replace(token, original)
    return restored


def normalize_math(text: str) -> str:
    protected, placeholders = protect_segments(text)

    def display_replacer(match: re.Match[str]) -> str:
        body = match.group(1).strip("\n")
        return f"\n\\[\n{body}\n\\]\n"

    protected = re.sub(
        r"(?<!\\)\$\$(.+?)(?<!\\)\$\$",
        display_replacer,
        protected,
        flags=re.S,
    )
    protected = re.sub(
        r"(?<!\\)\$(?!\$)([^$\n]+?)(?<!\\)\$",
        lambda match: rf"\({match.group(1)}\)",
        protected,
    )
    return restore_segments(protected, placeholders)


def load_manifest() -> Dict[str, Dict[str, str]]:
    if not MANIFEST_PATH.exists():
        return {}
    raw = read_text(MANIFEST_PATH).strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid JSON in {MANIFEST_PATH}") from exc
    entries = payload.get("entries", {})
    if not isinstance(entries, dict):
        raise PipelineError(f"{MANIFEST_PATH} must contain an 'entries' object")
    normalized: Dict[str, Dict[str, str]] = {}
    for key, entry in entries.items():
        if not isinstance(entry, dict):
            continue
        normalized[key] = {
            "post": str(entry.get("post", "")),
            "source_sha256": str(entry.get("source_sha256", "")),
            "pipeline_version": str(entry.get("pipeline_version", "")),
        }
    return normalized


def save_manifest(entries: Dict[str, Dict[str, str]]) -> bool:
    payload = {"pipeline_version": PIPELINE_VERSION, "entries": entries}
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if MANIFEST_PATH.exists() and read_text(MANIFEST_PATH) == content:
        return False
    MANIFEST_PATH.write_text(content, encoding="utf-8")
    return True


def write_text_if_changed(path: Path, content: str) -> bool:
    if path.exists() and read_text(path) == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def remove_file_if_exists(path: Path) -> bool:
    if not path.exists():
        return False
    path.unlink()
    return True


def collect_sources() -> List[Path]:
    if not SOURCE_DIR.exists():
        return []
    return sorted(path for path in SOURCE_DIR.glob("*.md") if path.is_file())


def build_document(path: Path) -> SourceDocument:
    metadata, body = parse_front_matter(path)
    slug = slugify(path.stem)
    date_prefix = parse_date(str(metadata["date"])).date().isoformat()
    post_name = f"{date_prefix}-{slug}.md"
    return SourceDocument(
        source_key=path.name,
        source_path=path,
        slug=slug,
        metadata=metadata,
        body=body,
        post_path=POSTS_DIR / post_name,
        source_sha256=source_sha256(path),
    )


def render_post(doc: SourceDocument) -> str:
    categories = normalize_tag_list(doc.metadata, "categories") or ["blog"]
    tags = normalize_tag_list(doc.metadata, "tags")
    lines: List[str] = [
        "---",
        "layout: post",
        f"title: {yaml_quote(str(doc.metadata['title']))}",
        f"date: {yaml_quote(str(doc.metadata['date']))}",
        f"categories: {yaml_list(categories)}",
    ]
    if tags:
        lines.append(f"tags: {yaml_list(tags)}")
    lines.extend(
        [
            f"blog_source: {yaml_quote('/' + rel_posix(doc.source_path.relative_to(ROOT)))}",
            "---",
            "",
            f"{MARKER} source={rel_posix(doc.source_path.relative_to(ROOT))} -->",
            "",
            normalize_math(doc.body).rstrip("\n"),
            "",
        ]
    )
    return "\n".join(lines)


def should_skip_generation(doc: SourceDocument, old_entry: Dict[str, str] | None) -> bool:
    if not old_entry:
        return False
    if old_entry.get("pipeline_version") != str(PIPELINE_VERSION):
        return False
    if old_entry.get("source_sha256") != doc.source_sha256:
        return False
    old_post = ROOT / old_entry.get("post", "")
    return old_post == doc.post_path and old_post.exists()


def run_pipeline() -> Tuple[int, int]:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    old_entries = load_manifest()
    new_entries: Dict[str, Dict[str, str]] = {}
    changed_files = 0
    used_slugs: Dict[str, str] = {}

    for source_path in collect_sources():
        doc = build_document(source_path)
        prior_source = used_slugs.get(doc.slug)
        if prior_source:
            raise PipelineError(
                f"Slug collision: {source_path.name} and {prior_source} both map to '{doc.slug}'"
            )
        used_slugs[doc.slug] = source_path.name

        old_entry = old_entries.get(doc.source_key)
        if not should_skip_generation(doc, old_entry):
            if write_text_if_changed(doc.post_path, render_post(doc)):
                changed_files += 1

        new_entries[doc.source_key] = {
            "post": rel_posix(doc.post_path.relative_to(ROOT)),
            "source_sha256": doc.source_sha256,
            "pipeline_version": str(PIPELINE_VERSION),
        }

    for source_key, old_entry in old_entries.items():
        old_post = ROOT / old_entry.get("post", "")
        if source_key not in new_entries:
            if remove_file_if_exists(old_post):
                changed_files += 1
            continue
        new_post = ROOT / new_entries[source_key]["post"]
        if old_post != new_post and remove_file_if_exists(old_post):
            changed_files += 1

    if save_manifest(new_entries):
        changed_files += 1

    return len(new_entries), changed_files


def main() -> int:
    try:
        posts_expected, changed = run_pipeline()
    except PipelineError as exc:
        print(f"[blog-pipeline] ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"[blog-pipeline] Completed: expected_posts={posts_expected}, changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
