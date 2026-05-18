"""Generate the 1200x630 Open Graph image for mubi2letterboxd.

Run from the repo root:  .venv/bin/python scripts/generate_og.py
Output:                  static/og-image.png

The image mirrors the live site: cream background, three blurred
optic blobs (magenta / cobalt / lavender) multiplied in, film grain,
and the headline in Didot with the italic tagline beneath. macOS-stock
fonts only (Didot, Helvetica), so no extra installs are needed.
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
CREAM = (243, 242, 233)
INK = (1, 21, 137)
INK_DIM = (26, 37, 112)
MAGENTA = (254, 1, 190)
LAVENDER = (196, 198, 231)

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
HELV = "/System/Library/Fonts/Helvetica.ttc"


def optic_layer() -> Image.Image:
    """Three big colored circles, heavily blurred, on white. Multiplied onto
    the cream base later — same effect as `mix-blend-mode: multiply` in CSS.
    """
    layer = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(layer)
    draw.ellipse([(-260, -260), (760, 760)], fill=MAGENTA)
    draw.ellipse([(720, 60), (1480, 820)], fill=INK)
    draw.ellipse([(80, 360), (980, 1180)], fill=LAVENDER)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=150))
    # Fade towards white so multiply doesn't crush the cream into mud.
    return Image.blend(Image.new("RGB", (W, H), (255, 255, 255)), layer, 0.62)


def grain_layer() -> Image.Image:
    """Soft monochrome film grain, low opacity, multiplied last."""
    noise = Image.effect_noise((W, H), 28).convert("RGB")
    return Image.blend(Image.new("RGB", (W, H), (255, 255, 255)), noise, 0.22)


def main() -> None:
    base = Image.new("RGB", (W, H), CREAM)
    base = ImageChops.multiply(base, optic_layer())
    base = ImageChops.multiply(base, grain_layer())

    draw = ImageDraw.Draw(base)

    title_font = ImageFont.truetype(DIDOT, 88, index=0)
    tag_font = ImageFont.truetype(DIDOT, 40, index=1)
    kicker_font = ImageFont.truetype(HELV, 20, index=1)
    foot_font = ImageFont.truetype(HELV, 18, index=1)
    csv_font = ImageFont.truetype(HELV, 16, index=0)

    pad = 80

    # Kicker with magenta dot
    dot_r = 7
    dot_y = pad + 8
    draw.ellipse([(pad, dot_y), (pad + dot_r * 2, dot_y + dot_r * 2)], fill=MAGENTA)
    draw.text(
        (pad + dot_r * 2 + 14, pad),
        "MUBI  ·  LETTERBOXD",
        font=kicker_font,
        fill=INK,
    )

    # Title (two lines)
    title_lines = ["Export your MUBI watchlist", "to Letterboxd."]
    y = 180
    for i, line in enumerate(title_lines):
        draw.text((pad, y + i * 104), line, font=title_font, fill=INK)

    # Italic tagline
    draw.text(
        (pad, y + len(title_lines) * 104 + 24),
        "Move your watchlist across the aisle.",
        font=tag_font,
        fill=INK_DIM,
    )

    # Bottom-left footer
    draw.text(
        (pad, H - pad - 4),
        "MUBI2LETTERBOXD  ·  BUILT BY CENGIZ ÇAKIR",
        font=foot_font,
        fill=INK,
    )

    # Bottom-right tiny CSV preview
    csv_lines = ["Title,Year", "Stalker,1979", "In the Mood for Love,2000"]
    for i, line in enumerate(csv_lines):
        bbox = csv_font.getbbox(line)
        tw = bbox[2] - bbox[0]
        draw.text(
            (W - pad - tw, H - pad - 4 - (len(csv_lines) - 1 - i) * 22),
            line,
            font=csv_font,
            fill=INK_DIM,
        )

    out = Path(__file__).resolve().parent.parent / "static" / "og-image.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    base.save(out, "PNG", optimize=True)
    print(f"Wrote {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
