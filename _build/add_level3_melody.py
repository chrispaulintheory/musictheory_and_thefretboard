#!/usr/bin/env python3
"""Add the Level 3 Melody First draft chapters to the current static site.

This intentionally does not run generate.py because the HTMLBook source is behind
the current hand-maintained Level 2 chapter files.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
CHAPTERS = WEB / "chapters"

LEVEL3 = [
    (
        "chapter-level-3-why-melody-comes-before-more-theory",
        "Why Melody Comes Before More Theory",
        ROOT / "level3-ch01-why-melody-comes-before-more-theory.md",
    ),
    (
        "chapter-level-3-the-three-components-of-melody",
        "The Three Components of Melody",
        ROOT / "level3-ch02-the-three-components-of-melody.md",
    ),
    (
        "chapter-level-3-phrasing",
        "Phrasing = How the Melody Speaks",
        ROOT / "level3-ch03-rhythm-make-one-note-musical.md",
    ),
    (
        "chapter-level-3-contour-make-notes-move-with-direction",
        "Melodic Shape: Make Notes Move With Direction",
        ROOT / "level3-ch04-contour-make-notes-move-with-direction.md",
    ),
    (
        "chapter-level-3-target-tones-make-melody-connect-to-chords",
        "Note Choice: Make Melody Connect to Chords",
        ROOT / "level3-ch05-target-tones-make-melody-connect-to-chords.md",
    ),
    (
        "chapter-level-3-building-a-melody-over-i-vi-iv-v",
        "Building a Melody Over I-vi-IV-V",
        ROOT / "level3-ch06-building-a-melody-over-i-vi-iv-v.md",
    ),
    (
        "chapter-level-3-turning-a-scale-pattern-into-a-phrase",
        "Turning a Scale Pattern into a Phrase",
        ROOT / "level3-ch07-turning-a-scale-pattern-into-a-phrase.md",
    ),
    (
        "chapter-level-3-improvisation-as-real-time-melody-writing",
        "Improvisation as Real-Time Melody Writing",
        ROOT / "level3-ch08-improvisation-as-real-time-melody-writing.md",
    ),
]

LAST_L2_ID = "chapter-level-2-musical-application-open-position-melody-over-i-vi-iv-v"
APPENDIX_ID = "back-matter-appendix"


def inline_md(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def markdown_body(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    # Drop the top-level chapter title; the page template supplies it.
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    out: list[str] = []
    para: list[str] = []
    list_type: str | None = None

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(f"<p>{inline_md(' '.join(para))}</p>")
            para = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    for raw in lines:
        line = raw.strip()
        if not line:
            flush_para()
            close_list()
            continue
        if line.startswith("## "):
            flush_para()
            close_list()
            out.append(f"<h2>{inline_md(line[3:])}</h2>")
            continue
        if line.startswith("### "):
            flush_para()
            close_list()
            out.append(f"<h3>{inline_md(line[4:])}</h3>")
            continue
        m_num = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m_num:
            flush_para()
            if list_type != "ol":
                close_list()
                out.append("<ol>")
                list_type = "ol"
            out.append(f"<li>{inline_md(m_num.group(2))}</li>")
            continue
        if line.startswith("- "):
            flush_para()
            if list_type != "ul":
                close_list()
                out.append("<ul>")
                list_type = "ul"
            out.append(f"<li>{inline_md(line[2:])}</li>")
            continue
        para.append(line)

    flush_para()
    close_list()
    return "\n".join(out)


def level3_sidebar(active_id: str = "") -> str:
    items = []
    for i, (slug, title, _path) in enumerate(LEVEL3, start=1):
        active = " active" if slug == active_id else ""
        items.append(
            f'      <li class="sidebar-chapter{active} ch-theory">\n'
            f'        <a href="../chapters/{slug}.html"><span class="ch-num">{i}</span>{html.escape(title)}</a>\n'
            "      </li>"
        )
    open_attr = " open" if active_id else ""
    return (
        f'  <details class="sidebar-part part-vi"{open_attr}>\n'
        '    <summary class="sidebar-part-title">\n'
        '      <span class="part-num">VI</span>\n'
        '      Level 3: Melody\n'
        '    </summary>\n'
        '    <ol class="sidebar-chapters">\n'
        + "\n".join(items)
        + "\n    </ol>\n  </details>\n"
    )


def sidebar_from_template(active_id: str = "") -> str:
    template = (CHAPTERS / f"{LAST_L2_ID}.html").read_text(encoding="utf-8")
    nav = re.search(r'<nav class="sidebar".*?</nav>', template, re.S).group(0)
    nav = re.sub(r"  <details class=\"sidebar-part part-vi\".*?</details>\n", "", nav, flags=re.S)
    nav = nav.replace(' class="sidebar-chapter active ', ' class="sidebar-chapter ')
    nav = nav.replace('  <details class="sidebar-part part-v" open>', '  <details class="sidebar-part part-v">')
    nav = nav.replace('  <details class="sidebar-part back-matter">', level3_sidebar(active_id) + '  <details class="sidebar-part back-matter">')
    return nav


def chapter_page(idx: int) -> str:
    slug, title, path = LEVEL3[idx]
    prev_id, prev_title = (LAST_L2_ID, "Musical Application: Open-Position Melody over I-vi-IV-V") if idx == 0 else (LEVEL3[idx - 1][0], LEVEL3[idx - 1][1])
    next_id, next_title = (APPENDIX_ID, "Appendix") if idx == len(LEVEL3) - 1 else (LEVEL3[idx + 1][0], LEVEL3[idx + 1][1])
    body = markdown_body(path)
    sidebar = sidebar_from_template(slug)
    desc = "Level 3 melody writing and improvisation for guitar: phrasing, melodic shape, and note choice."
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} — Music Theory and The Fretboard (Level 3)</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{html.escape(title)} — Music Theory and The Fretboard (Level 3)">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="article">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&family=Newsreader:ital,opsz,wght@0,6..72,300..800;1,6..72,300..800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/styles.css">
</head>
<body class="chapter-page theme-theory" data-chapter-id="{slug}">
  <button class="drawer-toggle" id="drawer-toggle" aria-label="Open navigation" aria-expanded="false" aria-controls="sidebar">
    <span class="hamburger"></span>
  </button>
  <div class="sidebar-overlay" id="sidebar-overlay"></div>
{sidebar}
  <main class="content" id="main-content">
    <nav class="breadcrumb" aria-label="breadcrumb">
      <a href="../index.html">Home</a>
      <span class="bc-sep">›</span>
      <span>Level 3: Melody</span>
      <span class="bc-sep">›</span>
      <span>{html.escape(title)}</span>
    </nav>
    <article class="chapter-article" id="{slug}">
      <header class="chapter-header">
        <p class="chapter-number-label">Level 3 &middot; Chapter {idx + 1}</p>
        <h1 class="chapter-title">{html.escape(title)}</h1>
      </header>
      <div class="chapter-body">
{body}
      </div>
    </article>
    <nav class="prev-next" aria-label="Chapter navigation">
      <a href="../chapters/{prev_id}.html" class="prev-next-link prev-link">
        <span class="pn-label">← Previous</span>
        <span class="pn-title">{html.escape(prev_title)}</span>
      </a>
      <a href="../chapters/{next_id}.html" class="prev-next-link next-link">
        <span class="pn-label">Next →</span>
        <span class="pn-title">{html.escape(next_title)}</span>
      </a>
    </nav>
  </main>
  <button class="back-to-top" id="back-to-top" aria-label="Back to top">↑</button>
  <div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Image lightbox" hidden>
    <button class="lightbox-close" id="lightbox-close" aria-label="Close lightbox">×</button>
    <img class="lightbox-img" id="lightbox-img" src="" alt="">
  </div>
  <script src="../js/site.js"></script>
</body>
</html>
"""


def write_level3_pages() -> None:
    for idx, (slug, _title, _path) in enumerate(LEVEL3):
        (CHAPTERS / f"{slug}.html").write_text(chapter_page(idx), encoding="utf-8")


def update_existing_sidebars() -> None:
    for path in CHAPTERS.glob("*.html"):
        if path.name.startswith("chapter-level-3-"):
            continue
        text = path.read_text(encoding="utf-8")
        if "Level 3: Melody" in text:
            text = re.sub(r'  <details class="sidebar-part part-vi".*?</details>\n', level3_sidebar(""), text, flags=re.S)
        else:
            text = text.replace('  <details class="sidebar-part back-matter">', level3_sidebar("") + '  <details class="sidebar-part back-matter">')
        if path.name == f"{LAST_L2_ID}.html":
            text = re.sub(
                r'<a href="../chapters/back-matter-appendix.html" class="prev-next-link next-link">\s*<span class="pn-label">Next →</span>\s*<span class="pn-title">Appendix</span>\s*</a>',
                '<a href="../chapters/chapter-level-3-why-melody-comes-before-more-theory.html" class="prev-next-link next-link">\n'
                '        <span class="pn-label">Next →</span>\n'
                '        <span class="pn-title">Why Melody Comes Before More Theory</span>\n'
                '      </a>',
                text,
                flags=re.S,
            )
        if path.name == f"{APPENDIX_ID}.html":
            text = re.sub(
                r'<a href="../chapters/[^"]+" class="prev-next-link prev-link">\s*<span class="pn-label">← Previous</span>\s*<span class="pn-title">[^<]+</span>\s*</a>',
                '<a href="../chapters/chapter-level-3-improvisation-as-real-time-melody-writing.html" class="prev-next-link prev-link">\n'
                '        <span class="pn-label">← Previous</span>\n'
                '        <span class="pn-title">Improvisation as Real-Time Melody Writing</span>\n'
                '      </a>',
                text,
                count=1,
                flags=re.S,
            )
        path.write_text(text, encoding="utf-8")


def update_index() -> None:
    path = WEB / "index.html"
    text = path.read_text(encoding="utf-8")
    card = """

    <div class="part-card part-vi">
      <div class="part-card-header">
        <span class="part-card-num">VI</span>
        <h2 class="part-card-title">Level 3: Melody</h2>
      </div>
      <p class="part-card-desc">Phrasing, melodic shape, and note choice: turn the theory and fretboard materials from Levels 1-2 into real melodic phrases.</p>
      <ul class="part-chapter-list">
<li><a href="chapters/chapter-level-3-why-melody-comes-before-more-theory.html">Why Melody Comes Before More Theory</a></li><li><a href="chapters/chapter-level-3-the-three-components-of-melody.html">The Three Components of Melody</a></li><li><a href="chapters/chapter-level-3-phrasing.html">Phrasing = How the Melody Speaks</a></li><li><a href="chapters/chapter-level-3-contour-make-notes-move-with-direction.html">Melodic Shape: Make Notes Move With Direction</a></li><li><a href="chapters/chapter-level-3-target-tones-make-melody-connect-to-chords.html">Note Choice: Make Melody Connect to Chords</a></li><li><a href="chapters/chapter-level-3-building-a-melody-over-i-vi-iv-v.html">Building a Melody Over I-vi-IV-V</a></li><li class="more-chapters">…and 2 more chapters</li>
</ul>
      <a class="part-card-cta" href="chapters/chapter-level-3-why-melody-comes-before-more-theory.html">Start reading →</a>
    </div>"""
    if "Level 3: Melody" in text:
        text = re.sub(
            r'\n\n    <div class="part-card part-vi">.*?      <a class="part-card-cta" href="chapters/chapter-level-3-why-melody-comes-before-more-theory.html">Start reading →</a>\n    </div>',
            card,
            text,
            count=1,
            flags=re.S,
        )
        path.write_text(text, encoding="utf-8")
        return
    marker = "      </div>\n    </section>"
    text = text.replace(marker, card + "\n" + marker, 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    write_level3_pages()
    update_existing_sidebars()
    update_index()
    print("Added Level 3 Melody pages and navigation.")


if __name__ == "__main__":
    main()
