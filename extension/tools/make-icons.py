#!/usr/bin/env python3
"""Draw the toolbar icons. Run it, do not hand-edit what it writes.

    python3 extension/tools/make-icons.py

WHY THIS FILE EXISTS
--------------------
Chrome will not take an SVG for a toolbar icon. It wants PNGs at fixed sizes,
and without them it draws a puzzle piece. So the mark has to be rasterised.

No image library is installed on this machine and decision 0002 says nothing
comes off the network, so nothing may be pip-installed to do it. The mark is
lucky: it is four axis-aligned rectangles and one circle, so a PNG writer built
out of `zlib` and `struct` -- both in the standard library -- draws it exactly.
Everything is supersampled 16x and box-filtered down, which is where the clean
edges at 16px come from.

WHAT IT DRAWS
-------------
Two sets, because the toolbar has two states and design/canvas/Extension.dc.html
draws both:

    icon-16/32/48/128.png         quiet. The mark in --v-ink-520. No dot.
    icon-on-16/32/48/128.png      a job post is on this page. The mark in
                                  --v-ink, with a --v-agent dot bottom right.

THE TILE
--------
design/assets/mark.svg carries no background on purpose. design/assets/
favicon.svg does carry one, and says why: a toolbar gives the mark no colour to
inherit and no ground to sit on. A toolbar icon is the favicon's situation, not
the mark's, so every size here is drawn on the favicon's tile.

THE GEOMETRY
------------
Two different drawings, exactly as design/assets/ ships them:

    16px            favicon.svg. Four strokes at 1.5, its own weights.
    32/48/128px     mark.svg. Stroke 3 in a 32 box.

favicon.svg's own note is explicit that it is not mark.svg shrunk, and that
shrinking mark.svg instead will blur it.

ROOM FOR THE DOT
----------------
The artboard hangs the dot off the corner of the mark: `right:-2px;bottom:-2px`
on a 16px box. In a browser that is fine, because the mark is an element on a
toolbar and has room around it. A PNG has no outside -- anything past the edge
is simply cut off, and drawing the dot inside the mark instead swallows the
right-hand bracket.

So the box here is 18 units and the mark is drawn into the first 16 of them.
The mark keeps its own proportions, the dot keeps the artboard's position and
size, and nothing is clipped. The 32 unit drawing gets the same treatment in a
36 unit box.

The quiet icon uses the same inset box even though it has no dot, so the mark
does not change size when the state changes.

THE COLOURS
-----------
Every colour comes from design/tokens.css, converted here rather than copied as
a hex, so there is one source for them and the conversion is reproducible. The
oklch -> sRGB maths is Bjorn Ottosson's, the same transform a browser runs.

    --v-bg-1       the tile
    --v-ink        the mark, awake
    --v-ink-520    the mark, quiet          ("the badge when it is asleep")
    --v-agent      the dot                  ("a job post is here")
"""

import math
import struct
import zlib
from pathlib import Path

ICONS = Path(__file__).resolve().parent.parent / "icons"

# Supersampling factor. 16 is well past the point where more stops showing.
SS = 16


# --- colour ----------------------------------------------------------------
# Straight out of design/tokens.css. Do not paste a hex in here; paste the
# token's own value and let the conversion below do the work.

TOKENS = {
    "--v-bg-1": (0.215, 0.008, 250),
    "--v-ink": (0.915, 0.005, 250),
    "--v-ink-520": (0.520, 0.010, 250),
    "--v-agent": (0.760, 0.130, 330),
}


def oklch_to_srgb(lightness, chroma, hue_deg):
    """oklch(L C H) -> an (r, g, b) triple of 0-255 ints.

    Ottosson's transform: polar to OKLab, OKLab to a cone response, cube it,
    that to linear sRGB, then the sRGB transfer curve. Out-of-gamut channels
    are clamped, which none of the four tokens above needs.
    """
    hue = math.radians(hue_deg)
    a = chroma * math.cos(hue)
    b = chroma * math.sin(hue)

    l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_ = lightness - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_**3, m_**3, s_**3

    linear = (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )

    out = []
    for channel in linear:
        channel = max(0.0, min(1.0, channel))
        if channel <= 0.0031308:
            encoded = 12.92 * channel
        else:
            encoded = 1.055 * (channel ** (1 / 2.4)) - 0.055
        out.append(int(round(encoded * 255)))
    return tuple(out)


COLOUR = {name: oklch_to_srgb(*value) for name, value in TOKENS.items()}


# --- a canvas --------------------------------------------------------------


class Canvas:
    """A supersampled RGB buffer. Only two shapes, which is all the mark is."""

    def __init__(self, size, background):
        self.size = size * SS
        self.px = bytearray(background * (self.size * self.size))

    def rect(self, x0, y0, x1, y1, colour, scale):
        """A rectangle in viewBox units. Half-open, so edges never double up."""
        x0, x1 = int(round(x0 * scale)), int(round(x1 * scale))
        y0, y1 = int(round(y0 * scale)), int(round(y1 * scale))
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.size, x1), min(self.size, y1)
        for y in range(y0, y1):
            row = y * self.size
            self.px[(row + x0) * 3 : (row + x1) * 3] = colour * (x1 - x0)

    def disc(self, cx, cy, r, colour, scale):
        cx, cy, r = cx * scale, cy * scale, r * scale
        for y in range(max(0, int(cy - r)), min(self.size, int(cy + r) + 1)):
            dy = y + 0.5 - cy
            if abs(dy) > r:
                continue
            half = math.sqrt(r * r - dy * dy)
            x0 = max(0, int(round(cx - half)))
            x1 = min(self.size, int(round(cx + half)))
            row = y * self.size
            if x1 > x0:
                self.px[(row + x0) * 3 : (row + x1) * 3] = colour * (x1 - x0)

    def downsample(self, size):
        """Box filter. This is the whole antialiasing story."""
        out = bytearray(size * size * 3)
        area = SS * SS
        for y in range(size):
            for x in range(size):
                totals = [0, 0, 0]
                for sy in range(y * SS, (y + 1) * SS):
                    base = (sy * self.size + x * SS) * 3
                    for sx in range(SS):
                        off = base + sx * 3
                        totals[0] += self.px[off]
                        totals[1] += self.px[off + 1]
                        totals[2] += self.px[off + 2]
                off = (y * size + x) * 3
                out[off] = totals[0] // area
                out[off + 1] = totals[1] // area
                out[off + 2] = totals[2] // area
        return bytes(out)


def write_png(path, size, pixels):
    """A minimal PNG. Colour type 2, 8-bit, one IDAT, filter 0 on every row."""

    def chunk(kind, payload):
        body = kind + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))

    stride = size * 3
    raw = b"".join(b"\x00" + pixels[y * stride : (y + 1) * stride] for y in range(size))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


# --- the two drawings ------------------------------------------------------
#
# Each bracket below is the union of three rectangles rather than a stroked
# path. A stroke of width w on a polyline with a miter join is exactly that
# union, and a union of rectangles is something this file can draw.


def draw_favicon_mark(canvas, ink):
    """design/assets/favicon.svg. A 16 unit mark, strokes at 1.5."""
    scale = canvas.size / 18  # an 18 unit box. See ROOM FOR THE DOT.
    h = 0.75  # half the stroke

    # left bracket: M5.5 3 H2.5 V13 H5.5
    canvas.rect(2.5 - h, 3 - h, 5.5, 3 + h, ink, scale)
    canvas.rect(2.5 - h, 3 - h, 2.5 + h, 13 + h, ink, scale)
    canvas.rect(2.5 - h, 13 - h, 5.5, 13 + h, ink, scale)

    # right bracket: M10.5 3 H13.5 V13 H10.5
    canvas.rect(10.5, 3 - h, 13.5 + h, 3 + h, ink, scale)
    canvas.rect(13.5 - h, 3 - h, 13.5 + h, 13 + h, ink, scale)
    canvas.rect(10.5, 13 - h, 13.5 + h, 13 + h, ink, scale)

    # the bar it holds
    canvas.rect(7, 3, 9, 13, ink, scale)


def draw_full_mark(canvas, ink):
    """design/assets/mark.svg. A 32 unit mark, strokes at 3."""
    scale = canvas.size / 36  # a 36 unit box. See ROOM FOR THE DOT.
    h = 1.5

    # left bracket: M11 6 H5 V26 H11
    canvas.rect(5 - h, 6 - h, 11, 6 + h, ink, scale)
    canvas.rect(5 - h, 6 - h, 5 + h, 26 + h, ink, scale)
    canvas.rect(5 - h, 26 - h, 11, 26 + h, ink, scale)

    # right bracket: M21 6 H27 V26 H21
    canvas.rect(21, 6 - h, 27 + h, 6 + h, ink, scale)
    canvas.rect(27 - h, 6 - h, 27 + h, 26 + h, ink, scale)
    canvas.rect(21, 26 - h, 27 + h, 26 + h, ink, scale)

    # the bar it holds
    canvas.rect(13.5, 6, 18.5, 26, ink, scale)


def draw_dot(canvas, tile):
    """The rose dot. Drawn here, never in design/assets/ -- favicon.svg says so.

    The artboard puts it at right:-2px bottom:-2px of a 16px mark: 7px across,
    hanging off the corner rather than sitting on the brackets. A PNG cannot
    hang off anything, which is what ROOM FOR THE DOT is for -- the mark is
    already inset, so the same geometry lands in free space.

    Given in fractions of the box, so it is the same dot at every size. On the
    18 unit box that is a centre of 14.5 and a radius of 3.5, exactly the
    artboard. The ring of tile colour is the artboard's 1.5px border, which it
    needs for the same reason: the dot has to read as a dot.
    """
    canvas.disc(14.5 / 18, 14.5 / 18, 3.5 / 18, COLOUR["--v-agent"], canvas.size)


def ring_for_dot(canvas, tile):
    canvas.disc(14.5 / 18, 14.5 / 18, 4.6 / 18, tile, canvas.size)


def build(size, awake, dot):
    tile = bytes(COLOUR["--v-bg-1"])
    ink = bytes(COLOUR["--v-ink"] if awake else COLOUR["--v-ink-520"])
    canvas = Canvas(size, tile)
    if size <= 16:
        draw_favicon_mark(canvas, ink)
    else:
        draw_full_mark(canvas, ink)
    if dot:
        ring_for_dot(canvas, tile)
        draw_dot(canvas, tile)
    return canvas.downsample(size)


def main():
    ICONS.mkdir(exist_ok=True)
    for size in (16, 32, 48, 128):
        write_png(ICONS / f"icon-{size}.png", size, build(size, awake=False, dot=False))
        write_png(ICONS / f"icon-on-{size}.png", size, build(size, awake=True, dot=True))

    print("tokens, converted from design/tokens.css:")
    for name, rgb in COLOUR.items():
        print("  %-14s #%02x%02x%02x" % (name, *rgb))
    print(f"wrote 8 files to {ICONS}")


if __name__ == "__main__":
    main()
