#!/usr/bin/env python3
"""Validate Astro blog content sources."""

from __future__ import annotations

import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "src" / "content" / "blog"
REQUIRED_META_FIELDS = ("title", "date")


class PipelineError(RuntimeError):
    """Raised when content validation fails."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").lstrip("\ufeff")
    except UnicodeDecodeError as exc:
        raise PipelineError(f"{path} must be UTF-8 encoded") from exc


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


def parse_front_matter(path: Path) -> Dict[str, str]:
    raw = read_text(path)
    match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)\Z", raw, re.S)
    if not match:
        raise PipelineError(f"{path} must begin with YAML front matter")

    metadata_block = match.group(1)
    metadata: Dict[str, str] = {}
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
        metadata[key] = value.strip().strip('"').strip("'")

    for field in REQUIRED_META_FIELDS:
        if field not in metadata or metadata[field].strip() == "":
            raise PipelineError(f"{path} missing required field: {field}")

    parse_date(metadata["date"])
    return metadata


def slugify(stem: str) -> str:
    normalized = unicodedata.normalize("NFKC", stem).strip().lower()
    normalized = re.sub(r"[\s_]+", "-", normalized)
    normalized = re.sub(r"[^\w\-]+", "-", normalized, flags=re.UNICODE)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    if not normalized:
        raise PipelineError(f"Cannot derive slug from filename: {stem}")
    return normalized


def collect_sources() -> Tuple[int, int]:
    if not SOURCE_DIR.exists():
        return 0, 0

    seen_slugs: Dict[str, str] = {}
    count = 0
    for path in sorted(SOURCE_DIR.glob("*.md")):
        if not path.is_file():
            continue
        parse_front_matter(path)
        slug = slugify(path.stem)
        prior = seen_slugs.get(slug)
        if prior:
            raise PipelineError(
                f"Slug collision: {path.name} and {prior} both map to '{slug}'"
            )
        seen_slugs[slug] = path.name
        count += 1

    return count, len(seen_slugs)


def main() -> int:
    try:
        sources, unique_slugs = collect_sources()
    except PipelineError as exc:
        print(f"[blog-validate] ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"[blog-validate] Completed: sources={sources}, unique_slugs={unique_slugs}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
