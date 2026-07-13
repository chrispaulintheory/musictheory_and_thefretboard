#!/usr/bin/env python3
"""Publish and verify the Level 1 Chapters 20–30 bass text pass.

The HTMLBook remains the content source of truth. A full generate.py run is
unsafe while later-level navigation is hand-maintained, so this script replaces
only the selected generated chapter bodies and preserves their current shells,
sidebars, and navigation.

Run from web/:
  uv run --with beautifulsoup4 --with lxml _build/apply_level1_chapters_20_30.py
  uv run --with beautifulsoup4 --with lxml _build/apply_level1_chapters_20_30.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup

import generate as generator
from generate import (
    CHAPTERS_DIR,
    ROOT,
    SOURCE,
    get_chapter_content_html,
    parse_all_chapters,
    rewrite_internal_links,
)


CHAPTER_IDS = (
    "chapter-the-fretboard-the-tritone-shape-on-the-e-a-d-g-string-set",
    "chapter-music-theory-chord-voicings",
    "chapter-the-fretboard-a-very-common-power-chord-voicing",
    "chapter-music-theory-inverting-the-perfect-intervals",
    "chapter-the-fretboard-power-chord-inversions",
    "chapter-musical-application-note-memorization-power-chords",
    "chapter-music-theory-intro-to-sharps-key-signatures-and-the-g-major-scale",
    "chapter-the-fretboard-the-g-major-scale",
    "chapter-music-theory-key-of-d-two-sharps",
    "chapter-the-fretboard-the-d-major-scale",
    "chapter-music-theory-exercises-scale-building",
)
XML_DECL_RE = re.compile(r"^<\?xml[^?]*\?>", re.MULTILINE)
CHAPTER_BODY_RE = re.compile(
    r'(?P<open>\s*<div class="chapter-body">\s*)'
    r'(?P<body>.*?)'
    r'(?P<close>\s*</div>\s*</article>)',
    re.DOTALL,
)


def source_chapters() -> tuple[list[dict], set[str]]:
    text = XML_DECL_RE.sub("", SOURCE.read_text(encoding="utf-8"), count=1).strip()
    chapters = parse_all_chapters(BeautifulSoup(text, "lxml"))
    chapter_ids = {chapter["id"] for chapter in chapters}
    by_id = {chapter["id"]: chapter for chapter in chapters}

    missing = [chapter_id for chapter_id in CHAPTER_IDS if chapter_id not in by_id]
    if missing:
        raise SystemExit(f"Missing source chapters: {', '.join(missing)}")

    return [by_id[chapter_id] for chapter_id in CHAPTER_IDS], chapter_ids


def expected_body(chapter: dict, chapter_ids: set[str]) -> str:
    content = get_chapter_content_html(chapter, depth="..")
    content = rewrite_internal_links(content, chapter_ids, depth="..").strip()
    # Keep the existing explicit combining-circumflex entities in Chapter 30
    # stable instead of churning equivalent rendered text on every publish.
    if chapter["id"] == "chapter-music-theory-exercises-scale-building":
        content = content.replace("\u0302", "&#x0302;")
    return content


def chapter_body_match(text: str, path: Path) -> re.Match[str]:
    matches = list(CHAPTER_BODY_RE.finditer(text))
    if len(matches) != 1:
        raise ValueError(
            f"{path.name}: expected exactly one chapter body, found {len(matches)}"
        )
    return matches[0]


def body_from_page(text: str, path: Path) -> str:
    match = chapter_body_match(text, path)
    return match.group("body").strip()


def replace_body(text: str, body: str, path: Path) -> str:
    match = chapter_body_match(text, path)
    return text[: match.start("body")] + body + text[match.end("body") :]


def resolve_image_read_only(src: str, depth: str = "..") -> str | None:
    """Resolve only assets that already exist; never copy or download in --check."""
    if not src or src.startswith("data:"):
        return None

    if src.startswith(("http://", "https://")):
        raw_basename = urllib.parse.unquote(src.rsplit("/", 1)[-1])
        for candidate in (raw_basename, generator.strip_resize_suffix(raw_basename)):
            normalized = generator.normalize_filename(candidate)
            if (generator.ASSETS_IMG / normalized).is_file():
                return f"{depth}/assets/img/{normalized}"
        return None

    local_file = generator.find_local_image(src)
    if local_file is None:
        return None
    normalized = generator.normalize_filename(local_file.name)
    if not (generator.ASSETS_IMG / normalized).is_file():
        return None
    return f"{depth}/assets/img/{normalized}"


def validate_images(body: str, chapter_id: str) -> list[str]:
    errors: list[str] = []
    soup = BeautifulSoup(f"<main>{body}</main>", "lxml")
    for image in soup.find_all("img"):
        src = image.get("src", "")
        if image.get("data-missing") == "true":
            errors.append(f"{chapter_id}: unresolved image {src or '[empty src]'}")
        elif not src:
            errors.append(f"{chapter_id}: image has an empty src")
        elif not src.startswith("../assets/img/"):
            errors.append(f"{chapter_id}: image is not localized: {src}")
        else:
            asset = ROOT / src.removeprefix("../")
            if not asset.is_file():
                errors.append(f"{chapter_id}: missing image {src}")
    return errors


def validate(chapters: list[dict], chapter_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for chapter in chapters:
        chapter_id = chapter["id"]
        path = CHAPTERS_DIR / f"{chapter_id}.html"
        if not path.exists():
            errors.append(f"Missing generated chapter: {path.name}")
            continue

        text = path.read_text(encoding="utf-8")
        try:
            actual = body_from_page(text, path)
        except ValueError as error:
            errors.append(str(error))
            continue

        expected = expected_body(chapter, chapter_ids)
        if actual != expected:
            errors.append(f"{path.name}: generated body differs from HTMLBook source")
        errors.extend(validate_images(actual, chapter_id))

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify source/output consistency without changing files",
    )
    args = parser.parse_args()

    chapters, chapter_ids = source_chapters()
    changed = 0

    if args.check:
        # The shared generator normally copies or downloads missing images.
        # A check must be read-only, so resolve only already-localized assets.
        generator.resolve_image = resolve_image_read_only

    if not args.check:
        for chapter in chapters:
            path = CHAPTERS_DIR / f'{chapter["id"]}.html'
            if not path.exists():
                raise SystemExit(f"Missing generated chapter: {path}")
            original = path.read_text(encoding="utf-8")
            updated = replace_body(
                original,
                expected_body(chapter, chapter_ids),
                path,
            )
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                changed += 1
        print(f"Updated {changed} of {len(CHAPTER_IDS)} Level 1 chapter bodies.")

    errors = validate(chapters, chapter_ids)
    if errors:
        print(f"Level 1 Chapters 20–30 check failed ({len(errors)} errors):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(
        "Level 1 Chapters 20–30 check passed: "
        "11 source-synchronized chapter bodies with valid local images."
    )


if __name__ == "__main__":
    main()
