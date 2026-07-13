#!/usr/bin/env python3
"""Publish and verify the Basic Concepts Guitar/Bass content pass.

The HTMLBook remains the content source of truth, but a full generate.py run is
unsafe while later-level navigation is hand-maintained. This script therefore
rebuilds only the eight Basic Concepts chapter bodies and preserves every
current sidebar, page shell, and later chapter body.

Run from web/:
  uv run --with beautifulsoup4 --with lxml _build/apply_basic_concepts_bass.py
  uv run --with beautifulsoup4 --with lxml _build/apply_basic_concepts_bass.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from generate import (
    CHAPTERS_DIR,
    ROOT,
    SOURCE,
    get_chapter_content_html,
    parse_all_chapters,
    rewrite_internal_links,
)


BASIC_PART_ID = "part-basic-concepts"
EXPECTED_CHAPTERS = 8
OLD_CHAPTER_5_TITLE = "Music Theory: Why are there two E strings on the guitar?"
NEW_CHAPTER_5_TITLE = "Music Theory: Why Note Names Repeat"
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
    basic = [
        chapter for chapter in chapters
        if chapter.get("part_id") == BASIC_PART_ID
    ]
    if len(basic) != EXPECTED_CHAPTERS:
        raise SystemExit(
            f"Expected {EXPECTED_CHAPTERS} Basic Concepts chapters, found {len(basic)}"
        )
    return basic, chapter_ids


def expected_body(chapter: dict, chapter_ids: set[str]) -> str:
    content = get_chapter_content_html(chapter, depth="..")
    return rewrite_internal_links(content, chapter_ids, depth="..").strip()


def body_from_page(text: str, path: Path) -> str:
    match = CHAPTER_BODY_RE.search(text)
    if not match:
        raise ValueError(f"{path.name}: could not locate chapter body")
    return match.group("body").strip()


def replace_body(text: str, body: str, path: Path) -> str:
    match = CHAPTER_BODY_RE.search(text)
    if not match:
        raise ValueError(f"{path.name}: could not locate chapter body")
    replacement = f'\n      <div class="chapter-body">\n        {body}\n      </div>\n    </article>'
    return text[: match.start()] + replacement + text[match.end() :]


def publish_title_references() -> int:
    changed = 0
    paths = [ROOT / "index.html", *sorted(CHAPTERS_DIR.glob("*.html"))]
    for path in paths:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = original.replace(OLD_CHAPTER_5_TITLE, NEW_CHAPTER_5_TITLE)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def direct_variant_sections(container: Tag) -> list[Tag]:
    return [
        child for child in container.find_all("section", recursive=False)
        if "instrument-variant" in child.get("class", [])
    ]


def validate_variant_contract(body: str, chapter_id: str) -> list[str]:
    errors: list[str] = []
    soup = BeautifulSoup(f"<main>{body}</main>", "lxml")
    containers = soup.select("div.instrument-variants")

    for index, container in enumerate(containers, start=1):
        if container.find_parent(class_="instrument-variant"):
            errors.append(f"{chapter_id}: variant container {index} is nested")
        variants = direct_variant_sections(container)
        instruments = [variant.get("data-instrument") for variant in variants]
        if instruments != ["guitar", "bass"]:
            errors.append(
                f"{chapter_id}: container {index} must contain Guitar then Bass; "
                f"found {instruments}"
            )
        for variant in variants:
            if variant.has_attr("hidden"):
                errors.append(
                    f"{chapter_id}: source variant must not have a static hidden attribute"
                )
            heading = variant.find(class_="instrument-variant__title", recursive=False)
            if heading is None:
                errors.append(
                    f"{chapter_id}: container {index} has an unlabeled variant"
                )

    invalid = [
        variant.get("data-instrument")
        for variant in soup.select(".instrument-variant[data-instrument]")
        if variant.get("data-instrument") not in {"guitar", "bass"}
    ]
    if invalid:
        errors.append(f"{chapter_id}: invalid instrument values: {invalid}")

    ids = [element["id"] for element in soup.select("[id]")]
    duplicates = sorted({element_id for element_id in ids if ids.count(element_id) > 1})
    if duplicates:
        errors.append(f"{chapter_id}: duplicate IDs in chapter body: {duplicates}")

    return errors


def validate_images(body: str, chapter_id: str) -> list[str]:
    errors: list[str] = []
    soup = BeautifulSoup(f"<main>{body}</main>", "lxml")
    for image in soup.find_all("img"):
        src = image.get("src", "")
        if src.startswith("../assets/img/"):
            asset = ROOT / src.removeprefix("../")
            if not asset.exists():
                errors.append(f"{chapter_id}: missing image {src}")
        variant = image.find_parent(class_="instrument-variant")
        if (
            not image.get("alt")
            and variant is not None
            and variant.get("data-instrument") == "bass"
        ):
            errors.append(
                f"{chapter_id}: bass-specific image lacks useful alt text: {src}"
            )
    return errors


def validate(
    basic: list[dict],
    chapter_ids: set[str],
) -> list[str]:
    errors: list[str] = []

    for chapter in basic:
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
            errors.append(f"{path.name}: generated body differs from the HTMLBook source")
        errors.extend(validate_variant_contract(actual, chapter_id))
        errors.extend(validate_images(actual, chapter_id))

    published_paths = [ROOT / "index.html", *sorted(CHAPTERS_DIR.glob("*.html"))]
    for path in published_paths:
        if path.exists() and OLD_CHAPTER_5_TITLE in path.read_text(encoding="utf-8"):
            errors.append(f"{path.name}: old Chapter 5 display title remains")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify source/output consistency without changing files",
    )
    args = parser.parse_args()

    basic, chapter_ids = source_chapters()
    changed_bodies = 0
    changed_title_files = 0

    if not args.check:
        for chapter in basic:
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
                changed_bodies += 1
        changed_title_files = publish_title_references()
        print(
            f"Updated {changed_bodies} of {EXPECTED_CHAPTERS} Basic Concepts bodies; "
            f"updated Chapter 5 labels in {changed_title_files} published files."
        )

    errors = validate(basic, chapter_ids)
    if errors:
        print(f"Basic Concepts Guitar/Bass check failed ({len(errors)} errors):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(
        "Basic Concepts Guitar/Bass check passed: "
        "8 source-synchronized chapter bodies and a consistent Chapter 5 title."
    )


if __name__ == "__main__":
    main()
