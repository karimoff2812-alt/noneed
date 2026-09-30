"""Small line-art concept icons so a card can visually explain the phrase, not
just display it as text. Each icon is rendered into its own transparent tile
at high resolution then composited onto the card as a badge."""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

TILE = 400
SUPERSAMPLE = 3


def _canvas():
    n = TILE * SUPERSAMPLE
    return Image.new("RGBA", (n, n), (0, 0, 0, 0)), n


def _finish(tile):
    return tile.resize((TILE, TILE), Image.LANCZOS)


def _stroke_width(n, weight=1.0):
    return max(2, int(n * 0.028 * weight))


def icon_heart(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy, r = n / 2, n / 2, n * 0.34
    pts = []
    for t in range(0, 361, 4):
        a = math.radians(t)
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x / 16 * r, cy - y / 16 * r - r * 0.12))
    d.line(pts + [pts[0]], fill=color, width=_stroke_width(n), joint="curve")
    return _finish(tile)


def icon_knot(color):
    """Two interlocking rings - a bond kept (loyalty / va'da / friendship)."""
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    r = n * 0.19
    w = _stroke_width(n)
    d.ellipse([n * 0.5 - r * 2, n * 0.5 - r, n * 0.5, n * 0.5 + r], outline=color, width=w)
    d.ellipse([n * 0.5, n * 0.5 - r, n * 0.5 + r * 2, n * 0.5 + r], outline=color, width=w)
    return _finish(tile)


def icon_hourglass(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy, r = n / 2, n / 2, n * 0.28
    w = _stroke_width(n)
    top = [(cx - r, cy - r), (cx + r, cy - r), (cx, cy)]
    bot = [(cx - r, cy + r), (cx + r, cy + r), (cx, cy)]
    d.line(top + [top[0]], fill=color, width=w, joint="curve")
    d.line(bot + [bot[0]], fill=color, width=w, joint="curve")
    cap = r * 1.15
    d.line([(cx - cap, cy - r), (cx + cap, cy - r)], fill=color, width=w)
    d.line([(cx - cap, cy + r), (cx + cap, cy + r)], fill=color, width=w)
    d.ellipse([cx - n * 0.02, cy - n * 0.02, cx + n * 0.02, cy + n * 0.02], fill=color)
    return _finish(tile)


def icon_book(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy, r = n / 2, n / 2, n * 0.3
    w = _stroke_width(n)
    left = [(cx - r, cy - r * 0.62), (cx, cy - r * 0.18), (cx, cy + r * 0.82), (cx - r, cy + r * 0.42)]
    right = [(cx + r, cy - r * 0.62), (cx, cy - r * 0.18), (cx, cy + r * 0.82), (cx + r, cy + r * 0.42)]
    d.line(left + [left[0]], fill=color, width=w, joint="curve")
    d.line(right + [right[0]], fill=color, width=w, joint="curve")
    d.line([(cx, cy - r * 0.18), (cx, cy + r * 0.82)], fill=color, width=max(2, w - 2))
    return _finish(tile)


def icon_tree(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy, r = n / 2, n / 2, n * 0.27
    w = _stroke_width(n)
    d.line([(cx, cy + r * 1.3), (cx, cy + r * 0.15)], fill=color, width=w)
    d.ellipse([cx - r, cy - r * 1.15, cx + r, cy + r * 0.35], outline=color, width=w)
    return _finish(tile)


def icon_mountain_flag(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy, r = n / 2, n / 2, n * 0.3
    w = _stroke_width(n)
    base_y = cy + r * 0.55
    peak = (cx - r * 0.1, cy - r * 0.75)
    d.line([(cx - r, base_y), peak, (cx + r, base_y)], fill=color, width=w, joint="curve")
    pole_top = (peak[0], peak[1] - r * 0.55)
    d.line([peak, pole_top], fill=color, width=max(2, w - 2))
    d.polygon([pole_top, (pole_top[0] + r * 0.5, pole_top[1] + r * 0.16), (pole_top[0], pole_top[1] + r * 0.32)],
              fill=color)
    return _finish(tile)


def icon_crescent_star(color):
    tile, n = _canvas()
    r = n * 0.26
    cx, cy = n / 2, n / 2
    m1 = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m1).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    m2 = Image.new("L", (n, n), 0)
    off = r * 0.55
    ImageDraw.Draw(m2).ellipse([cx - r + off, cy - r, cx + r + off, cy + r], fill=255)
    crescent = ImageChops.subtract(m1, m2)
    solid = Image.new("RGBA", (n, n), (*color, 255))
    tile.paste(solid, (0, 0), crescent)
    d = ImageDraw.Draw(tile)
    _star(d, cx + r * 1.15, cy - r * 0.75, r * 0.32, color, points=4)
    return _finish(tile)


def icon_sun(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy, r = n / 2, n / 2, n * 0.19
    w = _stroke_width(n)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    for i in range(8):
        a = math.radians(i * 45)
        x0, y0 = cx + math.cos(a) * r * 1.35, cy + math.sin(a) * r * 1.35
        x1, y1 = cx + math.cos(a) * r * 1.75, cy + math.sin(a) * r * 1.75
        d.line([(x0, y0), (x1, y1)], fill=color, width=w)
    return _finish(tile)


def icon_gift(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy, r = n / 2, n / 2, n * 0.28
    w = _stroke_width(n)
    box = [cx - r, cy - r * 0.35, cx + r, cy + r]
    d.rectangle(box, outline=color, width=w)
    d.line([(cx - r, cy - r * 0.05), (cx + r, cy - r * 0.05)], fill=color, width=w)
    d.line([(cx, cy - r * 0.35), (cx, cy + r)], fill=color, width=w)
    loop_r = r * 0.32
    d.ellipse([cx - loop_r * 1.8, cy - r * 0.35 - loop_r * 1.5, cx - loop_r * 0.2, cy - r * 0.35 + loop_r * 0.2],
              outline=color, width=max(2, w - 2))
    d.ellipse([cx + loop_r * 0.2, cy - r * 0.35 - loop_r * 1.5, cx + loop_r * 1.8, cy - r * 0.35 + loop_r * 0.2],
              outline=color, width=max(2, w - 2))
    return _finish(tile)


def icon_confetti_star(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy = n / 2, n / 2
    _star(d, cx, cy, n * 0.24, color, points=5)
    import random
    rng = random.Random(7)
    for _ in range(10):
        a = rng.uniform(0, math.tau)
        dist = rng.uniform(n * 0.32, n * 0.46)
        x, y = cx + math.cos(a) * dist, cy + math.sin(a) * dist
        s = rng.uniform(n * 0.018, n * 0.032)
        if rng.random() < 0.5:
            d.ellipse([x - s, y - s, x + s, y + s], fill=color)
        else:
            d.rectangle([x - s, y - s, x + s, y + s], fill=color)
    return _finish(tile)


def icon_cake(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy, r = n / 2, n / 2, n * 0.3
    w = _stroke_width(n)
    plate_y = cy + r * 0.95
    d.line([(cx - r * 1.15, plate_y), (cx + r * 1.15, plate_y)], fill=color, width=w)
    bt_top, bt_bot = cy + r * 0.28, plate_y
    d.rounded_rectangle([cx - r * 0.95, bt_top, cx + r * 0.95, bt_bot], radius=r * 0.1, outline=color, width=w)
    tt_top, tt_bot = cy - r * 0.32, bt_top
    d.rounded_rectangle([cx - r * 0.55, tt_top, cx + r * 0.55, tt_bot], radius=r * 0.08, outline=color, width=w)
    thin = max(2, w - 2)
    for i in range(-2, 3):
        x = cx + i * r * 0.22
        d.arc([x - r * 0.12, tt_top - r * 0.1, x + r * 0.12, tt_top + r * 0.14], 180, 360, fill=color, width=thin)
    candle_top = tt_top - r * 0.5
    d.line([(cx, tt_top), (cx, candle_top)], fill=color, width=thin)
    fr = r * 0.1
    d.ellipse([cx - fr, candle_top - fr * 2.1, cx + fr, candle_top], fill=color)
    return _finish(tile)


def _flower(d, cx, cy, r, color, petals=6):
    w = max(2, int(r * 0.16))
    for i in range(petals):
        a = math.tau / petals * i
        px, py = cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6
        d.ellipse([px - r * 0.34, py - r * 0.34, px + r * 0.34, py + r * 0.34], outline=color, width=w)
    d.ellipse([cx - r * 0.22, cy - r * 0.22, cx + r * 0.22, cy + r * 0.22], fill=color)


def icon_flowers(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy = n / 2, n / 2 + n * 0.06
    w = max(2, _stroke_width(n) - 1)
    base_y = cy + n * 0.28
    stems = [(-n * 0.11, cy + n * 0.03), (n * 0.12, cy - n * 0.02), (0, cy - n * 0.12)]
    for sx, sy in stems:
        d.line([(cx, base_y), (cx + sx, sy)], fill=color, width=w, joint="curve")
    _flower(d, cx - n * 0.11, cy + n * 0.03 - n * 0.05, n * 0.1, color)
    _flower(d, cx + n * 0.12, cy - n * 0.02 - n * 0.05, n * 0.1, color)
    _flower(d, cx, cy - n * 0.12 - n * 0.05, n * 0.12, color)
    return _finish(tile)


def icon_firework(color):
    tile, n = _canvas()
    d = ImageDraw.Draw(tile)
    cx, cy = n / 2, n / 2
    w = max(2, int(n * 0.02))
    for i in range(10):
        a = math.tau / 10 * i
        r1 = n * 0.09
        r2 = n * (0.3 if i % 2 == 0 else 0.21)
        x0, y0 = cx + math.cos(a) * r1, cy + math.sin(a) * r1
        x1, y1 = cx + math.cos(a) * r2, cy + math.sin(a) * r2
        d.line([(x0, y0), (x1, y1)], fill=color, width=w)
        d.ellipse([x1 - w, y1 - w, x1 + w, y1 + w], fill=color)
    d.ellipse([cx - n * 0.025, cy - n * 0.025, cx + n * 0.025, cy + n * 0.025], fill=color)
    return _finish(tile)


def _star(draw, cx, cy, r, color, points=5):
    pts = []
    for i in range(points * 2):
        a = math.pi / points * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    draw.polygon(pts, fill=color)


_BUILDERS = {
    "heart": icon_heart,
    "knot": icon_knot,
    "hourglass": icon_hourglass,
    "book": icon_book,
    "tree": icon_tree,
    "mountain_flag": icon_mountain_flag,
    "crescent_star": icon_crescent_star,
    "sun": icon_sun,
    "gift": icon_gift,
    "confetti_star": icon_confetti_star,
    "cake": icon_cake,
    "flowers": icon_flowers,
    "firework": icon_firework,
}

# Ordered so the first keyword match wins when a phrase touches several themes.
_KEYWORD_MAP = [
    ("cake", ("tug'ilgan kun", "tug'ilgan kuningiz", "tavallud", "yosh kuningiz")),
    ("gift", ("muborak bo'lsin", "sovg'a")),
    ("crescent_star", ("alloh", "qur'on", "hazrat", "iymon", "diyonat", "ramazon", "payg'ambar", "savob", "farishta")),
    ("knot", ("vafo", "ahd", "va'da", "sodiq", "do'stlik", "birodar", "va'dangga")),
    ("heart", ("sevgi", "muhabbat", "yurak", "qalb", "sog'in", "ishq")),
    ("hourglass", ("sabr", "vaqt", "umr", "kutish", "bardosh")),
    ("book", ("hikmat", "aql", "bilim", "ilm", "kitob", "haqiqat")),
    ("mountain_flag", ("g'alaba", "maqsad", "kuch", "harakat", "muvaffaqiyat", "kurash", "g'olib")),
    ("confetti_star", ("bayram", "nishon", "yubiley")),
    ("sun", ("umid", "yorug'", "baxt", "quvonch", "tong", "kelajak")),
    ("tree", ("tabiat", "hayot", "o'sish", "yaxshilik")),
]

# Which occasions deserve a fuller "scene" (main badge + accent icons
# scattered around the frame) instead of a single quiet badge. Reflective/
# religious/wisdom phrases stay minimal on purpose - clutter would fight the
# tone; celebratory ones get the richer treatment.
_SCENES = {
    "cake": ("firework", "flowers"),
    "confetti_star": ("firework", "gift"),
    "gift": ("confetti_star",),
    "heart": ("flowers",),
    "mountain_flag": ("confetti_star",),
}

# Each icon implies a mood, so once we know the icon we know the theme too -
# keeps the two systems from disagreeing (e.g. a "vafo" proverb attributed to
# a religious figure should not land on a pink love-theme background).
ICON_THEME_MAP = {
    "crescent_star": "islamic_teal",
    "cake": "party_confetti",
    "gift": "party_confetti",
    "confetti_star": "party_confetti",
    "heart": "warm_sunset",
    "sun": "warm_sunset",
    "book": "midnight_gold",
    "hourglass": "midnight_gold",
    "knot": "midnight_gold",
    "tree": "emerald_garden",
    "mountain_flag": "marble",
}

_cache = {}


def scatter_for(icon_key):
    return _SCENES.get(icon_key, ())


def pick_icon_key(text):
    lowered = text.lower()
    for key, keywords in _KEYWORD_MAP:
        if any(kw in lowered for kw in keywords):
            return key
    return None


def render_icon(key, color):
    cache_key = (key, color)
    if cache_key not in _cache:
        _cache[cache_key] = _BUILDERS[key](color)
    return _cache[cache_key]
