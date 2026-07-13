#!/usr/bin/env python3
"""Apply and verify the print-first Guitar/Bass presentation.

Guitar and bass applications are always visible together. The primary
HTMLBook currently trails hand-maintained Level 2/3 navigation, so a full
generate.py run is unsafe. This selective updater removes the retired
instrument selector from current generated pages without touching chapter
bodies or sidebars.

Run from web/:
  uv run --with beautifulsoup4 --with lxml _build/apply_instrument_presentation.py
  uv run --with beautifulsoup4 --with lxml _build/apply_instrument_presentation.py --check
"""

from __future__ import annotations

import argparse
import html
import re
import sys

from bs4 import BeautifulSoup

from generate import (
    CHAPTERS_DIR,
    GUITAR_BASS_PART_IDS,
    SOURCE,
    parse_all_chapters,
)


XML_DECL_RE = re.compile(r"^<\?xml[^?]*\?>", re.MULTILINE)
BODY_RE = re.compile(r"<body\b[^>]*>")
BOOTSTRAP_RE = re.compile(
    r'\s*<script id="instrument-preference-bootstrap">.*?</script>\s*',
    re.DOTALL,
)
PICKER_RE = re.compile(
    r"\n\s*<!-- instrument-picker:start -->.*?"
    r"<!-- instrument-picker:end -->\s*\n",
    re.DOTALL,
)
RETIRED_ARTIFACTS = (
    "data-instrument-picker",
    'name="preferred-instrument"',
    'id="instrument-preference-bootstrap"',
    "data-instrument-enabled",
    "instrument-ui-pending",
    "instrument-ui-ready",
    "data-active-instrument",
    "mtf.preferredInstrument",
)


def source_chapters() -> list[dict]:
    text = SOURCE.read_text(encoding="utf-8")
    text = XML_DECL_RE.sub("", text, count=1).strip()
    return parse_all_chapters(BeautifulSoup(text, "lxml"))


def scoped_chapters() -> dict[str, dict]:
    chapters = {
        chapter["id"]: chapter
        for chapter in source_chapters()
        if chapter.get("part_id") in GUITAR_BASS_PART_IDS
    }
    if len(chapters) != 30:
        raise SystemExit(
            f"Expected 30 Basic Concepts + Level 1 chapters, found {len(chapters)}"
        )
    return chapters


def replace_meta_description(text: str, title: str) -> str:
    description = html.escape(
        f"Level 1 guitar and bass theory and fretboard — {title}", quote=True
    )
    replacements = (
        (
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{description}">',
        ),
        (
            r'<meta property="og:description" content="[^"]*">',
            f'<meta property="og:description" content="{description}">',
        ),
    )
    for pattern, replacement in replacements:
        text, count = re.subn(pattern, replacement, text, count=1)
        if count != 1:
            raise ValueError(f"Could not replace metadata for {title!r}: {pattern}")
    return text


def replace_body_attributes(text: str, part_id: str) -> str:
    match = BODY_RE.search(text)
    if not match:
        raise ValueError("Missing <body> tag")

    body_tag = match.group(0)
    body_tag = re.sub(r'\sdata-part-id="[^"]*"', "", body_tag)
    body_tag = re.sub(r'\sdata-instrument-enabled="[^"]*"', "", body_tag)
    body_tag = body_tag[:-1] + f' data-part-id="{part_id}">'
    return text[: match.start()] + body_tag + text[match.end() :]


def remove_retired_toggle(text: str) -> str:
    text = BOOTSTRAP_RE.sub("\n", text, count=1)
    text = PICKER_RE.sub("\n", text, count=1)
    return re.sub(r'\sdata-instrument-enabled="[^"]*"', "", text)


def patch_page(path, chapter: dict | None) -> bool:
    original = path.read_text(encoding="utf-8")
    text = remove_retired_toggle(original)
    if chapter is not None:
        text = replace_meta_description(text, chapter["title"])
        text = replace_body_attributes(text, chapter["part_id"])

    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def validate(scoped: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    variant_count = 0

    for path in sorted(CHAPTERS_DIR.glob("*.html")):
        chapter_id = path.stem
        text = path.read_text(encoding="utf-8")

        for artifact in RETIRED_ARTIFACTS:
            if artifact in text:
                errors.append(f"{path.name}: retired toggle artifact remains: {artifact}")

        chapter = scoped.get(chapter_id)
        if chapter is not None:
            if f'data-part-id="{chapter["part_id"]}"' not in text:
                errors.append(f"{path.name}: missing or incorrect data-part-id")
            if "Level 1 guitar and bass theory and fretboard" not in text:
                errors.append(f"{path.name}: guitar-and-bass metadata missing")

        soup = BeautifulSoup(text, "lxml")
        for variant in soup.select(".instrument-variant[data-instrument]"):
            variant_count += 1
            if variant.get("data-instrument") not in {"guitar", "bass"}:
                errors.append(
                    f"{path.name}: invalid instrument label "
                    f"{variant.get('data-instrument')!r}"
                )
            if variant.has_attr("hidden"):
                errors.append(f"{path.name}: instrument application is statically hidden")

    if variant_count == 0:
        errors.append("No Guitar/Bass application blocks were found")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the print-first presentation without changing files",
    )
    args = parser.parse_args()

    scoped = scoped_chapters()
    changed = 0

    if not args.check:
        for path in sorted(CHAPTERS_DIR.glob("*.html")):
            try:
                changed += int(patch_page(path, scoped.get(path.stem)))
            except ValueError as error:
                raise SystemExit(f"{path.name}: {error}") from error
        print(f"Updated {changed} chapter shells; chapter bodies were preserved.")

    errors = validate(scoped)
    if errors:
        print(f"Print-first instrument presentation check failed ({len(errors)} errors):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(
        "Print-first instrument presentation check passed: "
        "no selector or preference code; Guitar and Bass applications remain visible."
    )


if __name__ == "__main__":
    main()
