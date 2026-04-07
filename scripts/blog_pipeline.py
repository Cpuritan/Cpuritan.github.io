#!/usr/bin/env python3
"""Sync legacy `_posts` sources into Astro content + validate generated entries."""

from __future__ import annotations

import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
LEGACY_POSTS_DIR = ROOT / "_posts"
TARGET_DIR = ROOT / "src" / "content" / "blog"
TARGET_ASSET_DIR = ROOT / "public" / "assets" / "posts"
MANIFEST_PATH = ROOT / ".astro-blog-sync-manifest.json"

PIPELINE_VERSION = 2
AUTO_MARKER = "<!-- AUTO-GENERATED: scripts/blog_pipeline.py -->"
CN_TZ = timezone(timedelta(hours=8))

DATE_FILE_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.+)$")
HEADING_RE = re.compile(r"^\s{0,3}#\s+(.+?)\s*$", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)\Z", re.S)
OBSIDIAN_IMAGE_RE = re.compile(r"!\[\[([^\]]+)\]\]")
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

REMOTE_URL_RE = re.compile(r"^(?:https?:|mailto:|data:|tel:|#|/)", re.IGNORECASE)

REQUIRED_META_FIELDS = ("title", "date")
FIXABLE_PATTERNS = {
    "broken_svg_tag_close": re.compile(r"\?\/text>", re.IGNORECASE),
    "suspicious_math_before_dollar": re.compile(r"\?\$(?=\$|\\|[A-Za-z(\[{])"),
    "suspicious_math_after_dollar": re.compile(r"\$\?(?=\$|\\|[A-Za-z(\[{])"),
    "suspicious_math_before_tex_command": re.compile(r"\?\\[A-Za-z]+"),
}
FENCED_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```|~~~[\s\S]*?~~~", re.MULTILINE)


class PipelineError(RuntimeError):
    """Raised when sync or validation fails."""


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise PipelineError(f"{path} must be UTF-8 encoded") from exc
    return text.replace("\r\n", "\n")


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
            return datetime.strptime(candidate, fmt)
        except ValueError:
            continue
    raise PipelineError(f"Unsupported date format: {value}")


def split_front_matter(raw: str) -> Tuple[Dict[str, str], Dict[str, str], str]:
    match = FRONT_MATTER_RE.match(raw)
    if not match:
        return {}, {}, raw

    metadata_block = match.group(1)
    body = match.group(2)

    metadata: Dict[str, str] = {}
    raw_values: Dict[str, str] = {}
    for raw_line in metadata_block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        raw_values[key] = value
        metadata[key] = value.strip().strip('"').strip("'")

    return metadata, raw_values, body


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).strip().lower()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[\s_]+", "-", normalized)
    normalized = re.sub(r"[^\w\-]+", "-", normalized, flags=re.UNICODE)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    if normalized:
        return normalized
    return "post"


def heading_from_body(body: str) -> Optional[str]:
    match = HEADING_RE.search(body)
    if not match:
        return None
    return match.group(1).strip()


def normalize_title(raw_title: str) -> str:
    value = raw_title.strip().strip('"').strip("'")
    value = re.sub(r"\s+", " ", value)
    return value or "Untitled"


def derive_date_from_source(path: Path, metadata: Dict[str, str]) -> datetime:
    if metadata.get("date"):
        return parse_date(metadata["date"])

    date_match = DATE_FILE_RE.match(path.stem)
    if date_match:
        return parse_date(date_match.group("date"))

    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=CN_TZ)
    return modified


def derive_base_slug(path: Path, metadata: Dict[str, str]) -> str:
    if metadata.get("slug"):
        return slugify(metadata["slug"])

    date_match = DATE_FILE_RE.match(path.stem)
    if date_match:
        return slugify(date_match.group("slug"))
    return slugify(path.stem)


def derive_title(path: Path, metadata: Dict[str, str], body: str) -> str:
    if metadata.get("title"):
        return normalize_title(metadata["title"])

    heading = heading_from_body(body)
    if heading:
        return normalize_title(heading)

    date_match = DATE_FILE_RE.match(path.stem)
    stem = date_match.group("slug") if date_match else path.stem
    return normalize_title(stem.replace("-", " "))


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def format_date_for_front_matter(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CN_TZ)
    dt = dt.astimezone(CN_TZ)
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def resolve_local_asset(source_file: Path, raw_target: str) -> Optional[Path]:
    cleaned = raw_target.strip().strip('"').strip("'")
    cleaned = cleaned.strip("<>").strip()
    if not cleaned or REMOTE_URL_RE.match(cleaned):
        return None

    candidate = (source_file.parent / cleaned).resolve()
    if candidate.exists() and candidate.is_file():
        return candidate

    return None


def url_for_asset(slug: str, relative_asset_path: Path) -> str:
    parts = ["assets", "posts", quote(slug, safe="")]
    parts.extend(quote(part, safe="") for part in relative_asset_path.parts)
    return "/" + "/".join(parts)


def copy_asset(
    source_file: Path,
    asset_file: Path,
    slug: str,
    expected_asset_relpaths: Set[str],
) -> str:
    try:
        rel_to_source = asset_file.relative_to(source_file.parent)
    except ValueError:
        rel_to_source = Path(asset_file.name)

    destination = TARGET_ASSET_DIR / slug / rel_to_source
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(asset_file, destination)
    expected_asset_relpaths.add(destination.relative_to(ROOT).as_posix())
    return url_for_asset(slug, rel_to_source)


def rewrite_obsidian_images(
    text: str,
    source_file: Path,
    slug: str,
    expected_asset_relpaths: Set[str],
) -> str:
    def replacement(match: re.Match[str]) -> str:
        inner = match.group(1).replace(r"\|", "|").strip()
        parts = [part.strip() for part in inner.split("|") if part.strip()]
        if not parts:
            return match.group(0)

        target = parts[0]
        width = next((part for part in parts[1:] if part.isdigit()), "")
        asset = resolve_local_asset(source_file, target)
        if not asset:
            return match.group(0)

        url = copy_asset(source_file, asset, slug, expected_asset_relpaths)
        alt = html_escape(asset.stem)
        if width:
            return f'<img src="{url}" alt="{alt}" width="{width}" loading="lazy" />'
        return f"![{alt}]({url})"

    return OBSIDIAN_IMAGE_RE.sub(replacement, text)


def rewrite_markdown_images(
    text: str,
    source_file: Path,
    slug: str,
    expected_asset_relpaths: Set[str],
) -> str:
    def replacement(match: re.Match[str]) -> str:
        alt = match.group(1)
        target = match.group(2).strip()
        if REMOTE_URL_RE.match(target):
            return match.group(0)

        asset = resolve_local_asset(source_file, target)
        if not asset:
            return match.group(0)

        url = copy_asset(source_file, asset, slug, expected_asset_relpaths)
        return f"![{alt}]({url})"

    return MARKDOWN_IMAGE_RE.sub(replacement, text)


def rewrite_body_for_assets(
    body: str,
    source_file: Path,
    slug: str,
    expected_asset_relpaths: Set[str],
) -> str:
    updated = rewrite_obsidian_images(body, source_file, slug, expected_asset_relpaths)
    updated = rewrite_markdown_images(updated, source_file, slug, expected_asset_relpaths)
    return updated


def inspect_content(path: Path, body: str) -> List[str]:
    issues: List[str] = []
    check_text = FENCED_CODE_BLOCK_RE.sub("", body)

    open_svg = len(re.findall(r"<svg\b", check_text, flags=re.IGNORECASE))
    close_svg = len(re.findall(r"</svg>", check_text, flags=re.IGNORECASE))
    if open_svg != close_svg:
        raise PipelineError(
            f"{path} has unmatched SVG block count: <svg={open_svg}, </svg>={close_svg}"
        )

    for issue_name, pattern in FIXABLE_PATTERNS.items():
        count = len(pattern.findall(check_text))
        if count > 0:
            issues.append(f"{path} -> {issue_name}: {count}")
    return issues


def ensure_unique_slug(
    proposed_slug: str, source_path: Path, used_slugs: Dict[str, Path]
) -> str:
    if proposed_slug not in used_slugs:
        used_slugs[proposed_slug] = source_path
        return proposed_slug

    parent_hint = slugify(source_path.parent.name) if source_path.parent != LEGACY_POSTS_DIR else ""
    if parent_hint:
        candidate = f"{parent_hint}-{proposed_slug}"
        if candidate not in used_slugs:
            used_slugs[candidate] = source_path
            return candidate

    counter = 2
    while True:
        candidate = f"{proposed_slug}-{counter}"
        if candidate not in used_slugs:
            used_slugs[candidate] = source_path
            return candidate
        counter += 1


def load_manifest() -> Dict[str, object]:
    if not MANIFEST_PATH.exists():
        return {}
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if current == content:
            return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def safe_unlink(path: Path) -> bool:
    if path.exists() and path.is_file():
        path.unlink()
        return True
    return False


def cleanup_removed(
    prior_paths: Iterable[str],
    expected_paths: Set[str],
    must_have_marker: bool,
) -> int:
    removed = 0
    for rel in prior_paths:
        if rel in expected_paths:
            continue
        abs_path = ROOT / rel
        if not abs_path.exists() or not abs_path.is_file():
            continue
        if must_have_marker:
            try:
                if AUTO_MARKER not in abs_path.read_text(encoding="utf-8"):
                    continue
            except UnicodeDecodeError:
                continue
        if safe_unlink(abs_path):
            removed += 1
    return removed


def prune_empty_asset_dirs() -> None:
    if not TARGET_ASSET_DIR.exists():
        return
    for directory in sorted(
        TARGET_ASSET_DIR.rglob("*"), key=lambda p: len(p.parts), reverse=True
    ):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def build_generated_markdown(
    title: str,
    date: datetime,
    body: str,
    raw_meta: Dict[str, str],
) -> str:
    lines: List[str] = [
        "---",
        f"title: {yaml_quote(title)}",
        f"date: {format_date_for_front_matter(date)}",
    ]
    for optional_key in ("tags", "categories", "description", "draft"):
        value = raw_meta.get(optional_key, "").strip()
        if value:
            lines.append(f"{optional_key}: {value}")
    lines.extend(["---", "", AUTO_MARKER, ""])
    cleaned_body = body.lstrip("\n").rstrip()
    lines.append(cleaned_body)
    lines.append("")
    return "\n".join(lines)


def sync_posts() -> Tuple[int, int, int, int]:
    if not LEGACY_POSTS_DIR.exists():
        raise PipelineError(f"Legacy source dir not found: {LEGACY_POSTS_DIR}")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_ASSET_DIR.mkdir(parents=True, exist_ok=True)

    legacy_files = sorted(
        [path for path in LEGACY_POSTS_DIR.rglob("*.md") if path.is_file()],
        key=lambda p: p.as_posix().lower(),
    )
    if not legacy_files:
        raise PipelineError(f"No markdown files found in {LEGACY_POSTS_DIR}")

    prior_manifest = load_manifest()
    prior_posts = set(prior_manifest.get("generated_posts", []))
    prior_assets = set(prior_manifest.get("generated_assets", []))

    used_slugs: Dict[str, Path] = {}
    expected_posts: Set[str] = set()
    expected_assets: Set[str] = set()
    warnings: List[str] = []
    written_posts = 0

    for source in legacy_files:
        raw = read_text(source)
        metadata, raw_meta, body = split_front_matter(raw)
        base_slug = derive_base_slug(source, metadata)
        slug = ensure_unique_slug(base_slug, source, used_slugs)
        title = derive_title(source, metadata, body)
        date_value = derive_date_from_source(source, metadata)

        rewritten_body = rewrite_body_for_assets(body, source, slug, expected_assets)
        warnings.extend(inspect_content(source, rewritten_body))

        output = build_generated_markdown(title, date_value, rewritten_body, raw_meta)
        output_path = TARGET_DIR / f"{slug}.md"
        if write_if_changed(output_path, output):
            written_posts += 1
        expected_posts.add(output_path.relative_to(ROOT).as_posix())

    removed_posts = cleanup_removed(prior_posts, expected_posts, must_have_marker=True)
    removed_assets = cleanup_removed(prior_assets, expected_assets, must_have_marker=False)
    prune_empty_asset_dirs()

    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "pipeline_version": PIPELINE_VERSION,
                "generated_posts": sorted(expected_posts),
                "generated_assets": sorted(expected_assets),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    for warning in warnings:
        print(f"[blog-sync] WARN: {warning}")

    return len(legacy_files), written_posts, removed_posts, removed_assets


def validate_generated() -> Tuple[int, int]:
    files = sorted(TARGET_DIR.glob("*.md"))
    if not files:
        raise PipelineError(f"No generated posts found in {TARGET_DIR}")

    seen_slugs: Dict[str, Path] = {}
    warning_count = 0
    for path in files:
        raw = read_text(path)
        metadata, _, body = split_front_matter(raw)
        for field in REQUIRED_META_FIELDS:
            if not metadata.get(field, "").strip():
                raise PipelineError(f"{path} missing required field: {field}")
        parse_date(metadata["date"])

        slug = slugify(path.stem)
        prior = seen_slugs.get(slug)
        if prior:
            raise PipelineError(
                f"Slug collision: {path.name} and {prior.name} both map to '{slug}'"
            )
        seen_slugs[slug] = path

        warning_count += len(inspect_content(path, body))

    return len(files), warning_count


def main() -> int:
    try:
        source_count, written, removed_posts, removed_assets = sync_posts()
        generated_count, warning_count = validate_generated()
    except PipelineError as exc:
        print(f"[blog-sync] ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        "[blog-sync] Completed: "
        f"sources={source_count}, generated={generated_count}, "
        f"written={written}, removed_posts={removed_posts}, removed_assets={removed_assets}, "
        f"warnings={warning_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
