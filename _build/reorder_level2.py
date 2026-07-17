"""
One-off: normalize the Level 2 (Part V) ordering across every chapter file +
index.html. The sidebar TOC is duplicated in every chapter page, so the canonical
order below is rendered into all of them.

DO NOT run generate.py (it rebuilds chapter files from the htmlbook source and
would clobber hand-edited Level 2 content). This script edits the per-chapter
files in place, which are the source of truth.
"""
import re
import pathlib

CH = pathlib.Path(__file__).resolve().parent.parent / "chapters"

# (filename, sidebar_title, full_title) in canonical Level 2 order.
ORDER = [
    ("chapter-level-2-major-and-minor-intervals.html",
     "Major and Minor Intervals: The Imperfect Interval Family",
     "Major and Minor Intervals: The Imperfect Interval Family"),
    ("chapter-level-2-the-fretboard-major-and-minor-3rd-shapes-on-the-e-a-d-g-string-set.html",
     "The Fretboard: Major and Minor 3rd Shapes (E-A-D-G Set)",
     "The Fretboard: Major and Minor 3rd Interval Shapes on the E-A-D-G String Set"),
    ("chapter-level-2-harmonizing-the-c-major-scale-in-3rds.html",
     "Harmonizing the C Major Scale in 3rds",
     "Harmonizing the C Major Scale in 3rds"),
    ("chapter-level-2-the-fretboard-harmonizing-the-c-major-scale-in-3rds.html",
     "The Fretboard: Harmonizing the C Major Scale in 3rds",
     "The Fretboard: Harmonizing the C Major Scale in 3rds"),
    ("chapter-level-2-music-theory-the-triad.html",
     "Music Theory: The Triad (Bird's-Eye View)",
     "Music Theory: The Triad (A Bird's-Eye View)"),
    ("chapter-level-2-music-theory-the-major-triad.html",
     "Music Theory: The Major Triad",
     "Music Theory: The Major Triad"),
    ("chapter-level-2-music-theory-the-minor-triad.html",
     "Music Theory: The Minor Triad",
     "Music Theory: The Minor Triad"),
    ("chapter-level-2-the-fretboard-the-major-triad-shape-on-the-e-a-d-and-a-d-g-string-sets.html",
     "The Fretboard: Major and Minor Triad Shapes (E-A-D and A-D-G Sets)",
     "The Fretboard: Major and Minor Triad Shapes on the E-A-D and A-D-G String Sets"),
    ("chapter-level-2-the-primary-triads.html",
     "Chords in a Key",
     "Music Theory and The Fretboard: Chords in a Key"),
    ("chapter-level-2-the-fretboard-building-the-rest-of-the-fretboard.html",
     "The Fretboard: Building the Rest of the Fretboard",
     "The Fretboard: Building the Rest of the Fretboard"),
    ("chapter-level-2-the-fretboard-memorizing-the-g-and-b-strings.html",
     "The Fretboard: Memorizing the G and B Strings",
     "The Fretboard: Memorizing the G and B Strings"),
    ("chapter-level-2-the-fretboard-the-c-major-scale-in-open-position.html",
     "The Fretboard: The C Major Scale in Open Position",
     "The Fretboard: The C Major Scale in Open Position"),
    ("chapter-level-2-the-fretboard-the-5th-and-4th-shapes-on-the-treble-strings.html",
     "The Fretboard: The 5th, 4th, and 3rd Shapes (Treble Strings)",
     "The Fretboard: The 5th, 4th, and 3rd Shapes on the Treble Strings"),
    ("chapter-level-2-the-fretboard-major-and-minor-triad-shapes-on-the-d-g-b-and-g-b-e-string-sets.html",
     "The Fretboard: Major and Minor Triad Shapes (D-G-B and G-B-E Sets)",
     "The Fretboard: Major and Minor Triad Shapes on the D-G-B and G-B-E String Sets"),
    ("chapter-level-2-the-fretboard-the-e-shape-barre-chord.html",
     "The Fretboard: Your First Movable Chord (The E-Shape Barre)",
     "The Fretboard: Your First Movable Chord (The E-Shape Barre)"),
    ("chapter-level-2-the-fretboard-the-a-shape-barre-chord.html",
     "The Fretboard: Your Second Movable Chord (The A-Shape Barre)",
     "The Fretboard: Your Second Movable Chord (The A-Shape Barre)"),
    ("chapter-level-2-barre-chords-are-triad-voicings.html",
     "Barre Chords Are Triad Voicings",
     "Music Theory and The Fretboard: Barre Chords Are Triad Voicings"),
    ("chapter-level-2-the-fretboard-the-triad-arpeggio.html",
     "The Fretboard: The Triad Arpeggio",
     "The Fretboard: The Triad Arpeggio"),
    ("chapter-level-2-the-fretboard-the-movable-major-scale-around-the-e-shape-barre.html",
     "The Fretboard: The Movable Major Scale Around the E-Shape Barre",
     "The Fretboard: The Movable Major Scale Around the E-Shape Barre"),
    ("chapter-level-2-music-theory-inverting-the-imperfect-intervals.html",
     "Music Theory: Inverting the Imperfect Intervals",
     "Music Theory: Inverting the Imperfect Intervals"),
    ("chapter-level-2-the-fretboard-major-and-minor-6th-shapes.html",
     "The Fretboard: Major and Minor 6th Shapes (Skip a String)",
     "The Fretboard: Major and Minor 6th Shapes (Skip a String)"),
    ("chapter-level-2-music-theory-triad-inversions.html",
     "Music Theory: Triad Inversions",
     "Music Theory: Triad Inversions"),
    ("chapter-level-2-the-fretboard-triad-inversions.html",
     "The Fretboard: Triad Inversions (One Chord, Three Homes)",
     "The Fretboard: Triad Inversions (One Chord, Three Homes)"),
    ("chapter-level-2-music-theory-the-spread-triad-and-the-10th.html",
     "Music Theory: The Spread Triad and the 10th",
     "Music Theory: The Spread Triad and the 10th"),
    ("chapter-level-2-the-fretboard-the-spread-triad-shape-on-the-e-d-g-string-set.html",
     "The Fretboard: The Spread Triad Shape (E-D-G Set)",
     "The Fretboard: The Spread Triad Shape on the E-D-G String Set"),
    ("chapter-level-2-the-rest-of-the-chords-in-the-key.html",
     "The Rest of the Chords in the Key",
     "Music Theory and The Fretboard: The Rest of the Chords in the Key"),
    ("chapter-level-2-music-theory-chord-families-and-function.html",
     "Music Theory: Chord Families and Function",
     "Music Theory: Chord Families and Function"),
    ("chapter-level-2-music-theory-common-chord-progressions.html",
     "Music Theory: Common Chord Progressions in a Key",
     "Music Theory: Common Chord Progressions in a Key"),
    ("chapter-level-2-the-fretboard-the-numeral-becomes-a-shape.html",
     "The Fretboard: The Numeral Becomes a Shape",
     "The Fretboard: The Numeral Becomes a Shape"),
    ("chapter-level-2-music-theory-sus-chords.html",
     "Music Theory: Sus Chords",
     "Music Theory: Sus Chords"),
    ("chapter-level-2-the-fretboard-sus-chords-on-barre-shapes.html",
     "The Fretboard: Sus Chords on Barre Shapes",
     "The Fretboard: Sus Chords on Barre Shapes"),
    ("chapter-level-2-music-theory-the-minor-scale.html",
     "Music Theory: The Minor Scale",
     "Music Theory: The Minor Scale"),
    ("chapter-level-2-the-fretboard-the-d-minor-scale-and-chords.html",
     "The Fretboard: The D Minor Scale and Chords",
     "The Fretboard: The D Minor Scale and Chords"),
    ("chapter-level-2-music-theory-relative-keys-and-the-f-major-scale.html",
     "Music Theory: Relative Keys and the F Major Scale",
     "Music Theory: Relative Keys and the F Major Scale"),
    ("chapter-level-2-the-fretboard-the-f-major-scale.html",
     "The Fretboard: The F Major Scale",
     "The Fretboard: The F Major Scale"),
    ("chapter-level-2-music-theory-completing-the-circle-of-fifths.html",
     "Music Theory: Completing the Circle of Fifths",
     "Music Theory: Completing the Circle of Fifths"),
    ("chapter-level-2-music-theory-the-augmented-triad.html",
     "Music Theory: The Augmented Triad",
     "Music Theory: The Augmented Triad"),
    ("chapter-level-2-musical-application-open-position-melody-over-i-vi-iv-v.html",
     "Musical Application: Open-Position Melody over I-vi-IV-V",
     "Musical Application: Open-Position Melody over I-vi-IV-V"),
]
# chapter-common-triad-voicings-caged.html removed 2026-07-01: absorbed into
# chapter-level-2-barre-chords-are-triad-voicings.html (file kept on disk, unlinked).
# chapter-major-minor-and-diminished-triads.html removed 2026-07-01: old preview,
# superseded by the dedicated Major/minor/diminished triad chapters (file kept on
# disk, unlinked). Its "G is V in C, I in G, IV in D" chords-from-intervals passage
# is salvage material for the planned common-progressions chapter.
# chapter-level-2-music-theory-the-diminished-triad.html removed 2026-07-02:
# absorbed into chapter-level-2-the-primary-triads.html, retitled "Chords in a Key"
# (file kept on disk, unlinked).
# chapter-level-2-the-fretboard-standard-tuning.html removed 2026-07-02: absorbed
# into chapter-level-2-the-fretboard-building-the-rest-of-the-fretboard.html as its
# closing "Standard tuning: all 4ths but one" section (file kept on disk, unlinked).
# chapter-level-2-fretboard-major-and-minor-3rd-shapes.html removed 2026-07-02:
# absorbed into chapter-level-2-the-fretboard-the-5th-and-4th-shapes-on-the-treble-strings.html,
# retitled "The Fretboard: The 5th, 4th, and 3rd Shapes on the Treble Strings"; its
# tab exercise figures were replaced with fretboard diagrams (gen_third_treble.py).
# File kept on disk, unlinked.
# chapter-secondary-chords.html removed 2026-07-02: rewritten as
# chapter-level-2-the-rest-of-the-chords-in-the-key.html ("secondary chords" term
# retired book-wide; collides with Level 3's secondary dominants). Old file kept on
# disk, unlinked.

# Boundaries: chapter immediately before the first Level 2 chapter, and after the last.
BOUNDARY_PREV = ("chapter-ti-and-the-major-scale.html", "Ti and The Major Scale")
BOUNDARY_NEXT = ("chapter-level-3-why-melody-comes-before-more-theory.html",
                 "Why Melody Comes Before More Theory")

FILES = {f for f, _, _ in ORDER}
INDEX_BY_FILE = {f: i for i, (f, _, _) in enumerate(ORDER)}


def sidebar_ol(active_file):
    lines = []
    for i, (f, side, _full) in enumerate(ORDER, start=1):
        cls = "sidebar-chapter active ch-misc" if f == active_file else "sidebar-chapter ch-misc"
        lines.append(f'      <li class="{cls}">')
        lines.append(f'        <a href="../chapters/{f}"><span class="ch-num">{i}</span>{side}</a>')
        lines.append('      </li>')
    return "\n" + "\n".join(lines)


def prev_next_block(idx):
    prev = BOUNDARY_PREV if idx == 0 else (ORDER[idx - 1][0], ORDER[idx - 1][2])
    nxt = BOUNDARY_NEXT if idx == len(ORDER) - 1 else (ORDER[idx + 1][0], ORDER[idx + 1][2])
    return (
        '    <nav class="prev-next" aria-label="Chapter navigation">\n'
        f'      <a href="../chapters/{prev[0]}" class="prev-next-link prev-link">\n'
        '        <span class="pn-label">← Previous</span>\n'
        f'        <span class="pn-title">{prev[1]}</span>\n'
        '      </a>\n'
        f'      <a href="../chapters/{nxt[0]}" class="prev-next-link next-link">\n'
        '        <span class="pn-label">Next →</span>\n'
        f'        <span class="pn-title">{nxt[1]}</span>\n'
        '      </a>\n'
        '    </nav>'
    )


PARTV_RE = re.compile(
    r'(<details class="sidebar-part part-v"[^>]*>.*?<ol class="sidebar-chapters">)(.*?)(\s*</ol>)',
    re.DOTALL)
NAV_RE = re.compile(r'    <nav class="prev-next".*?</nav>', re.DOTALL)
NUMLABEL_RE = re.compile(r'<p class="chapter-number-label">Level 2 &middot; Chapter \d+</p>')


def process_chapter(path):
    f = path.name
    s = orig = path.read_text()

    # 1. Rewrite the Level 2 sidebar block (every chapter page carries it).
    active = f if f in FILES else None
    new_s, n = PARTV_RE.subn(
        lambda m: m.group(1) + sidebar_ol(active) + "\n    </ol>", s
    )
    if n != 1:
        raise SystemExit(f"part-v sidebar not found (or multiple) in {f}: {n}")
    s = new_s

    # 2. For Level 2 chapters: fix the chapter-number label and prev/next nav.
    if f in FILES:
        idx = INDEX_BY_FILE[f]
        s, nl = NUMLABEL_RE.subn(
            f'<p class="chapter-number-label">Level 2 &middot; Chapter {idx + 1}</p>', s)
        if nl != 1:
            raise SystemExit(f"chapter-number-label not found in {f}: {nl}")
        s, nn = NAV_RE.subn(prev_next_block(idx), s)
        if nn != 1:
            raise SystemExit(f"prev-next nav not found in {f}: {nn}")

    # 3. Boundary chapter before Level 2: its Next must point at the new ch1.
    if f == BOUNDARY_PREV[0]:
        first_f, _, first_full = ORDER[0]
        s = re.sub(
            r'(<a href="\.\./chapters/)[^"]+(" class="prev-next-link next-link">\s*'
            r'<span class="pn-label">Next →</span>\s*<span class="pn-title">)[^<]+',
            lambda m: m.group(1) + first_f + m.group(2) + first_full, s, count=1)

    if s != orig:
        path.write_text(s)
        return True
    return False


def process_index():
    p = CH.parent / "index.html"
    s = p.read_text()
    first6 = "".join(
        f'<li><a href="chapters/{f}">{full}</a></li>'
        for f, _, full in ORDER[:6])
    remaining = len(ORDER) - 6
    new_list = first6 + f'<li class="more-chapters">…and {remaining} more chapters</li>'

    # Only the Level 2 card (anchored on its description text).
    s, n = re.subn(
        r'(<p class="part-card-desc">Completing the fretboard.*?<ul class="part-chapter-list">\s*)(.*?)(\s*</ul>)',
        lambda m: m.group(1) + new_list + m.group(3), s, count=1, flags=re.DOTALL)
    if n != 1:
        raise SystemExit(f"index Level 2 list not found: {n}")
    # Level 2 card CTA -> new ch1.
    s, n = re.subn(
        r'(<p class="part-card-desc">Completing the fretboard.*?<a class="part-card-cta" href=")[^"]+',
        lambda m: m.group(1) + "chapters/" + ORDER[0][0], s, count=1, flags=re.DOTALL)
    if n != 1:
        raise SystemExit(f"index Level 2 CTA not found: {n}")
    p.write_text(s)
    print("updated index.html")


def main():
    changed = 0
    for path in sorted(CH.glob("*.html")):
        if process_chapter(path):
            changed += 1
    print(f"updated {changed} chapter files")
    process_index()


if __name__ == "__main__":
    main()
