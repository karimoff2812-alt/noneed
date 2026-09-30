"""Typography helpers: auto-fit wrapping, letter-spaced small caps, soft text shadows."""
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def load_font(path, size):
    return ImageFont.truetype(path, size)


def wrap_to_width(draw, text, font, max_width):
    words = text.split()
    if not words:
        return [""]
    lines, current = [], words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def fit_quote(draw, text, font_path, max_width, max_height, start_size=92, min_size=40, line_spacing=1.32):
    size = start_size
    while size >= min_size:
        font = load_font(font_path, size)
        lines = wrap_to_width(draw, text, font, max_width)
        line_h = font.getbbox("Ag")[3] * line_spacing
        total_h = line_h * len(lines)
        widest = max(draw.textlength(l, font=font) for l in lines)
        if total_h <= max_height and widest <= max_width:
            return font, lines, line_h
        size -= 2
    font = load_font(font_path, min_size)
    lines = wrap_to_width(draw, text, font, max_width)
    line_h = font.getbbox("Ag")[3] * line_spacing
    return font, lines, line_h


def draw_text_with_shadow(draw, xy, text, font, fill, anchor="mm",
                           shadow_color=(0, 0, 0), shadow_opacity=120, shadow_blur=6, shadow_offset=(0, 3),
                           canvas_size=None, base_img=None):
    """Draws soft drop-shadow text directly onto base_img (RGBA) for legibility over busy art."""
    if base_img is None:
        draw.text(xy, text, font=font, fill=fill, anchor=anchor)
        return
    w, h = canvas_size
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sx, sy = xy[0] + shadow_offset[0], xy[1] + shadow_offset[1]
    sd.text((sx, sy), text, font=font, fill=(*shadow_color, shadow_opacity), anchor=anchor)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
    base_img.alpha_composite(shadow_layer)
    text_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    td.text(xy, text, font=font, fill=(*fill, 255), anchor=anchor)
    base_img.alpha_composite(text_layer)


def draw_tracked_text(draw, xy, text, font, fill, tracking=4, anchor_h="m"):
    """Manual letter-spacing (PIL has no native tracking) - used for small-caps labels."""
    total_w = sum(draw.textlength(ch, font=font) + tracking for ch in text) - tracking
    x, y = xy
    if anchor_h == "m":
        x -= total_w / 2
    cursor = x
    for ch in text:
        draw.text((cursor, y), ch, font=font, fill=fill, anchor="lm")
        cursor += draw.textlength(ch, font=font) + tracking
    return total_w
