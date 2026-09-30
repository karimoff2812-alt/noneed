"""Magazine-style card layout: asymmetric composition, an organic hand-drawn
looking floral illustration, generous whitespace and editorial typography -
the deliberate opposite of a centered, symmetric "quote card" template."""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

from . import engine, layout

FONT_DIR = __file__.rsplit("/", 1)[0] + "/fonts"

SERIF_DISPLAY = f"{FONT_DIR}/Italiana-Regular.ttf"
SERIF_HEADLINE = f"{FONT_DIR}/Lora-Regular.ttf"
SERIF_BODY_ITALIC = f"{FONT_DIR}/CrimsonPro-Italic.ttf"
SANS_LABEL = f"{FONT_DIR}/Outfit-Regular.ttf"
SANS_LABEL_BOLD = f"{FONT_DIR}/Outfit-Bold.ttf"


PALETTES = {
    "blush": {
        "bg_stops": [(0.0, (250, 236, 230)), (0.55, (246, 224, 216)), (1.0, (238, 210, 203))],
        "ink": (58, 34, 32), "accent": (176, 122, 96), "muted": (150, 118, 108),
        "stem": (150, 110, 85), "leaf": (150, 168, 122),
        "petals": [(205, 128, 123), (222, 160, 152), (180, 92, 92), (233, 190, 170)],
        "petal_center": (196, 148, 78), "dot": (196, 148, 78),
        "grain": 4, "bouquet_blur": False,
    },
    "sage": {
        "bg_stops": [(0.0, (240, 240, 226)), (0.55, (228, 232, 212)), (1.0, (210, 218, 194))],
        "ink": (46, 52, 36), "accent": (120, 132, 82), "muted": (110, 118, 92),
        "stem": (108, 120, 78), "leaf": (128, 148, 92),
        "petals": [(230, 224, 190), (198, 208, 160), (170, 188, 140), (240, 236, 214)],
        "petal_center": (188, 150, 76), "dot": (188, 150, 76),
        "grain": 4, "bouquet_blur": False,
    },
    "charcoal_gold": {
        "bg_stops": [(0.0, (30, 29, 34)), (0.55, (24, 24, 29)), (1.0, (16, 16, 20))],
        "ink": (240, 235, 224), "accent": (196, 160, 100), "muted": (168, 156, 138),
        "stem": (150, 122, 80), "leaf": (110, 120, 92),
        "petals": [(196, 160, 100), (150, 122, 80), (222, 196, 150), (110, 96, 70)],
        "petal_center": (222, 196, 150), "dot": (222, 196, 150),
        "grain": 7, "bouquet_blur": True,
    },
    "teal_gold": {
        "bg_stops": [(0.0, (16, 40, 42)), (0.55, (12, 32, 34)), (1.0, (8, 22, 24))],
        "ink": (238, 232, 216), "accent": (206, 168, 100), "muted": (170, 176, 160),
        "stem": (150, 130, 80), "leaf": (110, 150, 130),
        "petals": [(206, 168, 100), (150, 178, 160), (110, 96, 70), (224, 200, 150)],
        "petal_center": (224, 200, 150), "dot": (224, 200, 150),
        "grain": 6, "bouquet_blur": True,
    },
    "lavender": {
        "bg_stops": [(0.0, (240, 234, 244)), (0.55, (230, 222, 240)), (1.0, (216, 206, 232))],
        "ink": (48, 40, 58), "accent": (140, 110, 160), "muted": (120, 106, 138),
        "stem": (130, 108, 140), "leaf": (140, 150, 110),
        "petals": [(196, 170, 210), (216, 196, 226), (162, 128, 182), (236, 224, 240)],
        "petal_center": (200, 160, 90), "dot": (200, 160, 90),
        "grain": 4, "bouquet_blur": False,
    },
}


def _petal(size, color, alpha, outline):
    """A teardrop petal (round tip, pointed base) reads as a flower petal far
    more clearly than a plain ellipse."""
    w, h = size
    ss = 3
    tile = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    W, H = w * ss, h * ss
    d.pieslice([0, 0, W, H * 2], 180, 360, fill=(*color, alpha))
    d.polygon([(W * 0.5, H), (0, H * 0.5), (W, H * 0.5)], fill=(*color, alpha))
    if outline:
        d.arc([0, 0, W, H * 2], 180, 360, fill=(*outline, min(255, alpha + 40)), width=max(1, ss))
        d.line([(W * 0.5, H), (0, H * 0.5)], fill=(*outline, min(255, alpha + 40)), width=max(1, ss))
        d.line([(W * 0.5, H), (W, H * 0.5)], fill=(*outline, min(255, alpha + 40)), width=max(1, ss))
    return tile.resize((w, h), Image.LANCZOS)


def _draw_flower(layer, cx, cy, r, petal_colors, center_color, rng, petals=5, alpha=225):
    base_angle = rng.uniform(0, 60)
    outline = tuple(max(0, c - 40) for c in petal_colors[0])
    for i in range(petals):
        a = base_angle + (360 / petals) * i + rng.uniform(-5, 5)
        rad = math.radians(a - 90)
        dist = r * rng.uniform(0.5, 0.58)
        px, py = cx + math.cos(rad) * dist, cy + math.sin(rad) * dist
        pw, ph = r * rng.uniform(0.62, 0.74), r * rng.uniform(0.88, 1.02)
        color = rng.choice(petal_colors)
        petal = _petal((int(pw), int(ph)), color, alpha, outline)
        petal = petal.rotate(-a, expand=True, resample=Image.BICUBIC)
        layer.alpha_composite(petal, (int(px - petal.width / 2), int(py - petal.height / 2)))
    d = ImageDraw.Draw(layer)
    cr = r * 0.16
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(*center_color, 255))
    for i in range(7):
        a = math.tau / 7 * i
        dx, dy = math.cos(a) * cr * 0.55, math.sin(a) * cr * 0.55
        d.ellipse([cx + dx - 1.4, cy + dy - 1.4, cx + dx + 1.4, cy + dy + 1.4], fill=(*outline, 200))


def _draw_leaf(layer, x0, y0, x1, y1, width, color, alpha=190):
    d = ImageDraw.Draw(layer)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    bulge = width
    pts = [(x0, y0), (mx + nx * bulge, my + ny * bulge), (x1, y1), (mx - nx * bulge, my - ny * bulge)]
    d.polygon(pts, fill=(*color, alpha))


def draw_bouquet(size, palette, seed=None, anchor="bl", scale=1.0):
    """Returns an RGBA layer with an asymmetric floral illustration anchored
    to one corner - stems rising from a base point, a few detached petals
    drifting above for movement."""
    rng = random.Random(seed)
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    if anchor == "bl":
        base = (w * -0.04, h * 1.04)
        spread = 1
    else:
        base = (w * 1.04, h * 1.04)
        spread = -1

    n_flowers = 5
    targets = []
    for i in range(n_flowers):
        t = i / (n_flowers - 1)
        x = base[0] + spread * (w * (0.14 + 0.4 * t)) * scale
        y = base[1] - (h * (0.08 + 0.44 * t)) * scale
        targets.append((x, y))

    stem_color = palette["stem"]
    for (tx, ty) in targets:
        mx = (base[0] + tx) / 2 + rng.uniform(-w * 0.03, w * 0.03)
        my = (base[1] + ty) / 2
        d.line([base, (mx, my), (tx, ty)], fill=(*stem_color, 200), width=max(2, int(w * 0.0028)), joint="curve")
        leaf_t = rng.uniform(0.35, 0.6)
        lx = base[0] + (tx - base[0]) * leaf_t
        ly = base[1] + (ty - base[1]) * leaf_t
        _draw_leaf(layer, lx, ly, lx + spread * w * 0.05, ly - h * 0.02, w * 0.014, palette["leaf"])

    sizes = [0.085, 0.11, 0.075, 0.13, 0.095]
    for (tx, ty), s in zip(targets, sizes):
        _draw_flower(layer, tx, ty, h * s * scale, palette["petals"], palette["petal_center"], rng)

    for _ in range(9):
        px = base[0] + spread * w * rng.uniform(0.05, 0.62)
        py = base[1] - h * rng.uniform(0.12, 0.78)
        s = h * rng.uniform(0.014, 0.024)
        color = rng.choice(palette["petals"])
        petal = _petal((int(s * 1.3), int(s * 2)), color, rng.randint(110, 190), None)
        petal = petal.rotate(rng.uniform(0, 360), expand=True, resample=Image.BICUBIC)
        layer.alpha_composite(petal, (int(px - petal.width / 2), int(py - petal.height / 2)))

    for _ in range(6):
        px = base[0] + spread * w * rng.uniform(0.08, 0.55)
        py = base[1] - h * rng.uniform(0.1, 0.7)
        r = rng.uniform(1.5, 3) * (w / 1080)
        d.ellipse([px - r, py - r, px + r, py + r], fill=(*palette["dot"], rng.randint(120, 200)))

    return layer


def _thin_arcs(size, color, seed=None, corner="tr"):
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if corner == "tr":
        cx, cy, a0, a1 = w * 1.05, h * -0.02, 140, 230
    else:
        cx, cy, a0, a1 = w * -0.05, h * -0.02, -50, 40
    for i, r in enumerate([0.22, 0.3, 0.38]):
        rr = h * r
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1, fill=(*color, 150 - i * 25), width=2)
    return layer


def _text_block(draw, size, edge_x, top_y, eyebrow, headline, body, tagline, ink, accent, muted, align="right"):
    """align='right': block hugs edge_x from the left (text ends at edge_x) -
    pairs with a bottom-left bouquet. align='left': mirrored, block starts at
    edge_x - pairs with a bottom-right bouquet so text and illustration never
    fight over the same corner."""
    w, h = size
    right = align == "right"
    anchor_h = "r" if right else "l"

    def draw_line(txt, font, color, y):
        tw = draw.textlength(txt, font=font)
        x = edge_x - tw if right else edge_x
        draw.text((x, y), txt, font=font, fill=color)
        return tw

    def rule(y, rule_w):
        x0 = edge_x - rule_w if right else edge_x
        x1 = edge_x if right else edge_x + rule_w
        draw.line([(x0, y), (x1, y)], fill=(*accent, 200), width=2)

    # Font sizes and vertical rhythm are based on w (the wrap-width axis),
    # not h - the two card formats share the same width (1080) but differ a
    # lot in height, so sizing off h made portrait status images render with
    # oversized, overlapping text.
    u = w
    y = top_y
    if eyebrow:
        ef = layout.load_font(SANS_LABEL_BOLD, int(u * 0.0165))
        tw = layout.draw_tracked_text(draw, (edge_x, y), eyebrow, ef, (*accent, 255),
                                       tracking=int(u * 0.0045), anchor_h=anchor_h)
        y += u * 0.028
        rule(y, min(tw, w * 0.16))
        y += u * 0.045

    if headline:
        hf = layout.load_font(SERIF_DISPLAY, int(u * 0.078))
        lines = layout.wrap_to_width(draw, headline, hf, w * 0.62)
        hl_h = hf.getbbox("Ag")[3] * 1.2
        for ln in lines:
            draw_line(ln, hf, (*ink, 255), y)
            y += hl_h
        y += u * 0.012

    if body:
        bf_size = int(u * 0.032)
        bf = layout.load_font(SERIF_BODY_ITALIC, bf_size)
        max_w = w * 0.55
        lines = layout.wrap_to_width(draw, body, bf, max_w)
        while len(lines) > 5 and bf_size > int(u * 0.022):
            bf_size -= 2
            bf = layout.load_font(SERIF_BODY_ITALIC, bf_size)
            lines = layout.wrap_to_width(draw, body, bf, max_w)
        line_h = bf.getbbox("Ag")[3] * 1.42
        for ln in lines:
            draw_line(ln, bf, (*ink, 235), y)
            y += line_h
        y += u * 0.022

    if tagline:
        y += u * 0.008
        tf = layout.load_font(SANS_LABEL, int(u * 0.0145))
        tw = layout.draw_tracked_text(draw, (edge_x, y), tagline, tf, (*muted, 255),
                                       tracking=int(u * 0.003), anchor_h=anchor_h)
        rule(y - u * 0.016, min(tw, w * 0.12))
        y += u * 0.03

    return y


def compose_editorial(text, author=None, palette=None, size=(1080, 1350), seed=None,
                       eyebrow="TABRIK", headline=None, tagline=None,
                       footer="Kichkina tabib • t.me/yordamchiagent1_bot", anchor="bl"):
    rng = random.Random(seed)
    w, h = size
    bg = engine.multi_stop_gradient(size, palette["bg_stops"], angle=100)
    bg = engine.add_film_grain(bg, amount=palette.get("grain", 4), seed=seed)
    base = bg.convert("RGBA")

    bouquet = draw_bouquet(size, palette, seed=seed, anchor=anchor)
    if palette.get("bouquet_blur"):
        bouquet = bouquet.filter(ImageFilter.GaussianBlur(0.6))
    base.alpha_composite(bouquet)

    arcs = _thin_arcs(size, palette["accent"], seed=seed, corner=("tr" if anchor == "bl" else "tl"))
    base.alpha_composite(arcs)

    d = ImageDraw.Draw(base)
    margin = int(min(w, h) * 0.055)
    d.rectangle([margin, margin, w - margin, h - margin], outline=(*palette["accent"], 130), width=1)

    align = "right" if anchor == "bl" else "left"
    edge_x = (w - margin - int(w * 0.045)) if align == "right" else (margin + int(w * 0.045))
    top_y = h * 0.085
    _text_block(
        d, size, edge_x, top_y,
        eyebrow, headline, text, tagline,
        palette["ink"], palette["accent"], palette["muted"], align=align,
    )

    if author:
        af = layout.load_font(SANS_LABEL_BOLD, int(w * 0.0155))
        ay = h * 0.9
        anchor_h = "r" if align == "right" else "l"
        tw = layout.draw_tracked_text(d, (edge_x, ay), author.upper(), af, (*palette["ink"], 230),
                                       tracking=int(w * 0.003), anchor_h=anchor_h)
        rx0 = edge_x - tw if align == "right" else edge_x
        rx1 = edge_x if align == "right" else edge_x + tw
        d.line([(rx0, ay - h * 0.014), (rx1, ay - h * 0.014)], fill=(*palette["accent"], 200), width=1)

    if footer:
        ff = layout.load_font(SANS_LABEL, int(w * 0.0135))
        d.text((w / 2, h * 0.965), footer, font=ff, fill=(*palette["muted"], 200), anchor="mm")

    return base.convert("RGB")
