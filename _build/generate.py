#!/usr/bin/env python3
"""
Music Theory and The Fretboard — static site generator.
Splits the source HTMLBook into a polished multi-page static website.

Run: uv run --with beautifulsoup4 --with lxml _build/generate.py
"""

import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

try:
    from bs4 import BeautifulSoup, Comment, NavigableString, Tag
except ImportError:
    print("Error: beautifulsoup4 not installed.")
    print("Run: uv run --with beautifulsoup4 --with lxml _build/generate.py")
    sys.exit(1)

# ─── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent
SOURCE = ROOT / "Music-Theory-and-The-Fretboard-Level-1-1709264790.-htmlbook.html"
ASSETS_IMG = ROOT / "assets" / "img"
CHAPTERS_DIR = ROOT / "chapters"

# ─── Chapter type detection ───────────────────────────────────────────────────

def chapter_type(title: str) -> str:
    """Return 'theory', 'fretboard', 'both', or 'misc'."""
    t = title.lower()
    has_theory = "music theory" in t
    has_fretboard = "fretboard" in t
    if has_theory and has_fretboard:
        return "both"
    if has_theory or "musical application" in t or "exercises" in t:
        return "theory"
    if has_fretboard:
        return "fretboard"
    return "misc"


# ─── Image resolution ─────────────────────────────────────────────────────────

RESIZE_SUFFIX_RE = re.compile(r"-\d+x\d+(-\d+)?(?=\.[a-zA-Z]+$)")
# Narrow no-break space U+202F
NNBSP = " "


def normalize_filename(name: str) -> str:
    """Replace spaces and narrow no-break spaces with underscores."""
    return re.sub(r"[\s" + NNBSP + r"]+", "_", name)


def strip_resize_suffix(filename: str) -> str:
    """Strip WordPress-style resize suffix like -1024x249 from filename."""
    return RESIZE_SUFFIX_RE.sub("", filename)


def find_local_image(src: str) -> Optional[Path]:
    """Try to find a local file for the given src basename."""
    # Try: exact, strip-resize, with NNBSP→space, strip-resize+NNBSP→space
    candidates = [src]
    stripped = strip_resize_suffix(src)
    if stripped != src:
        candidates.append(stripped)
    # Also try replacing NNBSP with regular space (or vice versa)
    for c in list(candidates):
        if NNBSP in c:
            candidates.append(c.replace(NNBSP, " "))
        if " " in c:
            candidates.append(c.replace(" ", NNBSP))

    for name in candidates:
        p = ROOT / name
        if p.exists():
            return p
    return None


_download_cache: dict[str, Optional[str]] = {}


def resolve_image(src: str, depth: str = "..") -> Optional[str]:
    """
    Resolve an img src to a local assets/img/ path.
    Returns relative path from chapter dir, e.g. '../assets/img/foo.png'.
    Downloads remote images. Returns None if unresolvable.
    """
    if not src or src.startswith("data:"):
        return None

    cache_key = src
    if cache_key in _download_cache:
        cached = _download_cache[cache_key]
        if cached is None:
            return None
        return f"{depth}/assets/img/{cached}"

    if src.startswith("http://") or src.startswith("https://"):
        # Remote image — extract basename, strip resize suffix
        raw_basename = urllib.parse.unquote(src.split("/")[-1])

        # Prefer a local copy if one exists (e.g. images extracted from the
        # print PDF). Check the exact basename first, then the resize-stripped
        # name. On-disk files may use spaces, narrow no-break spaces, or
        # underscores interchangeably, so try every spelling.
        for cand in (raw_basename, strip_resize_suffix(raw_basename)):
            norm = normalize_filename(cand)  # web-facing name (underscores)
            name_variants = {cand, norm, cand.replace(" ", NNBSP), cand.replace(NNBSP, " ")}
            # Already-copied web asset?
            if (ASSETS_IMG / norm).exists():
                _download_cache[cache_key] = norm
                return f"{depth}/assets/img/{norm}"
            # Source file present under any spelling (in assets/img or ROOT)?
            found = None
            for variant in name_variants:
                for base in (ASSETS_IMG, ROOT):
                    p = base / variant
                    if p.exists():
                        found = p
                        break
                if found:
                    break
            if found is None:
                found = find_local_image(cand)
            if found is not None:
                dest = ASSETS_IMG / norm
                if not dest.exists():
                    ASSETS_IMG.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(found, dest)
                _download_cache[cache_key] = norm
                return f"{depth}/assets/img/{norm}"

        local_name = normalize_filename(strip_resize_suffix(raw_basename))
        dest = ASSETS_IMG / local_name
        if not dest.exists():
            # Try full-size URL (without resize suffix) first, then exact
            full_size_raw = RESIZE_SUFFIX_RE.sub("", raw_basename)
            base_url = src.rsplit("/", 1)[0]

            def encode_url(base: str, fname: str) -> str:
                """URL-encode a filename (handles non-ASCII like U+202F)."""
                encoded = urllib.parse.quote(fname, safe=".-_")
                return f"{base}/{encoded}"

            candidates = []
            if full_size_raw != raw_basename:
                candidates.append(encode_url(base_url, full_size_raw))
            candidates.append(encode_url(base_url, raw_basename))

            downloaded = False
            for url in candidates:
                try:
                    req = urllib.request.Request(
                        url,
                        headers={"User-Agent": "Mozilla/5.0 (compatible; static-site-builder/1.0)"},
                    )
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        if resp.status == 200:
                            ASSETS_IMG.mkdir(parents=True, exist_ok=True)
                            dest.write_bytes(resp.read())
                            downloaded = True
                            break
                except (urllib.error.URLError, urllib.error.HTTPError, OSError):
                    pass
            if not downloaded:
                print(f"  WARN: Could not download {src[:80]!r}")
                _download_cache[cache_key] = None
                return None
        _download_cache[cache_key] = local_name
        return f"{depth}/assets/img/{local_name}"

    else:
        # Local image
        local_file = find_local_image(src)
        if local_file is None:
            print(f"  WARN: Could not find local image: {src!r}")
            _download_cache[cache_key] = None
            return None
        local_name = normalize_filename(local_file.name)
        dest = ASSETS_IMG / local_name
        if not dest.exists():
            ASSETS_IMG.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_file, dest)
        _download_cache[cache_key] = local_name
        return f"{depth}/assets/img/{local_name}"


# ─── HTML content processing ──────────────────────────────────────────────────

def process_content_html(tag: Tag, depth: str = "..") -> str:
    """
    Process a chapter section's content:
    - Rewrite img src/srcset to local assets
    - Demote h1 subheads to h2/h3
    - Mark student assignment sections
    - Remove Pressbooks interactive embeds
    - Fix misc cruft
    """
    # Work on a copy
    from copy import deepcopy
    tag = deepcopy(tag)

    # Remove HTML comments
    for c in tag.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    # Remove interactive/oembed embed boxes
    for div in tag.find_all("div", class_=lambda c: c and "interactive-content" in " ".join(c)):
        div.extract()

    # Fix img tags
    for img in tag.find_all("img"):
        src = img.get("src", "")
        if not src:
            img.extract()
            continue
        resolved = resolve_image(src, depth)
        if resolved:
            img["src"] = resolved
            # Replace complex srcset with just the single resolved image
            if img.get("srcset"):
                img["srcset"] = resolved
            # Keep width/height if present (prevents layout shift)
            img["loading"] = "lazy"
            # Remove sizes attr (not needed for single-image srcset)
            if "sizes" in img.attrs:
                del img.attrs["sizes"]
            # Clear alignment classes — CSS handles this
            if img.get("class"):
                classes = [c for c in img.get("class", []) if c not in (
                    "aligncenter", "alignnone", "alignleft", "alignright",
                    "size-full", "size-medium",
                )]
                if classes:
                    img["class"] = classes
                else:
                    del img["class"]
        else:
            # Keep broken img but flag it
            img["data-missing"] = "true"
            if img.get("srcset"):
                del img["srcset"]

    # Wrap lone img inside figure if not already wrapped
    for img in tag.find_all("img"):
        parent = img.parent
        if parent and parent.name not in ("figure", "td", "th", "a"):
            # Check if it's inside a p with only the img (and whitespace)
            if parent.name == "p":
                siblings = [c for c in parent.children if not (isinstance(c, NavigableString) and not c.strip())]
                if len(siblings) == 1:
                    # Wrap the p in a figure
                    figure = BeautifulSoup("<figure></figure>", "lxml").figure
                    parent.replace_with(figure)
                    figure.append(img)

    # Semantic heading cleanup:
    # Any h1 inside chapter content (not the chapter-title in header) → h2
    # h1 with text-align style → h2 class="centered-subhead" / "subhead"
    # Detect student assignment h1 → add class for callout styling
    for h1 in tag.find_all("h1"):
        # Skip the chapter header h1 (it's in the header element, but we stripped header)
        style = h1.get("style", "")
        text = h1.get_text(strip=True)
        new_tag_name = "h2"
        new_classes = []

        if "text-align: center" in style or "text-align:center" in style:
            new_classes.append("centered-subhead")

        # Student assignment heading detection
        lower_text = text.lower()
        if "student assignment" in lower_text or "student quiz" in lower_text:
            new_classes.append("assignment-heading")

        h1.name = new_tag_name
        if "style" in h1.attrs:
            del h1.attrs["style"]
        if new_classes:
            existing = h1.get("class", [])
            h1["class"] = existing + new_classes

    # h3/h4 with text-align style → add class
    for h in tag.find_all(["h3", "h4"]):
        style = h.get("style", "")
        if "text-align: center" in style or "text-align:center" in style:
            existing = h.get("class", [])
            h["class"] = existing + ["centered-subhead"]
            del h.attrs["style"]
        elif "style" in h.attrs and h.attrs["style"] == "text-align: center":
            del h.attrs["style"]

    # Mark page-break-before divs (used for student assignments) as assignment-box
    for div in tag.find_all("div", class_="page-break-before"):
        div["class"] = ["assignment-box"]

    # Remove empty paragraphs and &nbsp; only paragraphs
    for p in tag.find_all("p"):
        text = p.get_text()
        if not text.strip() or text.strip() == "\xa0":
            p.extract()

    # Strip inline color/font-size/font-weight styles from p tags,
    # but preserve text-align and some structural ones
    for p in tag.find_all("p"):
        style = p.get("style", "")
        if style:
            # Keep only text-align
            parts = [s.strip() for s in style.split(";") if s.strip()]
            kept = [s for s in parts if s.startswith("text-align")]
            if kept:
                p["style"] = "; ".join(kept)
            else:
                del p.attrs["style"]

    # Also handle spans with only font styling
    for span in tag.find_all("span"):
        style = span.get("style", "")
        if style and not span.get("class"):
            # Remove font-size/font-weight spans by unwrapping
            if "font-size" in style and "color" not in style and "background" not in style:
                span.unwrap()

    # Remove empty h4 tags
    for h in tag.find_all(["h4"]):
        if not h.get_text(strip=True):
            h.extract()

    # Fix table styles — strip inline widths etc for responsive CSS
    for table in tag.find_all("table"):
        if "style" in table.attrs:
            del table.attrs["style"]
    for td in tag.find_all(["td", "tr"]):
        if "style" in td.attrs:
            # Keep only text-align
            style = td.attrs["style"]
            parts = [s.strip() for s in style.split(";") if s.strip()]
            kept = [s for s in parts if s.startswith("text-align")]
            if kept:
                td["style"] = "; ".join(kept)
            else:
                del td.attrs["style"]

    # Return just the inner HTML (not the outer tag itself)
    return tag.decode_contents()


# ─── Sidebar HTML ─────────────────────────────────────────────────────────────

def generate_sidebar(all_chapters: list[dict], active_id: str = "", depth: str = "..") -> str:
    """Generate the persistent sidebar navigation HTML."""

    html = []
    html.append('<nav class="sidebar" id="sidebar" aria-label="Table of contents">')
    html.append(f'  <div class="sidebar-header">')
    html.append(f'    <a href="{depth}/index.html" class="sidebar-logo">')
    html.append(f'      <span class="sidebar-logo-title">Music Theory</span>')
    html.append(f'      <span class="sidebar-logo-amp">&amp;</span>')
    html.append(f'      <span class="sidebar-logo-sub">The Fretboard</span>')
    html.append(f'    </a>')
    html.append(f'  </div>')
    html.append(f'  <div class="sidebar-scroll">')

    # Group chapters by part, preserving reading order
    parts: list[tuple[str, dict, list[dict]]] = []
    for ch in all_chapters:
        if not parts or parts[-1][0] != ch["part_id"]:
            parts.append((ch["part_id"], ch.get("part_info", {}), [ch]))
        else:
            parts[-1][2].append(ch)

    for part_id, part_info, chs in parts:
        part_title = part_info.get("short", "")
        part_num = part_info.get("number", "")
        part_class = part_info.get("color_class", "")
        num_html = f'<span class="part-num">{part_num}</span>' if part_num else ""

        # Single-page part (e.g. Introduction) → direct link, no collapsible group
        if len(chs) == 1:
            ch = chs[0]
            slug = f"{depth}/chapters/{ch['id']}.html"
            active_class = " active" if ch["id"] == active_id else ""
            html.append(f'  <div class="sidebar-part sidebar-part-flat {part_class}{active_class}">')
            html.append(f'    <a class="sidebar-part-title sidebar-part-link" href="{slug}">')
            if num_html:
                html.append(f'      {num_html}')
            html.append(f'      {part_title}')
            html.append(f'    </a>')
            html.append(f'  </div>')
            continue

        is_open = any(c["id"] == active_id for c in chs)
        open_attr = " open" if is_open else ""
        html.append(f'  <details class="sidebar-part {part_class}"{open_attr}>')
        html.append(f'    <summary class="sidebar-part-title">')
        if num_html:
            html.append(f'      {num_html}')
        html.append(f'      {part_title}')
        html.append(f'    </summary>')
        html.append(f'    <ol class="sidebar-chapters">')
        for ch in chs:
            slug = f"{depth}/chapters/{ch['id']}.html"
            active_class = " active" if ch["id"] == active_id else ""
            type_class = f" ch-{ch.get('type', 'misc')}"
            ch_num = f'<span class="ch-num">{ch["number"]}</span>' if ch.get("number") else ""
            html.append(f'      <li class="sidebar-chapter{active_class}{type_class}">')
            html.append(f'        <a href="{slug}">{ch_num}{ch["title"]}</a>')
            html.append(f'      </li>')
        html.append("    </ol>")
        html.append("  </details>")

    html.append("  </div>")  # sidebar-scroll
    html.append("</nav>")
    return "\n".join(html)


# ─── Page templates ───────────────────────────────────────────────────────────

GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&"
    "family=Newsreader:ital,opsz,wght@0,6..72,300..800;1,6..72,300..800&"
    "display=swap"
)


def page_head(title: str, description: str, depth: str = "..") -> str:
    """Generate the <head> block for a page."""
    return f"""  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="article">
  <link rel="icon" href="{depth}/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{GOOGLE_FONTS}" rel="stylesheet">
  <link rel="stylesheet" href="{depth}/css/styles.css">"""


def generate_chapter_page(
    chapter: dict,
    content_html: str,
    sidebar_html: str,
    prev_ch: Optional[dict],
    next_ch: Optional[dict],
    depth: str = "..",
) -> str:
    """Render a full chapter page."""
    ch_id = chapter["id"]
    title = chapter["title"]
    ch_type = chapter.get("type", "misc")
    part_title = chapter.get("part_info", {}).get("short", "")
    ch_num = chapter.get("number", "")
    num_label = f"Chapter {ch_num}" if ch_num else ""

    full_title = f"{title} — Music Theory and The Fretboard (Level 1)"
    desc = f"Level 1 guitar theory and fretboard — {title}"

    prev_link = ""
    if prev_ch:
        prev_label = prev_ch["title"]
        prev_slug = f"{depth}/chapters/{prev_ch['id']}.html"
        prev_link = f"""<a href="{prev_slug}" class="prev-next-link prev-link">
        <span class="pn-label">← Previous</span>
        <span class="pn-title">{prev_label}</span>
      </a>"""

    next_link = ""
    if next_ch:
        next_label = next_ch["title"]
        next_slug = f"{depth}/chapters/{next_ch['id']}.html"
        next_link = f"""<a href="{next_slug}" class="prev-next-link next-link">
        <span class="pn-label">Next →</span>
        <span class="pn-title">{next_label}</span>
      </a>"""

    breadcrumb = ""
    if part_title:
        breadcrumb = f"""<nav class="breadcrumb" aria-label="breadcrumb">
      <a href="{depth}/index.html">Home</a>
      <span class="bc-sep">›</span>
      <span>{part_title}</span>
      <span class="bc-sep">›</span>
      <span>{title}</span>
    </nav>"""

    chapter_label = ""
    if num_label:
        chapter_label = f'<p class="chapter-number-label">{num_label}</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{page_head(full_title, desc, depth)}
</head>
<body class="chapter-page theme-{ch_type}" data-chapter-id="{ch_id}">
  <button class="drawer-toggle" id="drawer-toggle" aria-label="Open navigation" aria-expanded="false" aria-controls="sidebar">
    <span class="hamburger"></span>
  </button>
  <div class="sidebar-overlay" id="sidebar-overlay"></div>
{sidebar_html}
  <main class="content" id="main-content">
    {breadcrumb}
    <article class="chapter-article" id="{ch_id}">
      <header class="chapter-header">
        {chapter_label}
        <h1 class="chapter-title">{title}</h1>
      </header>
      <div class="chapter-body">
        {content_html}
      </div>
    </article>
    <nav class="prev-next" aria-label="Chapter navigation">
      {prev_link}
      {next_link}
    </nav>
  </main>
  <button class="back-to-top" id="back-to-top" aria-label="Back to top">↑</button>
  <div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Image lightbox" hidden>
    <button class="lightbox-close" id="lightbox-close" aria-label="Close lightbox">×</button>
    <img class="lightbox-img" id="lightbox-img" src="" alt="">
  </div>
  <script src="{depth}/js/site.js"></script>
</body>
</html>"""


def generate_index_page(all_chapters: list[dict], soup: BeautifulSoup) -> str:
    """Generate the home page index.html."""

    # Extract the author note from the introduction
    intro = soup.find(id="front-matter-introduction")
    author_note_html = ""
    if intro:
        # Get the first few paragraphs
        paras = intro.find_all("p", limit=6)
        note_parts = []
        for p in paras:
            text = p.get_text(strip=True)
            if text and len(text) > 30:
                note_parts.append(str(p))
            if len(note_parts) >= 3:
                break
        author_note_html = "\n".join(note_parts)

    # Build part cards
    parts_config = [
        {
            "id": "part-basic-concepts",
            "number": "I",
            "title": "Basic Concepts",
            "color_class": "part-i",
            "desc": "Pitch, tablature, notes, string names, the fret markers — the essential vocabulary.",
        },
        {
            "id": "part-main-body",
            "number": "II",
            "title": "Level 1",
            "color_class": "part-ii",
            "desc": "The Major Scale, intervals, power chords, key signatures, the bass strings — the core curriculum.",
        },
        {
            "id": "part-bonus-introduction-to-standard-notation-sheet-music",
            "number": "III",
            "title": "Bonus: Standard Notation",
            "color_class": "part-iii",
            "desc": "How to read sheet music — notes on each string of the guitar.",
        },
        {
            "id": "part-bonus-introduction-to-ear-training",
            "number": "IV",
            "title": "Bonus: Ear Training",
            "color_class": "part-iv",
            "desc": "Do–Re–Mi–Fa–Sol–La–Ti: solfège fundamentals for your inner ear.",
        },
        {
            "id": "part-level-2-preview",
            "number": "V",
            "title": "Bonus: Level 2 Preview",
            "color_class": "part-v",
            "desc": "A taste of what's next: major/minor intervals, triads, and the CAGED system.",
            "is_preview": True,
        },
    ]

    cards_html = []
    for part in parts_config:
        # Find chapters in this part
        part_chapters = [c for c in all_chapters if c["part_id"] == part["id"]]
        is_preview = part.get("is_preview", False)
        preview_badge = '<span class="preview-badge">ebook exclusive</span>' if is_preview else ""
        chapter_list = ""
        if part_chapters:
            items = []
            for c in part_chapters[:6]:  # Show first 6 on the card
                items.append(f'<li><a href="chapters/{c["id"]}.html">{c["title"]}</a></li>')
            if len(part_chapters) > 6:
                items.append(f'<li class="more-chapters">…and {len(part_chapters) - 6} more chapters</li>')
            chapter_list = f'<ul class="part-chapter-list">\n{"".join(items)}\n</ul>'
        first_ch = part_chapters[0] if part_chapters else None
        start_link = f'href="chapters/{first_ch["id"]}.html"' if first_ch else 'href="#"'
        cards_html.append(f"""
    <div class="part-card {part['color_class']}">
      <div class="part-card-header">
        <span class="part-card-num">{part['number']}</span>
        <h2 class="part-card-title">{part['title']}</h2>
        {preview_badge}
      </div>
      <p class="part-card-desc">{part['desc']}</p>
      {chapter_list}
      <a class="part-card-cta" {start_link}>Start reading →</a>
    </div>""")

    cards_markup = "\n".join(cards_html)

    # First numbered chapter for the hero CTA
    first_numbered = next((c for c in all_chapters if c.get("number")), None)
    first_chapter = all_chapters[0] if all_chapters else None
    hero_cta = (
        f'<a href="chapters/{first_numbered["id"]}.html" class="hero-cta">Start Reading — Chapter 1</a>'
        if first_numbered
        else (
            f'<a href="chapters/{first_chapter["id"]}.html" class="hero-cta">Begin Reading</a>'
            if first_chapter
            else ""
        )
    )

    full_title = "Music Theory and The Fretboard (Level 1)"
    desc_meta = "Bridge music theory concepts directly to their fretboard shapes. A clear, strategic learning roadmap for absolute-beginner guitarists."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{page_head(full_title, desc_meta, ".")}
  <link rel="stylesheet" href="css/home.css">
</head>
<body class="home-page">
  <header class="hero">
    <div class="hero-inner">
      <p class="hero-level">Level 1</p>
      <h1 class="hero-title">
        <span class="hero-title-main">Music Theory</span>
        <span class="hero-title-amp">&amp;</span>
        <span class="hero-title-sub">The Fretboard</span>
      </h1>
      <p class="hero-tagline">Bridge theory concepts directly to their fretboard shapes.</p>
      <p class="hero-authors">by Denisse Vallecillos and Chris Paul</p>
      {hero_cta}
    </div>
    <div class="hero-fretboard" aria-hidden="true">
      <div class="fret-strings">
        {"".join(f'<div class="fret-string s{i}"></div>' for i in range(1,7))}
      </div>
      <div class="fret-markers">
        {"".join(f'<div class="fret-dot"></div>' for _ in range(8))}
      </div>
    </div>
  </header>

  <main class="home-main">
    <section class="toc-section" aria-label="Table of contents">
      <h2 class="section-heading">Contents</h2>
      <div class="parts-grid">
        {cards_markup}
      </div>
    </section>

    <section class="author-section" aria-label="About the authors">
      <h2 class="section-heading">About This Book</h2>
      <div class="author-note">
        {author_note_html if author_note_html else "<p>A comprehensive, beginner-friendly guitar theory book by Denisse Vallecillos and Chris Paul.</p>"}
      </div>
      <div class="about-grid">
        <div class="about-card">
          <h3>Denisse Vallecillos</h3>
          <p>Music educator with a B.S. in Music Education and M.S. in Orchestral Conducting. Former high school guitar teacher, professional violinist.</p>
        </div>
        <div class="about-card">
          <h3>Chris Paul</h3>
          <p>Co-author with a Professional Guitar Skills Certificate from Berklee Online. Author of <em>Guitar Fretboard Mastery</em>.</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <p>© 2023 Denisse Vallecillos and Chris Paul. All Rights Reserved.</p>
    <p class="footer-isbn">ISBN: 9798391152729</p>
  </footer>
  <script src="js/site.js"></script>
</body>
</html>"""


# ─── Source parsing ───────────────────────────────────────────────────────────

PART_META = {
    "part-basic-concepts": {
        "id": "part-basic-concepts",
        "title": "Part I — Basic Concepts",
        "short": "Basic Concepts",
        "number": "I",
        "color_class": "part-i",
    },
    "part-main-body": {
        "id": "part-main-body",
        "title": "Part II — Level 1",
        "short": "Level 1",
        "number": "II",
        "color_class": "part-ii",
    },
    "part-bonus-introduction-to-standard-notation-sheet-music": {
        "id": "part-bonus-introduction-to-standard-notation-sheet-music",
        "title": "BONUS — Standard Notation",
        "short": "Standard Notation",
        "number": "III",
        "color_class": "part-iii",
    },
    "part-bonus-introduction-to-ear-training": {
        "id": "part-bonus-introduction-to-ear-training",
        "title": "BONUS — Ear Training",
        "short": "Ear Training",
        "number": "IV",
        "color_class": "part-iv",
    },
    "part-level-2-preview": {
        "id": "part-level-2-preview",
        "title": "BONUS — Level 2 Preview",
        "short": "Level 2 Preview",
        "number": "V",
        "color_class": "part-v",
    },
    "front-matter": {
        "id": "front-matter",
        "title": "Introduction",
        "short": "Introduction",
        "number": "",
        "color_class": "front-matter",
    },
    "back-matter": {
        "id": "back-matter",
        "title": "Back Matter",
        "short": "Appendix",
        "number": "",
        "color_class": "back-matter",
    },
}


def parse_all_chapters(soup: BeautifulSoup) -> list[dict]:
    """Extract all chapters (including front/back matter) in reading order."""
    chapters = []
    ch_counter = 0

    def get_chapter_title(section: Tag) -> str:
        header = section.find("header")
        if header:
            h1 = header.find("h1")
            if h1:
                return h1.get_text(strip=True)
        # Fallback to title attribute
        return section.get("title", section.get("id", "Unknown"))

    def get_chapter_number(section: Tag) -> str:
        header = section.find("header")
        if header:
            num_el = header.find(attrs={"data-type": "subtitle"})
            if num_el:
                return num_el.get_text(strip=True)
        return ""

    # Front matter sections (outside parts)
    for section in soup.find_all(["section"], recursive=False):
        if section.get("data-type") in ("introduction", "preface", "foreword"):
            sec_id = section.get("id", "")
            if not sec_id:
                continue
            title = get_chapter_title(section)
            chapters.append({
                "id": sec_id,
                "title": title,
                "number": "",
                "part_id": "front-matter",
                "part_info": PART_META["front-matter"],
                "type": "misc",
                "section": section,
            })

    # Actually, the body has sections directly
    body = soup.find("body")
    if not body:
        body = soup

    # Process in order: front matter → parts (with chapters) → back matter
    for child in body.children:
        if not isinstance(child, Tag):
            continue

        # Front matter (direct children with data-type=introduction)
        if child.get("data-type") in ("introduction", "preface", "foreword"):
            sec_id = child.get("id", "")
            if not sec_id:
                continue
            title = get_chapter_title(child)
            chapters.append({
                "id": sec_id,
                "title": title,
                "number": "",
                "part_id": "front-matter",
                "part_info": PART_META["front-matter"],
                "type": "misc",
                "section": child,
            })

        # Parts (div[data-type="part"])
        elif child.get("data-type") == "part":
            part_id = child.get("id", "")
            part_info = PART_META.get(part_id, {
                "id": part_id,
                "title": part_id,
                "short": part_id,
                "number": "",
                "color_class": "part-misc",
            })
            for section in child.find_all("section", recursive=False):
                if section.get("data-type") == "chapter":
                    sec_id = section.get("id", "")
                    if not sec_id:
                        continue
                    ch_counter += 1
                    title = get_chapter_title(section)
                    ch_num = get_chapter_number(section) or str(ch_counter)
                    chapters.append({
                        "id": sec_id,
                        "title": title,
                        "number": ch_num,
                        "part_id": part_id,
                        "part_info": part_info,
                        "type": chapter_type(title),
                        "section": section,
                    })

        # Back matter (direct children with data-type=appendix/colophon/afterword)
        elif child.get("data-type") in ("appendix", "colophon", "afterword", "glossary"):
            sec_id = child.get("id", "")
            if not sec_id:
                continue
            title = get_chapter_title(child)
            chapters.append({
                "id": sec_id,
                "title": title,
                "number": "",
                "part_id": "back-matter",
                "part_info": PART_META["back-matter"],
                "type": "misc",
                "section": child,
            })

    return chapters


def get_chapter_content_html(chapter: dict, depth: str = "..") -> str:
    """Extract and clean the body HTML for a chapter (excludes header)."""
    section = chapter["section"]
    # Find the content: everything inside the section except the header
    header = section.find("header")

    # Collect all content after the header
    content_parts = []
    for child in section.children:
        if isinstance(child, Tag) and child.name == "header":
            continue  # skip the header (we handle it separately in the template)
        content_parts.append(str(child))

    # Build a temporary soup from the content
    content_html = "".join(content_parts)
    temp_soup = BeautifulSoup(f"<div>{content_html}</div>", "lxml")
    wrapper = temp_soup.find("div")
    if wrapper:
        return process_content_html(wrapper, depth)
    return content_html


# ─── Internal link rewriting ──────────────────────────────────────────────────

def rewrite_internal_links(html: str, chapter_ids: set[str], depth: str = "..") -> str:
    """Rewrite #anchor links that point to chapter IDs → chapter page URLs."""
    def replace_link(m: re.Match) -> str:
        anchor = m.group(1)
        if anchor in chapter_ids:
            return f'href="{depth}/chapters/{anchor}.html"'
        return m.group(0)

    return re.sub(r'href="#([^"]+)"', replace_link, html)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("▶ Music Theory and The Fretboard — static site generator")
    print(f"  Source: {SOURCE}")

    if not SOURCE.exists():
        print(f"Error: Source file not found: {SOURCE}")
        sys.exit(1)

    # Ensure output dirs exist
    ASSETS_IMG.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    # Parse source
    print("\n── Phase 0: Parsing source…")
    text = SOURCE.read_text(encoding="utf-8")
    # Strip XML declaration so lxml parses it as HTML
    text = re.sub(r"^<\?xml[^?]*\?>", "", text, count=1).strip()
    soup = BeautifulSoup(text, "lxml")

    # Extract chapter structure
    print("── Phase 1: Extracting structure…")
    all_chapters = parse_all_chapters(soup)
    chapter_ids = {c["id"] for c in all_chapters}
    print(f"  Found {len(all_chapters)} sections (chapters + front/back matter)")

    # Generate all chapter pages
    print("\n── Phase 2: Generating chapter pages…")
    sidebar_html_cache: dict[str, str] = {}  # per active_id
    depth = ".."

    for i, chapter in enumerate(all_chapters):
        ch_id = chapter["id"]
        prev_ch = all_chapters[i - 1] if i > 0 else None
        next_ch = all_chapters[i + 1] if i < len(all_chapters) - 1 else None

        print(f"  [{i+1:2d}/{len(all_chapters)}] {ch_id}")

        # Get sidebar (cached per active id is wasteful; generate once per page)
        sidebar = generate_sidebar(all_chapters, active_id=ch_id, depth=depth)

        # Get content
        content_html = get_chapter_content_html(chapter, depth=depth)

        # Rewrite internal links
        content_html = rewrite_internal_links(content_html, chapter_ids, depth)

        # Generate page
        page_html = generate_chapter_page(
            chapter=chapter,
            content_html=content_html,
            sidebar_html=sidebar,
            prev_ch=prev_ch,
            next_ch=next_ch,
            depth=depth,
        )

        out_path = CHAPTERS_DIR / f"{ch_id}.html"
        out_path.write_text(page_html, encoding="utf-8")

    # Generate index
    print("\n── Phase 3: Generating index.html…")
    index_html = generate_index_page(all_chapters, soup)
    # Fix internal links in index (depth=".")
    index_html = rewrite_internal_links(index_html, chapter_ids, depth=".")
    (ROOT / "index.html").write_text(index_html, encoding="utf-8")

    print("\n── Summary ──────────────────────────────────────────────")
    print(f"  ✓ {len(all_chapters)} chapter pages → web/chapters/")
    print(f"  ✓ index.html → web/")

    # Image report
    missing = [src for src, path in _download_cache.items() if path is None]
    if missing:
        print(f"\n  ⚠ {len(missing)} images could not be resolved:")
        for src in missing[:20]:
            print(f"    - {src[:80]}")
        if len(missing) > 20:
            print(f"    … and {len(missing) - 20} more")
    else:
        print(f"  ✓ All images resolved")

    img_count = sum(1 for p in _download_cache.values() if p is not None)
    print(f"  ✓ {img_count} images → web/assets/img/")
    print("\n✅ Done. Open web/index.html to view the site.")


if __name__ == "__main__":
    main()
