"""Composes the final greeting/quote card: background + frame + typography + ornaments."""
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import icons, layout
from .themes import THEMES, pick_theme, theme_by_key

FONT_DIR = __file__.rsplit("/", 1)[0] + "/fonts"


def _is_dark(color):
    r, g, b = color
    return (0.299 * r + 0.587 * g + 0.114 * b) < 140


def _draw_frame(base, size, accent, inset_ratio=0.045):
    w, h = size
    inset = int(min(w, h) * inset_ratio)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(
        [inset, inset, w - inset, h - inset], radius=int(min(w, h) * 0.02),
        outline=(*accent, 90), width=2,
    )
    corner = int(min(w, h) * 0.05)
    for cx, cy, dx, dy in [
        (inset, inset, 1, 1), (w - inset, inset, -1, 1),
        (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1),
    ]:
        gap = int(min(w, h) * 0.018)
        d.line([(cx + gap * dx, cy), (cx + (gap + corner) * dx, cy)], fill=(*accent, 160), width=2)
        d.line([(cx, cy + gap * dy), (cx, cy + (gap + corner) * dy)], fill=(*accent, 160), width=2)


def _draw_chip(base, size, label, accent, text_color):
    w, h = size
    font = layout.load_font(f"{FONT_DIR}/Outfit-Bold.ttf", int(h * 0.0185))
    d = ImageDraw.Draw(base)
    tracking = int(h * 0.006)
    text_w = sum(d.textlength(ch, font=font) + tracking for ch in label) - tracking
    pad_x, pad_y = int(h * 0.028), int(h * 0.014)
    chip_w, chip_h = text_w + pad_x * 2, font.getbbox("Ag")[3] + pad_y * 2
    cx = w / 2
    cy = h * 0.115
    d.rounded_rectangle(
        [cx - chip_w / 2, cy - chip_h / 2, cx + chip_w / 2, cy + chip_h / 2],
        radius=chip_h / 2, outline=(*accent, 200), width=2,
    )
    layout.draw_tracked_text(d, (cx, cy), label, font, (*accent, 255), tracking=tracking)


def _draw_quote_mark(base, size, accent, y_ratio):
    w, h = size
    font = layout.load_font(f"{FONT_DIR}/Gloock-Regular.ttf", int(h * 0.11))
    d = ImageDraw.Draw(base)
    d.text((w / 2, h * y_ratio), "“", font=font, fill=(*accent, 70), anchor="mm")


def _draw_icon_badge(base, size, icon_key, accent, y_ratio=0.205):
    """A ringed badge with a line-art icon, so the phrase's meaning reads at a
    glance before the text is even read."""
    w, h = size
    cx, cy = w / 2, h * y_ratio
    ring_r = h * 0.052
    d = ImageDraw.Draw(base)
    d.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], outline=(*accent, 200), width=2)
    icon_tile = icons.render_icon(icon_key, accent)
    icon_size = int(ring_r * 1.35)
    icon_tile = icon_tile.resize((icon_size, icon_size), Image.LANCZOS)
    base.alpha_composite(icon_tile, (int(cx - icon_size / 2), int(cy - icon_size / 2)))


def _draw_divider(base, size, accent, y):
    w, h = size
    d = ImageDraw.Draw(base)
    half = w * 0.06
    cx = w / 2
    d.line([(cx - half, y), (cx - half * 0.28, y)], fill=(*accent, 200), width=2)
    d.line([(cx + half * 0.28, y), (cx + half, y)], fill=(*accent, 200), width=2)
    r = h * 0.004
    d.ellipse([cx - r, y - r, cx + r, y + r], fill=(*accent, 220))


def _draw_watermark(base, size, color, text="Kichkina tabib • t.me/yordamchiagent1_bot"):
    w, h = size
    font = layout.load_font(f"{FONT_DIR}/Outfit-Regular.ttf", int(h * 0.0145))
    d = ImageDraw.Draw(base)
    d.text((w / 2, h * 0.965), text, font=font, fill=(*color, 130), anchor="mm")


_SCATTER_SLOTS = (
    (0.135, 0.10, 0.8, 200),
    (0.865, 0.085, 0.65, 180),
    (0.87, 0.40, 0.95, 235),
    (0.11, 0.44, 0.8, 220),
)


def _draw_scene_scatter(base, size, accent, scatter_keys, seed=None):
    """Places a small handful of accent icons around the frame corners so the
    card reads as a little scene (e.g. cake + fireworks + flowers for a
    birthday) rather than a single lonely badge. Works for any occasion that
    declares scatter icons in icons.scatter_for()."""
    if not scatter_keys:
        return
    rng = random.Random(seed)
    w, h = size
    slots = list(_SCATTER_SLOTS)
    rng.shuffle(slots)
    for (x_r, y_r, scale, alpha), key in zip(slots, scatter_keys * 2):
        x, y = w * x_r, h * (y_r if h <= w else y_r * 0.92)
        tile = icons.render_icon(key, accent)
        s = max(1, int(h * 0.085 * scale))
        tile = tile.resize((s, s), Image.LANCZOS)
        a = tile.split()[3].point(lambda p, alpha=alpha: int(p * alpha / 255))
        tile.putalpha(a)
        jitter = int(h * 0.01)
        ox, oy = rng.randint(-jitter, jitter), rng.randint(-jitter, jitter)
        base.alpha_composite(tile, (int(x - s / 2) + ox, int(y - s / 2) + oy))


def compose_card(text, author=None, theme=None, size=(1080, 1080), seed=None,
                  category_label=None, watermark=True):
    """Build one finished card. theme: Theme object, theme key string, or None (auto-pick)."""
    rng = random.Random(seed)
    # Author often carries the strongest signal ("Hazrat Ali", "Xalq maqoli") -
    # match icon/theme keywords against text and author together.
    match_text = f"{text} {author or ''}"
    icon_key = icons.pick_icon_key(match_text)

    if theme is None:
        mapped = icons.ICON_THEME_MAP.get(icon_key)
        theme = theme_by_key(mapped) if mapped else pick_theme(match_text, rng)
    elif isinstance(theme, str):
        theme = theme_by_key(theme) or pick_theme(match_text, rng)

    bg = theme.background(size, seed=seed)
    base = bg.convert("RGBA")
    w, h = size

    label = category_label or theme.label
    _draw_chip(base, size, label, theme.accent, theme.text_color)

    if icon_key:
        _draw_icon_badge(base, size, icon_key, theme.accent)
        _draw_scene_scatter(base, size, theme.accent, icons.scatter_for(icon_key), seed=seed)
    else:
        _draw_quote_mark(base, size, theme.accent, y_ratio=0.225)

    margin_x = int(w * 0.135)
    top_bound = h * 0.30
    bottom_bound = h * (0.72 if author else 0.76)
    max_w = w - margin_x * 2
    max_h = bottom_bound - top_bound

    probe = ImageDraw.Draw(base)
    start_size = int(h * 0.075)
    min_size = int(h * 0.032)
    font, lines, line_h = layout.fit_quote(
        probe, text, theme.quote_font, max_w, max_h,
        start_size=start_size, min_size=min_size,
    )

    block_h = line_h * len(lines)
    y = top_bound + (max_h - block_h) / 2 + line_h / 2
    for line in lines:
        layout.draw_text_with_shadow(
            probe, (w / 2, y), line, font, theme.text_color, anchor="mm",
            shadow_opacity=130, shadow_blur=int(h * 0.006), shadow_offset=(0, int(h * 0.003)),
            canvas_size=size, base_img=base,
        )
        y += line_h

    divider_y = y + line_h * 0.05
    _draw_divider(base, size, theme.accent, divider_y)

    if author:
        author_font = layout.load_font(theme.author_font, int(h * 0.0225))
        d = ImageDraw.Draw(base)
        layout.draw_tracked_text(
            d, (w / 2, divider_y + h * 0.045), author.upper(), author_font,
            (*theme.author_color, 255), tracking=int(h * 0.0035),
        )

    _draw_frame(base, size, theme.accent)
    if watermark:
        sample = bg.getpixel((w // 2, int(h * 0.965)))
        wm_color = (255, 255, 255) if _is_dark(sample) else (30, 24, 16)
        _draw_watermark(base, size, wm_color)

    return base.convert("RGB")


def compose_status(text, author=None, theme=None, seed=None, category_label=None):
    """Vertical 1080x1920 story/status format - same language, taller safe area."""
    return compose_card(
        text, author=author, theme=theme, size=(1080, 1920), seed=seed,
        category_label=category_label,
    )


def list_theme_keys():
    return list(THEMES.keys())
