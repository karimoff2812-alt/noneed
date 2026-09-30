"""Theme definitions: each theme is a self-contained mood (palette + background recipe
+ typography) so cards stop looking like plain black boxes with white text."""
import math
import random
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFilter

from . import engine

FONT_DIR = __file__.rsplit("/", 1)[0] + "/fonts"


@dataclass
class Theme:
    key: str
    label: str                 # Uzbek display name, shown on the category chip
    quote_font: str
    quote_italic: bool
    author_font: str
    accent: tuple               # gold/accent RGB used for lines, quote marks, chip border
    text_color: tuple
    author_color: tuple
    chip_bg: tuple
    background: callable         # fn(size, seed) -> PIL.Image
    keywords: tuple = field(default_factory=tuple)  # for auto-theme matching


def _panel_gradient_bg(size, seed, stops, angle, blob_colors, grain=9, vignette=0.5):
    img = engine.multi_stop_gradient(size, stops, angle=angle)
    img = engine.add_bokeh_blobs(img, count=16, color_palette=blob_colors, seed=seed)
    img = img.filter(ImageFilter.GaussianBlur(2))
    img = engine.add_top_sheen(img, opacity=26)
    img = engine.add_film_grain(img, amount=grain, seed=seed)
    img = engine.add_vignette(img, strength=vignette)
    return img


def bg_midnight_gold(size, seed=None):
    return _panel_gradient_bg(
        size, seed,
        stops=[(0.0, (18, 22, 34)), (0.45, (26, 27, 46)), (1.0, (10, 11, 20))],
        angle=115,
        blob_colors=[(214, 175, 105), (120, 110, 160), (60, 70, 110)],
        grain=8, vignette=0.55,
    )


def bg_warm_sunset(size, seed=None):
    return _panel_gradient_bg(
        size, seed,
        stops=[(0.0, (255, 158, 128)), (0.5, (233, 96, 122)), (1.0, (94, 53, 117))],
        angle=100,
        blob_colors=[(255, 214, 153), (255, 255, 255), (255, 120, 140)],
        grain=7, vignette=0.45,
    )


def bg_emerald_garden(size, seed=None):
    return _panel_gradient_bg(
        size, seed,
        stops=[(0.0, (20, 66, 58)), (0.5, (13, 46, 45)), (1.0, (8, 24, 28))],
        angle=125,
        blob_colors=[(196, 220, 150), (110, 180, 150), (230, 200, 120)],
        grain=8, vignette=0.5,
    )


def bg_pearl_paper(size, seed=None):
    img = engine.multi_stop_gradient(
        size, [(0.0, (250, 244, 232)), (0.55, (240, 231, 213)), (1.0, (226, 213, 189))], angle=100,
    )
    img = engine.add_bokeh_blobs(img, count=10, color_palette=[(255, 255, 255), (214, 190, 150)],
                                  seed=seed, opacity=(8, 22))
    img = engine.add_film_grain(img, amount=6, seed=seed)
    img = engine.add_vignette(img, strength=0.22, feather=1.5)
    return img


def bg_marble(size, seed=None):
    rng = random.Random(seed)
    img = engine.multi_stop_gradient(
        size, [(0.0, (40, 42, 48)), (0.5, (58, 58, 64)), (1.0, (24, 25, 30))], angle=100,
    )
    w, h = size
    veins = Image.new("L", size, 0)
    vd = ImageDraw.Draw(veins)
    for _ in range(6):
        x = rng.uniform(0, w)
        y = -50
        pts = [(x, y)]
        for _ in range(9):
            x += rng.uniform(-w * 0.12, w * 0.12)
            y += h / 9
            pts.append((x, y))
        vd.line(pts, fill=rng.randint(140, 220), width=rng.randint(2, 5))
    veins = veins.filter(ImageFilter.GaussianBlur(3))
    gold = Image.new("RGB", size, (196, 168, 110))
    img = Image.composite(gold, img, veins.point(lambda p: int(p * 0.35)))
    img = engine.add_bokeh_blobs(img, count=8, color_palette=[(255, 255, 255)], seed=seed, opacity=(6, 16))
    img = engine.add_film_grain(img, amount=7, seed=seed)
    img = engine.add_vignette(img, strength=0.5)
    return img


def bg_islamic_teal(size, seed=None):
    img = _panel_gradient_bg(
        size, seed,
        stops=[(0.0, (9, 46, 48)), (0.5, (12, 58, 56)), (1.0, (6, 30, 32))],
        angle=115,
        blob_colors=[(214, 175, 105), (90, 150, 140)],
        grain=8, vignette=0.55,
    )
    return _draw_geometric_lattice(img, color=(214, 175, 105), opacity=26)


def _draw_geometric_lattice(img, color, opacity):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    step = w / 7
    r = step * 0.5
    for row in range(-1, 9):
        for col in range(-1, 9):
            cx = col * step + (step / 2 if row % 2 else 0)
            cy = row * step * 0.87
            _star8(d, cx, cy, r, color, opacity)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.4))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _star8(draw, cx, cy, r, color, opacity):
    pts_outer = [(cx + r * math.cos(a), cy + r * math.sin(a))
                 for a in [math.radians(45 * i) for i in range(8)]]
    pts_inner = [(cx + r * 0.55 * math.cos(a + math.radians(22.5)), cy + r * 0.55 * math.sin(a + math.radians(22.5)))
                 for a in [math.radians(45 * i) for i in range(8)]]
    pts = []
    for o, i in zip(pts_outer, pts_inner):
        pts.append(o)
        pts.append(i)
    draw.polygon(pts, outline=(*color, opacity))


THEMES = {
    "midnight_gold": Theme(
        key="midnight_gold", label="HIKMAT",
        quote_font=f"{FONT_DIR}/Lora-Italic.ttf", quote_italic=True,
        author_font=f"{FONT_DIR}/Outfit-Regular.ttf",
        accent=(214, 175, 105), text_color=(245, 241, 232), author_color=(214, 175, 105),
        chip_bg=(255, 255, 255),
        background=bg_midnight_gold,
        keywords=("hikmat", "aql", "sabr", "vaqt", "umr", "haqiqat"),
    ),
    "warm_sunset": Theme(
        key="warm_sunset", label="SEVGI",
        quote_font=f"{FONT_DIR}/CrimsonPro-Italic.ttf", quote_italic=True,
        author_font=f"{FONT_DIR}/Outfit-Regular.ttf",
        accent=(255, 236, 214), text_color=(255, 250, 245), author_color=(255, 236, 214),
        chip_bg=(255, 255, 255),
        background=bg_warm_sunset,
        keywords=("sevgi", "muhabbat", "yurak", "qalb", "sog'in"),
    ),
    "emerald_garden": Theme(
        key="emerald_garden", label="TABIAT",
        quote_font=f"{FONT_DIR}/Lora-Italic.ttf", quote_italic=True,
        author_font=f"{FONT_DIR}/Outfit-Regular.ttf",
        accent=(196, 220, 150), text_color=(240, 245, 236), author_color=(196, 220, 150),
        chip_bg=(255, 255, 255),
        background=bg_emerald_garden,
        keywords=("tabiat", "hayot", "kelajak", "umid", "yaxshilik"),
    ),
    "pearl_paper": Theme(
        key="pearl_paper", label="MINIMAL",
        quote_font=f"{FONT_DIR}/CrimsonPro-Italic.ttf", quote_italic=True,
        author_font=f"{FONT_DIR}/Outfit-Regular.ttf",
        accent=(150, 120, 80), text_color=(48, 40, 30), author_color=(120, 95, 60),
        chip_bg=(60, 50, 35),
        background=bg_pearl_paper,
        keywords=("oddiy", "sokin", "tinchlik"),
    ),
    "marble": Theme(
        key="marble", label="MOTIVATSIYA",
        quote_font=f"{FONT_DIR}/Lora-Bold.ttf", quote_italic=False,
        author_font=f"{FONT_DIR}/Outfit-Regular.ttf",
        accent=(214, 186, 130), text_color=(248, 246, 240), author_color=(214, 186, 130),
        chip_bg=(255, 255, 255),
        background=bg_marble,
        keywords=("g'alaba", "kuch", "maqsad", "harakat", "muvaffaqiyat"),
    ),
    "islamic_teal": Theme(
        key="islamic_teal", label="DINIY",
        quote_font=f"{FONT_DIR}/Lora-Italic.ttf", quote_italic=True,
        author_font=f"{FONT_DIR}/Outfit-Regular.ttf",
        accent=(214, 175, 105), text_color=(244, 240, 228), author_color=(214, 175, 105),
        chip_bg=(255, 255, 255),
        background=bg_islamic_teal,
        keywords=("alloh", "qur'on", "hazrat", "iymon", "diyonat", "savob", "payg'ambar"),
    ),
}


def pick_theme(text, rng=None):
    rng = rng or random
    lowered = text.lower()
    for theme in THEMES.values():
        if any(kw in lowered for kw in theme.keywords):
            return theme
    return rng.choice(list(THEMES.values()))


def theme_by_key(key):
    return THEMES.get(key)
