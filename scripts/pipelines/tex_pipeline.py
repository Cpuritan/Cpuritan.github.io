#!/usr/bin/env python3
"""Convert LaTeX sources into Astro blog content and PDF backups.

Source files:
  latex/<slug>.tex

Generated files:
  src/content/blog/<slug>.md
  public/assets/papers/<slug>.pdf
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

PIPELINE_VERSION = 1
REQUIRED_META_FIELDS = ("title", "date")
MARKER = "<!-- AUTO-GENERATED: latex-pipeline"

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "latex"
CONTENT_DIR = ROOT / "src" / "content" / "blog"
PDF_DIR = ROOT / "public" / "assets" / "papers"
MANIFEST_PATH = ROOT / "scripts" / "state" / "latex-pipeline.json"


class PipelineError(RuntimeError):
    """Raised when the conversion pipeline cannot continue safely."""


@dataclass
class SourceDocument:
    slug: str
    source_path: Path
    metadata: Dict[str, object]
    content_path: Path
    pdf_path: Path
    source_sha256: str


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise PipelineError(f"Missing required command: {name}")


def rel_posix(path: Path) -> str:
    return path.as_posix()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
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
    inner = inner.replace(r'\"', '"')
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


def comment_content(line: str) -> str | None:
    stripped = line.lstrip()
    if not stripped.startswith("%"):
        return None
    payload = stripped[1:]
    if payload.startswith(" "):
        payload = payload[1:]
    return payload.rstrip("\n")


def parse_metadata(path: Path) -> Dict[str, object]:
    lines = read_text(path).splitlines(keepends=True)
    if not lines:
        raise PipelineError(f"{path} is empty")

    index = 0
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines):
        raise PipelineError(f"{path} contains only whitespace")

    opening = comment_content(lines[index])
    if opening is None or opening.strip() != "---":
        raise PipelineError(f"{path} must start with commented front matter: % ---")
    index += 1

    metadata_lines: List[str] = []
    while index < len(lines):
        payload = comment_content(lines[index])
        if payload is None:
            raise PipelineError(
                f"{path} front matter line must be a comment starting with %"
            )
        if payload.strip() == "---":
            break
        metadata_lines.append(payload)
        index += 1

    if index >= len(lines):
        raise PipelineError(f"{path} front matter is missing closing % ---")

    metadata: Dict[str, object] = {}
    for raw_line in metadata_lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise PipelineError(
                f"{path} front matter line must contain ':': {raw_line.strip()}"
            )
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise PipelineError(f"{path} contains an empty front matter key")
        metadata[key] = parse_meta_value(value)

    for field in REQUIRED_META_FIELDS:
        if field not in metadata or str(metadata[field]).strip() == "":
            raise PipelineError(f"{path} missing required field: {field}")

    parse_date(str(metadata["date"]))
    return metadata


def normalize_tag_list(metadata: Dict[str, object], key: str) -> List[str]:
    if key not in metadata:
        return []
    raw = metadata[key]
    if isinstance(raw, list):
        values = [str(item).strip() for item in raw]
    else:
        values = [part.strip() for part in str(raw).split(",")]
    clean = [item for item in values if item]
    return clean


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_list(values: List[str]) -> str:
    return "[" + ", ".join(yaml_quote(item) for item in values) + "]"


def source_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def pandoc_to_markdown(source: Path) -> str:
    cmd = [
        "pandoc",
        "--from=latex",
        "--to=gfm+tex_math_dollars",
        "--wrap=none",
        rel_posix(source),
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise PipelineError(f"Pandoc failed for {source}:\n{proc.stderr.strip()}")
    body = proc.stdout.strip()
    return body + "\n" if body else ""


def build_pdf(source: Path, target_pdf: Path) -> bool:
    with tempfile.TemporaryDirectory(prefix="tex-pipeline-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        cmd = ["tectonic", "--outdir", rel_posix(tmp_path), rel_posix(source)]
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise PipelineError(f"Tectonic failed for {source}:\n{proc.stderr.strip()}")
        pdf_name = source.with_suffix(".pdf").name
        generated_pdf = tmp_path / pdf_name
        if not generated_pdf.exists():
            raise PipelineError(f"Tectonic did not produce {pdf_name}")
        target_pdf.parent.mkdir(parents=True, exist_ok=True)
        if target_pdf.exists() and target_pdf.read_bytes() == generated_pdf.read_bytes():
            return False
        shutil.copy2(generated_pdf, target_pdf)
        return True


def compose_content_markdown(doc: SourceDocument, markdown_body: str) -> str:
    title = str(doc.metadata["title"])
    date_str = str(doc.metadata["date"])
    categories = normalize_tag_list(doc.metadata, "categories")
    tags = normalize_tag_list(doc.metadata, "tags")

    lines: List[str] = [
        "---",
        f"title: {yaml_quote(title)}",
        f"date: {yaml_quote(date_str)}",
    ]
    if categories:
        lines.append(f"categories: {yaml_list(categories)}")
    if tags:
        lines.append(f"tags: {yaml_list(tags)}")
    lines.extend(
        [
            f"latex_source: {yaml_quote('/latex/' + doc.source_path.name)}",
            f"latex_pdf: {yaml_quote('/assets/papers/' + doc.slug + '.pdf')}",
            "---",
            "",
            f"{MARKER} source=latex/{doc.slug}.tex -->",
            "",
            f"> Auto-generated from `latex/{doc.slug}.tex`.",
            f"> PDF backup: [Open PDF](/assets/papers/{doc.slug}.pdf)",
            "",
        ]
    )
    if markdown_body:
        lines.append(markdown_body.rstrip("\n"))
    lines.append("")
    return "\n".join(lines)


def write_text_if_changed(path: Path, content: str) -> bool:
    if path.exists() and read_text(path) == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def is_generated_content(path: Path) -> bool:
    if not path.exists():
        return False
    return MARKER in read_text(path)


def remove_file_if_exists(path: Path) -> bool:
    if not path.exists():
        return False
    path.unlink()
    return True


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
    return entries


def save_manifest(entries: Dict[str, Dict[str, str]]) -> bool:
    payload = {"pipeline_version": PIPELINE_VERSION, "entries": entries}
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return write_text_if_changed(MANIFEST_PATH, content)


def build_document_plan(source_path: Path) -> SourceDocument:
    metadata = parse_metadata(source_path)
    slug = source_path.stem
    content_path = CONTENT_DIR / f"{slug}.md"
    pdf_path = PDF_DIR / f"{slug}.pdf"
    return SourceDocument(
        slug=slug,
        source_path=source_path,
        metadata=metadata,
        content_path=content_path,
        pdf_path=pdf_path,
        source_sha256=source_sha256(source_path),
    )


def should_skip_generation(doc: SourceDocument, old_entry: Dict[str, str] | None) -> bool:
    if not old_entry:
        return False
    if old_entry.get("pipeline_version") != str(PIPELINE_VERSION):
        return False
    if old_entry.get("source_sha256") != doc.source_sha256:
        return False
    old_content = ROOT / old_entry.get("content", "")
    old_pdf = ROOT / old_entry.get("pdf", "")
    if old_content != doc.content_path or old_pdf != doc.pdf_path:
        return False
    return old_content.exists() and old_pdf.exists()


def normalize_old_entries(raw_entries: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    normalized: Dict[str, Dict[str, str]] = {}
    for slug, entry in raw_entries.items():
        if not isinstance(entry, dict):
            continue
        normalized[slug] = {
            "source_sha256": str(entry.get("source_sha256", "")),
            "content": str(entry.get("content", "")),
            "pdf": str(entry.get("pdf", "")),
            "pipeline_version": str(entry.get("pipeline_version", "")),
        }
    return normalized


def collect_sources() -> List[Path]:
    if not SOURCE_DIR.exists():
        return []
    return sorted(path for path in SOURCE_DIR.glob("*.tex") if path.is_file())


def run_pipeline() -> Tuple[int, int, int]:
    require_command("pandoc")
    require_command("tectonic")

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    old_entries = normalize_old_entries(load_manifest())
    new_entries: Dict[str, Dict[str, str]] = {}
    changed_files = 0
    processed_sources = 0

    for source in collect_sources():
        processed_sources += 1
        doc = build_document_plan(source)
        old_entry = old_entries.get(doc.slug)

        if not old_entry and doc.content_path.exists() and not is_generated_content(
            doc.content_path
        ):
            raise PipelineError(
                f"Refusing to overwrite manually maintained content file: {doc.content_path}"
            )

        if not should_skip_generation(doc, old_entry):
            markdown_body = pandoc_to_markdown(source)
            if build_pdf(source, doc.pdf_path):
                changed_files += 1
            content_text = compose_content_markdown(doc, markdown_body)
            if write_text_if_changed(doc.content_path, content_text):
                changed_files += 1

        new_entries[doc.slug] = {
            "source_sha256": doc.source_sha256,
            "content": rel_posix(doc.content_path.relative_to(ROOT)),
            "pdf": rel_posix(doc.pdf_path.relative_to(ROOT)),
            "pipeline_version": str(PIPELINE_VERSION),
        }

    for slug, old_entry in old_entries.items():
        old_content = ROOT / old_entry.get("content", "")
        old_pdf = ROOT / old_entry.get("pdf", "")
        if slug not in new_entries:
            if remove_file_if_exists(old_content):
                changed_files += 1
            if remove_file_if_exists(old_pdf):
                changed_files += 1
            continue
        new_content = ROOT / new_entries[slug]["content"]
        if old_content != new_content and remove_file_if_exists(old_content):
            changed_files += 1

    if save_manifest(new_entries):
        changed_files += 1

    return processed_sources, len(new_entries), changed_files


def main() -> int:
    try:
        sources_scanned, contents_expected, changed = run_pipeline()
    except PipelineError as exc:
        print(f"[latex-pipeline] ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        "[latex-pipeline] Completed: "
        f"sources={sources_scanned}, expected_contents={contents_expected}, changed={changed}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
