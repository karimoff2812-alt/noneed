"""Composes the final greeting/quote card: background + frame + typography + ornaments."""
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import layout
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


def compose_card(text, author=None, theme=None, size=(1080, 1080), seed=None,
                  category_label=None, watermark=True):
    """Build one finished card. theme: Theme object, theme key string, or None (auto-pick)."""
    rng = random.Random(seed)
    if theme is None:
        theme = pick_theme(text, rng)
    elif isinstance(theme, str):
        theme = theme_by_key(theme) or pick_theme(text, rng)

    bg = theme.background(size, seed=seed)
    base = bg.convert("RGBA")
    w, h = size

    label = category_label or theme.label
    _draw_chip(base, size, label, theme.accent, theme.text_color)
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
