"""Generate the chromatic-to-diatonic palette diagram used in Level 1."""

from pathlib import Path
import sys

TOOLS_DIR = Path(__file__).parents[2] / "tools" / "fretboard-generator"
sys.path.insert(0, str(TOOLS_DIR))

from src.fretboard_svg import NOTE_FONT, _e, _svg_open, _t
from src.string_strip import degree_color


WIDTH = 1258
HEIGHT = 337
LEFT = 49.0
STEP = (WIDTH - 2 * LEFT) / 12
TOP_Y = 50.0
BOTTOM_Y = 262.0
TOP_RADIUS = 25.0
BOTTOM_RADIUS = 16.0
INK = "#1a1a1a"
SCALE_OFFSETS = (0, 2, 4, 5, 7, 9, 11, 12)
STEP_INSTRUCTIONS = (
    "Choose a Starting Note",
    "Move Up 2 Notes",
    "Move Up 2 More Notes",
    "Move Up 1 Note",
    "Move Up 2 More Notes",
    "Move Up 2 More Notes",
    "Move Up 2 More Notes",
)


def blend(start: str, end: str, amount: float) -> str:
    """Blend two six-digit hex colors."""
    a = tuple(int(start[i : i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(end[i : i + 2], 16) for i in (1, 3, 5))
    rgb = tuple(round(x + (y - x) * amount) for x, y in zip(a, b))
    return "#" + "".join(f"{channel:02x}" for channel in rgb)


def down_arrow(x: float, top: float, height: float) -> str:
    """Return a simple outlined downward arrow centered at x."""
    shaft_half = 8.0
    head_half = 20.0
    head_height = 20.0
    bottom = top + height
    shoulder = bottom - head_height
    points = (
        f"{x - shaft_half},{top} {x + shaft_half},{top} "
        f"{x + shaft_half},{shoulder} {x + head_half},{shoulder} "
        f"{x},{bottom} {x - head_half},{shoulder} "
        f"{x - shaft_half},{shoulder}"
    )
    return _e(
        "polygon",
        points=points,
        fill="none",
        stroke=INK,
        stroke_width=5,
        stroke_linejoin="round",
    )


def build_svg(*, revealed_count: int = 8, instruction: str = "Apply the Major Scale Formula") -> str:
    if not 1 <= revealed_count <= 8:
        raise ValueError("revealed_count must be between 1 and 8")

    parts: list[str] = []

    # One chromatic octave: 12 semitone steps plus the repeated starting pitch.
    for index in range(13):
        x = LEFT + index * STEP
        fill = blend("#181818", "#b8b8b8", index / 12)
        parts.append(_e("circle", cx=round(x, 2), cy=TOP_Y, r=TOP_RADIUS, fill=fill))

    center_x = WIDTH / 2
    parts.append(down_arrow(center_x, 82, 50))
    parts.append(
        _t(
            "text",
            instruction,
            x=center_x,
            y=163,
            text_anchor="middle",
            font_size=22,
            font_weight="bold",
            font_family=NOTE_FONT,
            fill=INK,
        )
    )
    parts.append(down_arrow(center_x, 177, 50))

    # Keep all 13 chromatic positions. The five notes outside the major scale
    # remain black; the eight scale notes receive rainbow colors and labels.
    revealed_offsets = SCALE_OFFSETS[:revealed_count]
    degree_by_offset = {offset: index for index, offset in enumerate(revealed_offsets)}
    for offset in range(13):
        x = LEFT + offset * STEP
        degree_index = degree_by_offset.get(offset)
        if degree_index is None:
            parts.append(
                _e(
                    "circle",
                    cx=round(x, 2),
                    cy=BOTTOM_Y,
                    r=BOTTOM_RADIUS,
                    fill=INK,
                )
            )
            continue

        degree = degree_index % 7
        octave = 1 if degree_index == 7 else 0
        fill = degree_color(degree, octave)
        parts.append(
            _e(
                "circle",
                cx=round(x, 2),
                cy=BOTTOM_Y,
                r=BOTTOM_RADIUS,
                fill=fill,
            )
        )

        # Both the circumflex and numeral sit beneath the colored dot.
        hat_bottom = 302.0
        hat_top = 294.0
        hat_half_width = 7.0
        points = (
            f"{x - hat_half_width:.2f},{hat_bottom:.2f} "
            f"{x:.2f},{hat_top:.2f} "
            f"{x + hat_half_width:.2f},{hat_bottom:.2f}"
        )
        parts.append(
            _e(
                "polyline",
                points=points,
                fill="none",
                stroke=INK,
                stroke_width=3,
                stroke_linecap="round",
                stroke_linejoin="round",
            )
        )
        parts.append(
            _t(
                "text",
                str(degree + 1),
                x=round(x, 2),
                y=331,
                text_anchor="middle",
                font_size=27,
                font_weight="bold",
                font_family=NOTE_FONT,
                fill=INK,
            )
        )

    svg_open = _svg_open(WIDTH, HEIGHT, f"0 0 {WIDTH} {HEIGHT}")
    return f"{svg_open}\n  " + "\n  ".join(parts) + "\n</svg>"


if __name__ == "__main__":
    output_dir = TOOLS_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    for step, instruction in enumerate(STEP_INSTRUCTIONS, start=1):
        output = output_dir / f"chromatic-to-diatonic-step-{step}.svg"
        output.write_text(
            build_svg(revealed_count=step, instruction=instruction),
            encoding="utf-8",
        )
        print(output)

    final_output = output_dir / "chromatic-to-diatonic-applied.svg"
    final_output.write_text(build_svg(), encoding="utf-8")
    print(final_output)
