#!/usr/bin/env python3
"""
QA check: verify all internal links and local image references in generated site.
Run: uv run --with beautifulsoup4 --with lxml _build/qa_check.py
"""

import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Run: uv run --with beautifulsoup4 --with lxml _build/qa_check.py")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
errors = []
warnings = []


def check_file(html_path: Path, base_dir: Path) -> None:
    text = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "lxml")

    # Check internal links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http") or href.startswith("#") or href.startswith("mailto:"):
            continue
        target = (html_path.parent / href).resolve()
        if not target.exists():
            errors.append(f"BROKEN LINK in {html_path.name}: {href}")

    # Check image srcs
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("http") or src.startswith("data:"):
            continue
        target = (html_path.parent / src).resolve()
        if not target.exists():
            if img.get("data-missing"):
                warnings.append(f"MISSING IMG (flagged) in {html_path.name}: {src}")
            else:
                errors.append(f"BROKEN IMG in {html_path.name}: {src}")


def main() -> None:
    print("── QA Check ───────────────────────────────────────────")

    pages = list(ROOT.glob("*.html")) + list((ROOT / "chapters").glob("*.html"))
    print(f"  Checking {len(pages)} HTML pages…\n")

    for p in sorted(pages):
        check_file(p, ROOT)

    if errors:
        print(f"❌ {len(errors)} errors:")
        for e in errors:
            print(f"   {e}")
    else:
        print("✅ No broken links or images.")

    if warnings:
        print(f"\n⚠  {len(warnings)} warnings (unfetchable remote images):")
        for w in warnings[:20]:
            print(f"   {w}")
        if len(warnings) > 20:
            print(f"   … and {len(warnings) - 20} more")

    print(f"\n── Stats ───────────────────────────────────────────────")
    total_imgs = sum(
        len(BeautifulSoup(p.read_text(encoding="utf-8"), "lxml").find_all("img"))
        for p in pages
    )
    img_count = len(list((ROOT / "assets" / "img").glob("*")))
    ch_count = len(list((ROOT / "chapters").glob("*.html")))
    print(f"  Pages:        {len(pages)}")
    print(f"  Chapter pages: {ch_count}")
    print(f"  Total <img> tags: {total_imgs}")
    print(f"  Images in assets/img/: {img_count}")
    print(f"  CSS files: {len(list((ROOT / 'css').glob('*.css')))}")


if __name__ == "__main__":
    main()
