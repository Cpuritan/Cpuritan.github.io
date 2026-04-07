#!/usr/bin/env python3
"""Validate blog markdown integrity before build/deploy."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "src" / "content" / "blog"

FENCED_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```|~~~[\s\S]*?~~~", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\r\n]+`")

BROKEN_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    (
        "legacy_generated_marker",
        re.compile(r"AUTO-GENERATED:\s*scripts/blog_pipeline\.py"),
    ),
    ("broken_svg_close_tag", re.compile(r"\?\/text>", re.IGNORECASE)),
    ("replacement_character", re.compile("\uFFFD")),
)

MOJIBAKE_TOKENS = (
    "\u95c6\u8dfa\u656d",
    "\u9369\u8f70\u7c2c",
    "\u9422\u71bc\u77de",
    "\u9411\ue15e\u752b",
    "\u95c2\ue1c0\ue57d",
    "\u7481\uff04\u757b",
    "\u6d7c\u6a3a\u5bf2",
)

PRIVATE_USE_RE = re.compile(r"[\uE000-\uF8FF]")
KANA_BOPOMOFO_RE = re.compile(r"[\u3040-\u30FF\u3100-\u312F]")
EURO_RE = re.compile(r"\u20AC")
CJK_RE = re.compile(r"[\u4E00-\u9FFF]")

MOJIBAKE_KANA_THRESHOLD = 8
MOJIBAKE_EURO_THRESHOLD = 5


def read_utf8_strict(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: not valid UTF-8 ({exc})") from exc


def strip_code_blocks(text: str) -> str:
    without_fences = FENCED_CODE_BLOCK_RE.sub("", text)
    return INLINE_CODE_RE.sub("", without_fences)


def inspect_svg(path: Path, text: str) -> List[str]:
    issues: List[str] = []
    open_count = len(re.findall(r"<svg\b", text, flags=re.IGNORECASE))
    close_count = len(re.findall(r"</svg>", text, flags=re.IGNORECASE))

    if open_count != close_count:
        issues.append(
            f"{path}: unmatched svg tags (<svg={open_count}, </svg>={close_count})"
        )
        return issues

    blocks = re.findall(r"<svg\b[\s\S]*?</svg>", text, flags=re.IGNORECASE)
    for idx, block in enumerate(blocks, start=1):
        try:
            ET.fromstring(block)
        except ET.ParseError as exc:
            issues.append(f"{path}: svg#{idx} parse error ({exc})")
    return issues


def inspect_mojibake(path: Path, text: str) -> List[str]:
    issues: List[str] = []
    if not CJK_RE.search(text):
        return issues

    token_hits = 0
    for token in MOJIBAKE_TOKENS:
        token_hits += text.count(token)
    if token_hits > 0:
        issues.append(f"{path}: suspicious mojibake token hits={token_hits}")

    pua_count = len(PRIVATE_USE_RE.findall(text))
    kana_count = len(KANA_BOPOMOFO_RE.findall(text))
    euro_count = len(EURO_RE.findall(text))

    if pua_count > 0:
        issues.append(f"{path}: suspicious private-use chars count={pua_count}")
    if kana_count >= MOJIBAKE_KANA_THRESHOLD:
        issues.append(
            f"{path}: suspicious kana/bopomofo chars count={kana_count} "
            f"(threshold={MOJIBAKE_KANA_THRESHOLD})"
        )
    if euro_count >= MOJIBAKE_EURO_THRESHOLD:
        issues.append(
            f"{path}: suspicious euro-sign chars count={euro_count} "
            f"(threshold={MOJIBAKE_EURO_THRESHOLD})"
        )
    return issues


def inspect_patterns(path: Path, text: str) -> List[str]:
    issues: List[str] = []
    for name, pattern in BROKEN_PATTERNS:
        hits = len(pattern.findall(text))
        if hits > 0:
            issues.append(f"{path}: {name} count={hits}")
    return issues


def inspect_file(path: Path) -> List[str]:
    text = read_utf8_strict(path)
    scan_text = strip_code_blocks(text)
    issues: List[str] = []
    issues.extend(inspect_patterns(path, scan_text))
    issues.extend(inspect_mojibake(path, scan_text))
    issues.extend(inspect_svg(path, scan_text))
    return issues


def main() -> int:
    if not BLOG_DIR.exists():
        print(f"[content-guard] ERROR: missing blog dir: {BLOG_DIR}", file=sys.stderr)
        return 1

    files = sorted(BLOG_DIR.glob("*.md"))
    if not files:
        print("[content-guard] ERROR: no markdown files found", file=sys.stderr)
        return 1

    all_issues: List[str] = []
    for path in files:
        try:
            all_issues.extend(inspect_file(path))
        except Exception as exc:  # pylint: disable=broad-except
            all_issues.append(f"{path}: unexpected error ({exc})")

    if all_issues:
        print("[content-guard] FAILED")
        for issue in all_issues:
            print(f" - {issue}")
        return 1

    print(f"[content-guard] OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
