#!/usr/bin/env python3
"""Draw entry.html's front page offline with Pillow and system fonts only.

Coordinates use the final 1024-pixel page. Supersampling smooths the primitive
illustrations and type. Measured text boxes wrap at words and reject overflow.
"""

import hashlib
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "entry.png"
SIZE, SCALE = 1024, 2
PAPER, INK, MUTED, RULE, WHITE = "#f5f2e9", "#192b32", "#526168", "#d5d5cb", "#fcfbf6"
FONTS = {
    "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "sans-bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
}


@lru_cache(maxsize=None)
def font(size, face="bold"):
    return ImageFont.truetype(FONTS[face], round(size * SCALE))


class Page:
    def __init__(self):
        self.image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text_boxes = []

    @staticmethod
    def coords(values):
        return tuple(round(value * SCALE) for value in values)

    def rect(self, box, fill, outline=None, width=1, radius=0):
        if radius:
            self.draw.rounded_rectangle(self.coords(box), round(radius * SCALE),
                                        fill=fill, outline=outline, width=round(width * SCALE))
        else:
            self.draw.rectangle(self.coords(box), fill=fill, outline=outline,
                                width=round(width * SCALE))

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.draw.ellipse(self.coords(box), fill=fill, outline=outline, width=round(width * SCALE))

    def line(self, points, fill, width=1):
        self.draw.line([self.coords(p) for p in points], fill=fill,
                       width=round(width * SCALE), joint="curve")

    def polygon(self, points, fill):
        self.draw.polygon([self.coords(p) for p in points], fill=fill)

    def arc(self, box, start, end, fill, width=1):
        self.draw.arc(self.coords(box), start, end, fill=fill, width=round(width * SCALE))

    def text(self, value, box, size, face="bold", color=INK, leading=None, align="left"):
        """Wrap at words, preserve explicit newlines, and validate visible bounds."""
        x, y, width, height = box
        selected = font(size, face)
        leading = leading or size * 1.25
        lines = []
        for paragraph in value.split("\n"):
            current = ""
            for word in paragraph.split():
                if selected.getlength(word) > width * SCALE:
                    raise ValueError(f"Word too wide for text box: {word!r}")
                candidate = f"{current} {word}" if current else word
                if selected.getlength(candidate) <= width * SCALE:
                    current = candidate
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
        for index, line in enumerate(lines):
            bounds = selected.getbbox(line)
            line_width = (bounds[2] - bounds[0]) / SCALE
            line_height = (bounds[3] - bounds[1]) / SCALE
            line_y = y + index * leading
            if line_width > width or line_y + line_height > y + height:
                raise ValueError(f"Text overflows text box: {value!r}")
            line_x = x
            if align == "center":
                line_x += (width - line_width) / 2
            elif align == "right":
                line_x += width - line_width
            position = (round(line_x * SCALE) - bounds[0], round(line_y * SCALE) - bounds[1])
            self.draw.text(position, line, font=selected, fill=color)
            self.text_boxes.append((line, line_x, line_y, line_width, line_height))

    def check_text(self):
        for index, (label, x, y, width, height) in enumerate(self.text_boxes):
            if x < 0 or y < 0 or x + width > SIZE or y + height > SIZE:
                raise ValueError(f"Text leaves page: {label!r}")
            for other, ox, oy, ow, oh in self.text_boxes[index + 1:]:
                if x < ox + ow and ox < x + width and y < oy + oh and oy < y + height:
                    raise ValueError(f"Overlapping text: {label!r} / {other!r}")


def globe(page, x, y, radius, color, width=2):
    page.ellipse((x - radius, y - radius, x + radius, y + radius), outline=color, width=width)
    page.ellipse((x - radius * .45, y - radius, x + radius * .45, y + radius),
                 outline=color, width=width)
    page.line([(x - radius, y), (x + radius, y)], color, width)
    page.line([(x, y - radius), (x, y + radius)], color, width)
    for direction in (-1, 1):
        points = [(x + radius * t, y + direction * radius * (.35 + .22 * t * t))
                  for t in [i / 20 for i in range(-16, 17)]]
        page.line(points, color, width)


def chip(page, x, y, color, background):
    for py in (25, 39, 53, 67, 81):
        page.line([(x + 1, y + py), (x + 13, y + py)], color, 3)
        page.line([(x + 109, y + py), (x + 121, y + py)], color, 3)
    for px in (28, 44, 60, 76, 92):
        page.line([(x + px, y + 1), (x + px, y + 13)], color, 3)
        page.line([(x + px, y + 94), (x + px, y + 106)], color, 3)
    page.rect((x + 13, y + 13, x + 109, y + 94), color, radius=4)
    page.rect((x + 22, y + 22, x + 100, y + 85), background, radius=2)
    page.text("NVIDIA", (x + 22, y + 34, 78, 15), 12, color=color, align="center")
    for px, py in ((37, 67), (55, 59), (73, 50)):
        page.rect((x + px, y + py, x + px + 10, y + 77), color)


def star(page, x, y, radius, color):
    points = []
    for index in range(10):
        angle = -math.pi / 2 + index * math.pi / 5
        length = radius if index % 2 == 0 else radius * .42
        points.append((x + math.cos(angle) * length, y + math.sin(angle) * length))
    page.polygon(points, color)


def journey(page, x, y, color):
    blue, red, light, gold = "#345a83", "#ae5655", "#fffdf8", "#c5a141"
    globe(page, x + 67, y + 53, 45, "#c1d0da", 1.4)
    plane = [(12, 58), (50, 48), (44, 15), (53, 12), (70, 44), (106, 36),
             (121, 36), (127, 42), (123, 46), (75, 60), (60, 98), (50, 101),
             (53, 67), (30, 73), (19, 87), (11, 89), (16, 68), (9, 64)]
    page.polygon([(x + px, y + py) for px, py in plane], color)
    for index in range(0, 21, 3):
        t = index / 20
        px, py = x + 129 + 56 * t, y + 31 - 60 * t * (1 - t)
        page.ellipse((px - 1, py - 1, px + 1, py + 1), fill=color)
    page.ellipse((x + 182, y + 28, x + 188, y + 34), fill=color)
    page.text("MANILA", (x + 199, y + 9, 127, 27), 24, "sans-bold")
    page.text("Philippines", (x + 200, y + 36, 125, 18), 14, "sans", MUTED)
    fx, fy = x + 333, y + 4
    page.rect((fx, fy, fx + 80, fy + 21), blue)
    page.rect((fx, fy + 21, fx + 80, fy + 42), red)
    page.polygon([(fx, fy), (fx + 36, fy + 21), (fx, fy + 42)], light)
    page.ellipse((fx + 8, fy + 17, fx + 16, fy + 25), fill=gold)
    for angle in range(0, 360, 45):
        theta = math.radians(angle)
        page.line([(fx + 12, fy + 21),
                   (fx + 12 + 8 * math.cos(theta), fy + 21 + 8 * math.sin(theta))], gold, 1.4)
    for px, py in ((5, 7), (5, 35), (28, 21)):
        star(page, fx + px, fy + py, 4, gold)
    for offset, country in ((199, "INDIA"), (276, "JAPAN"), (353, "AUSTRALIA")):
        fx, fy = x + offset, y + 64
        if country == "INDIA":
            page.rect((fx, fy, fx + 54, fy + 9), "#d79a56")
            page.rect((fx, fy + 9, fx + 54, fy + 18), light)
            page.rect((fx, fy + 18, fx + 54, fy + 27), "#567660")
            page.ellipse((fx + 23.5, fy + 10, fx + 30.5, fy + 17), outline=blue)
            page.line([(fx + 23.5, fy + 13.5), (fx + 30.5, fy + 13.5)], blue, .7)
            page.line([(fx + 27, fy + 10), (fx + 27, fy + 17)], blue, .7)
        elif country == "JAPAN":
            page.rect((fx, fy, fx + 54, fy + 27), light, "#c6d3db")
            page.ellipse((fx + 20, fy + 6.5, fx + 34, fy + 20.5), fill=red)
        else:
            page.rect((fx, fy, fx + 54, fy + 27), blue)
            page.line([(fx, fy), (fx + 23, fy + 13)], light, 3)
            page.line([(fx, fy + 13), (fx + 23, fy)], light, 3)
            page.line([(fx + 11.5, fy), (fx + 11.5, fy + 13)], light, 5)
            page.line([(fx, fy + 6.5), (fx + 23, fy + 6.5)], light, 5)
            page.line([(fx + 11.5, fy), (fx + 11.5, fy + 13)], red, 2)
            page.line([(fx, fy + 6.5), (fx + 23, fy + 6.5)], red, 2)
            for px, py, radius in ((11, 21, 4), (38, 7, 3), (45, 15, 3), (32, 16, 3), (38, 24, 3)):
                star(page, fx + px, fy + py, radius, light)
        page.text(country, (fx - 7, fy + 33, 68, 14), 11.5, "sans-bold", align="center")


def waves(page, x, y, color, rows=(99, 107)):
    for row in rows:
        page.line([(x + px, y + row - 2.5 * math.sin((px - 10) * math.pi / 24))
                   for px in range(10, 107)], color, 1.3)


def bridge(page, x, y, color):
    page.ellipse((x + 9, y + 6, x + 103, y + 100), fill="#f3ecdf")
    page.line([(x + 7, y + 63), (x + 43, y + 63), (x + 47, y + 68),
               (x + 42, y + 72), (x + 7, y + 72)], color, 5)
    for py in (63, 72):
        page.line([(x + 76, y + py), (x + 105, y + py)], color, 5)
    for px in (22, 90):
        page.line([(x + px, y + 72), (x + px, y + 96)], color, 5)
    page.line([(x + 53, y + 76), (x + 66, y + 84)], color, 6)
    waves(page, x, y, color)
    for px, py in ((10, 10), (16, 16), (22, 22)):
        page.line([(x + px, y + py), (x + px + 2, y + py + 2)], color, 1.5)
    angle = math.radians(43)
    def rotate(points):
        return [(x + 27 + px * math.cos(angle) - py * math.sin(angle),
                 y + 22 + px * math.sin(angle) + py * math.cos(angle)) for px, py in points]
    page.polygon(rotate([(0, 0), (31, 0), (42, 4), (31, 8), (0, 8), (4, 4)]), color)
    page.polygon(rotate([(16, 0), (11, -7), (23, 0)]), color)
    page.polygon(rotate([(16, 8), (11, 15), (23, 8)]), color)


def radar(page, x, y, color):
    page.ellipse((x + 11, y + 2, x + 101, y + 92), fill="#f4e8e2")
    page.line([(x + 26, y + 76), (x + 37, y + 54), (x + 49, y + 76)], color, 3.5)
    page.line([(x + 19, y + 77), (x + 57, y + 77)], color, 3.5)
    dish = [(19, 35), (17, 47), (22, 58), (38, 64), (50, 60), (59, 51)]
    page.polygon([(x + px, y + py) for px, py in dish], "#e4c7bc")
    page.line([(x + px, y + py) for px, py in dish + [dish[0]]], color, 2.5)
    page.line([(x + 41, y + 52), (x + 61, y + 31)], color, 2)
    page.arc((x + 49, y + 24, x + 67, y + 57), -65, 35, color, 2)
    page.arc((x + 49, y + 15, x + 79, y + 65), -65, 35, color, 2)
    page.line([(x + 66, y + 15), (x + 91, y + 31)], color, 2.5)
    page.line([(x + 66, y + 31), (x + 91, y + 15)], color, 2.5)
    for px in (65, 92):
        for py in (14, 32):
            page.ellipse((x + px - 8, y + py - 3, x + px + 8, y + py + 3), outline=color, width=2)
    page.rect((x + 74, y + 17, x + 84, y + 30), color, radius=3)
    page.text("SHEIKH ISA AIR BASE", (x - 2, y + 89, 116, 13), 10.5, "sans-bold", align="center")
    page.text("BAHRAIN", (x, y + 103, 112, 13), 10, "sans-bold", align="center")


def sanctions(page, x, y, color):
    page.ellipse((x + 12, y + 4, x + 100, y + 92), fill="#eee9ef")
    angle = math.radians(-35)
    def block(box):
        left, top, right, bottom = box
        points = [(left, top), (right, top), (right, bottom), (left, bottom)]
        page.polygon([(x + 59 + px * math.cos(angle) - py * math.sin(angle),
                       y + 34 + px * math.sin(angle) + py * math.cos(angle)) for px, py in points], color)
    for box in ((-22, -16, 17, 7), (-26, -18, -20, 9), (15, -18, 21, 9), (-6, 5, 3, 45)):
        block(box)
    page.polygon([(x + 32, y + 76), (x + 81, y + 76), (x + 86, y + 84), (x + 27, y + 84)], color)
    page.rect((x + 3, y + 89, x + 109, y + 113), WHITE, color, 2)
    page.text("SANCTIONS", (x + 6, y + 96, 100, 14), 11, color=color, align="center")


def cyclone(page, x, y, color):
    page.ellipse((x + 9, y + 6, x + 103, y + 100), fill="#e6eff0")
    for rotation in (0, math.pi):
        points = []
        for index in range(121):
            t = index / 120
            angle, radius = -.92 + 4.5 * t + rotation, 50 - 34 * t
            points.append((x + 56 + radius * math.cos(angle), y + 53 + radius * math.sin(angle)))
        page.line(points, color, 9)
        for px, py in (points[0], points[-1]):
            page.ellipse((px - 4.5, py - 4.5, px + 4.5, py + 4.5), fill=color)
    page.ellipse((x + 46, y + 43, x + 66, y + 63), fill=color)
    page.ellipse((x + 51, y + 48, x + 61, y + 58), fill=WHITE)
    waves(page, x, y, color, rows=(106,))


def panel(page, x, y, height, color, background=WHITE, border=RULE):
    page.rect((x, y, x + 471, y + height - 1), background, border)
    page.rect((x, y, x + 471, y + 3), color)


def draw_page():
    page = Page()
    page.text("GLOBAL BRIEFING", (32, 22, 400, 15), 11)
    page.text("THE DAY IN ONE IMAGE", (592, 22, 400, 15), 11, align="right")
    page.text("WORLD NEWS", (29, 52, 861, 90), 100)
    globe(page, 944, 90, 38, INK)
    page.rect((32, 147, 991, 198), INK)
    page.text("WEDNESDAY 18 NOVEMBER 2026", (32, 157, 960, 39), 42, color=PAPER, align="center")

    green, blue = "#326b51", "#3b6689"
    panel(page, 32, 215, 309, green, "#edf3eb", "#c4d2c2")
    panel(page, 520, 215, 309, blue, "#edf2f5", "#c6d3db")
    page.text("BUSINESS • TECHNOLOGY", (52, 230, 432, 17), 11.5, color=green)
    page.text("NVIDIA’S RECORD\nQUARTER", (52, 259, 432, 70), 32, leading=34)
    chip(page, 52, 335, green, "#edf3eb")
    page.text("$115.8bn", (189, 337, 295, 58), 50)
    page.text("QUARTERLY REVENUE", (189, 395, 295, 18), 13, "sans", MUTED)
    page.text("+103% year on year", (189, 419, 295, 22), 18, color=green)
    page.text("First earnings after Jensen Huang resigned as CEO.", (52, 449, 432, 23), 17.5, "sans")
    page.text("Interim CEO: Colette Kress", (52, 477, 260, 18), 15, "sans-bold")
    page.text("Forecast: $130bn", (317, 477, 167, 18), 15, "sans-bold", align="right")
    page.text("Board has no plan to reinstate Huang as CEO.", (52, 498, 432, 18), 14.5, "sans", MUTED)

    page.text("DIPLOMACY • PHILIPPINES", (540, 230, 432, 17), 11.5, color=blue)
    page.text("TRUMP ARRIVES\nIN MANILA", (540, 259, 432, 70), 32, leading=34)
    journey(page, 540, 330, blue)
    page.text("Quad talks with India, Japan and Australia.", (540, 449, 432, 23), 17.5, "sans")
    page.text("US President Donald Trump", (540, 477, 432, 18), 15, "sans-bold")
    page.text("Ahead of China visit and APEC summit.", (540, 498, 432, 18), 14.5, "sans", MUTED)

    compact = [
        (32, 540, "#947341", "UKRAINE", "KERCH BRIDGE\nSPAN DESTROYED", bridge,
         "Ukraine’s Flamingo cruise missiles\nRoad span to occupied Crimea",
         "Russia pounds Kyiv bridges in return."),
        (520, 540, "#a65d4c", "IRAN • UNITED STATES", "GULF DRONE\nSTANDOFF", radar,
         "IRGC claims US radar hit.\nCENTCOM: intercepted; no damage or injuries.",
         "US jets strike IRGC missile site on Qeshm Island."),
        (32, 735, "#76617f", "UNITED KINGDOM", "UK SANCTIONS\n8 FIRMS", sanctions,
         "Illegal West Bank settlements", "Britain moves to protect the two-state solution."),
        (520, 735, "#387785", "INDIA • BAY OF BENGAL", "CYCLONE AKVAN\nINTENSIFIES", cyclone,
         "Over the Bay of Bengal", "Andhra Pradesh and Odisha on high alert."),
    ]
    for x, y, color, eyebrow, headline, illustration, note, summary in compact:
        panel(page, x, y, 179, color)
        illustration(page, x + 18, y + 20, color)
        page.text(eyebrow, (x + 147, y + 14, 310, 16), 11.5, color=color)
        page.text(headline, (x + 147, y + 35, 310, 60), 27, leading=29)
        page.text(note, (x + 147, y + 101, 310, 36), 14.5, "sans", MUTED, leading=17)
        page.text(summary, (x + 18, y + 142, 436, 25), 17.5, "sans")
        if illustration == cyclone:
            page.rect((x + 147, y + 123, x + 245, y + 140), None, "#9cb9bd")
            page.text("HIGH ALERT", (x + 152, y + 127, 89, 12), 10, color=color)

    page.line([(32, 931), (992, 931)], INK, 2)
    page.line([(379, 942), (379, 978)], "#c9cdc5")
    page.line([(726, 942), (726, 978)], "#c9cdc5")
    page.text("India: record 10th SAFF football title", (32, 943, 331, 18), 15, "sans-bold")
    page.text("Pakistan beaten 2-1", (32, 963, 331, 18), 15, "sans")
    page.text("MS Dhoni retires from the IPL", (398, 943, 312, 18), 15, "sans-bold")
    page.text("Becomes Chennai Super Kings mentor", (398, 963, 312, 18), 15, "sans")
    page.text("Grammy 2027", (745, 943, 247, 18), 15, "sans-bold")
    page.text("Nominations announced", (745, 963, 247, 18), 15, "sans")
    page.line([(32, 985), (992, 985)], "#c9cdc5")
    page.text("18 November 2026 — the day in one image", (32, 993, 960, 18),
              13, "sans", MUTED, align="center")
    page.check_text()
    return page.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main():
    draw_page().save(TARGET, format="PNG", optimize=True, compress_level=9)
    with Image.open(TARGET) as finished:
        assert finished.format == "PNG", "Output must be PNG"
        assert finished.size == (SIZE, SIZE), "Output must be 1024x1024"
        finished.verify()
    contents = TARGET.read_bytes()
    if len(contents) > 1_048_576:
        raise SystemExit(f"PNG exceeds 1 MiB: {len(contents)} bytes")
    print(f"entry.png: {len(contents)} bytes; 1024x1024; valid PNG")
    print(f"sha256: {hashlib.sha256(contents).hexdigest()}")


if __name__ == "__main__":
    main()
