#!/usr/bin/env python3
"""
Normalize the Level 1 tail after inserting Chapter 31, "The Sharp Side of the
Circle of Fifths."  Chapter HTML files are intentionally edited in place; the
HTMLBook is not touched.

The sidebar table of contents is duplicated in every full chapter page, so the
three Level 1 sections below are rendered into every page that carries them.
"""
import pathlib
import re


CH = pathlib.Path(__file__).resolve().parent.parent / "chapters"


LEVEL1_CORE = [
    ("chapter-music-theory-the-major-scale-creates-a-palette-of-7-colors-notes.html", "Music Theory: The Major Scale creates a palette of 7 colors (notes)", "ch-theory", 9),
    ("chapter-the-fretboard-the-major-scale-on-a-single-string.html", "The Fretboard: The Major Scale on a single string", "ch-fretboard", 10),
    ("chapter-music-theory-the-c-major-scale.html", "Music Theory: The C Major Scale", "ch-theory", 11),
    ("chapter-the-fretboard-memorizing-note-locations-on-the-e-a-d-strings.html", "The Fretboard: Memorizing Note Locations on the E, A, D Strings", "ch-fretboard", 12),
    ("chapter-music-theory-intro-to-intervals.html", "Music Theory: Intro to Intervals", "ch-theory", 13),
    ("chapter-the-harmonic-overtone-series.html", "Music Theory and The Fretboard: The Harmonic (Overtone) Series", "ch-both", 14),
    ("chapter-music-theory-the-5th-interval.html", "Music Theory: The Perfect Intervals", "ch-theory", 15),
    ("chapter-the-fretboard-power-chords-2.html", "The Fretboard: Perfect 4ths, 5ths, and Octave Shapes", "ch-fretboard", 16),
    ("chapter-music-theory-power-chord-chord-symbols.html", "Music Theory: Chords In a Key", "ch-theory", 17),
    ("chapter-the-fretboard-power-chord-shapes.html", "The Fretboard: The 6 Power Chord Shapes in the Key of C", "ch-fretboard", 18),
    ("chapter-music-theory-why-the-5th-interval-b-f-is-not-a-perfect-5th.html", "Music Theory: Why B–F is not a Perfect 5th", "ch-theory", 19),
    ("chapter-the-fretboard-the-tritone-shape-on-the-e-a-d-g-string-set.html", "The Fretboard: The Diminished 5th Shape on the E-A-D-G String Set", "ch-fretboard", 20),
    ("chapter-music-theory-chord-voicings.html", "Music Theory: Chord Voicings", "ch-theory", 21),
    ("chapter-the-fretboard-a-very-common-power-chord-voicing.html", "The Fretboard: A Very Common Power Chord Voicing", "ch-fretboard", 22),
    ("chapter-music-theory-inverting-the-perfect-intervals.html", "Music Theory: Inverting the Perfect Intervals", "ch-theory", 23),
    ("chapter-the-fretboard-power-chord-inversions.html", "The Fretboard: Power Chord Inversions", "ch-fretboard", 24),
    ("chapter-musical-application-note-memorization-power-chords.html", "Musical Application (Note Recall + Power Chords): Playing Along with Songs", "ch-theory", 25),
    ("chapter-music-theory-intro-to-sharps-key-signatures-and-the-g-major-scale.html", "Music Theory: Intro to Sharps, Naturals, Key Signatures, and the G Major Scale", "ch-theory", 26),
    ("chapter-the-fretboard-the-g-major-scale.html", "The Fretboard: The G Major Scale and Power Chords in the Key of G", "ch-fretboard", 27),
    ("chapter-music-theory-key-of-d-two-sharps.html", "Music Theory: Key of D (two sharps)", "ch-theory", 28),
    ("chapter-the-fretboard-the-d-major-scale.html", "The Fretboard: The D Major Scale and Power Chords in the Key of D", "ch-fretboard", 29),
    ("chapter-music-theory-exercises-scale-building.html", "Music Theory Exercises: Building the A, E, B, and F♯ Major Scales", "ch-theory", 30),
    ("chapter-music-theory-the-sharp-side-of-the-circle-of-fifths.html", "Music Theory: The Sharp Side of the Circle of Fifths", "ch-theory", 31),
]

STANDARD_NOTATION = [
    ("chapter-some-important-terms.html", "Some Important Terms", "ch-misc", 32),
    ("chapter-notes-on-the-e-string.html", "Notes on the E String", "ch-misc", 33),
    ("chapter-notes-on-the-b-string.html", "Notes on the B String", "ch-misc", 34),
    ("chapter-notes-on-the-g-string.html", "Notes on the G String", "ch-misc", 35),
    ("chapter-notes-on-the-d-string.html", "Notes on the D String", "ch-misc", 36),
    ("chapter-notes-on-the-a-string.html", "Notes on the A String", "ch-misc", 37),
    ("chapter-notes-on-the-low-e-string.html", "Notes on the low E String", "ch-misc", 38),
]

EAR_TRAINING = [
    ("chapter-do-mi-sol.html", "Do - Mi - Sol", "ch-misc", 39),
    ("chapter-la.html", "La", "ch-misc", 40),
    ("chapter-re.html", "Re", "ch-misc", 41),
    ("chapter-fa.html", "Fa", "ch-misc", 42),
    ("chapter-slug-5-note-scale.html", "5 Note Scale", "ch-misc", 43),
    ("chapter-ti-and-the-major-scale.html", "Ti and The Major Scale", "ch-misc", 44),
]

PARTS = {
    "part-ii": LEVEL1_CORE,
    "part-iii": STANDARD_NOTATION,
    "part-iv": EAR_TRAINING,
}

TAIL_ORDER = LEVEL1_CORE[-2:] + STANDARD_NOTATION + EAR_TRAINING
TAIL_INDEX = {f: i for i, (f, _title, _cls, _num) in enumerate(TAIL_ORDER)}

BOUNDARY_PREV = (
    "chapter-the-fretboard-the-d-major-scale.html",
    "The Fretboard: The D Major Scale and Power Chords in the Key of D",
)
BOUNDARY_NEXT = (
    "chapter-level-2-major-and-minor-intervals.html",
    "Major and Minor Intervals: The Imperfect Interval Family",
)

NAV_RE = re.compile(r'    <nav class="prev-next".*?</nav>', re.DOTALL)
NUMLABEL_RE = re.compile(r'<p class="chapter-number-label">Chapter \d+</p>')


def sidebar_items(entries, active_file):
    lines = []
    for filename, title, kind, number in entries:
        active = " active" if filename == active_file else ""
        lines.extend([
            f'      <li class="sidebar-chapter{active} {kind}">',
            f'        <a href="../chapters/{filename}"><span class="ch-num">{number}</span>{title}</a>',
            '      </li>',
        ])
    return "\n" + "\n".join(lines) + "\n    "


def replace_part(text, part_class, entries, active_file):
    pattern = re.compile(
        rf'(<details class="sidebar-part {part_class}"[^>]*>.*?<ol class="sidebar-chapters">)(.*?)(\s*</ol>)',
        re.DOTALL,
    )
    return pattern.sub(
        lambda m: m.group(1) + sidebar_items(entries, active_file) + m.group(3),
        text,
        count=1,
    )


def prev_next_block(index):
    prev = BOUNDARY_PREV if index == 0 else (TAIL_ORDER[index - 1][0], TAIL_ORDER[index - 1][1])
    nxt = BOUNDARY_NEXT if index == len(TAIL_ORDER) - 1 else (TAIL_ORDER[index + 1][0], TAIL_ORDER[index + 1][1])
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


def process_chapter(path):
    filename = path.name
    text = original = path.read_text(encoding="utf-8")

    for part_class, entries in PARTS.items():
        text = replace_part(text, part_class, entries, filename)

    if filename in TAIL_INDEX:
        index = TAIL_INDEX[filename]
        number = TAIL_ORDER[index][3]
        text, count = NUMLABEL_RE.subn(
            f'<p class="chapter-number-label">Chapter {number}</p>', text
        )
        if count != 1:
            raise SystemExit(f"chapter-number-label not found in {filename}: {count}")
        text, count = NAV_RE.subn(prev_next_block(index), text)
        if count != 1:
            raise SystemExit(f"prev-next nav not found in {filename}: {count}")

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def process_index():
    path = CH.parent / "index.html"
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'(<p class="part-card-desc">The Major Scale.*?<li class="more-chapters">…and )\d+( more chapters</li>)',
        lambda m: m.group(1) + str(len(LEVEL1_CORE) - 6) + m.group(2),
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise SystemExit(f"index Level 1 count not found: {count}")
    path.write_text(updated, encoding="utf-8")
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
