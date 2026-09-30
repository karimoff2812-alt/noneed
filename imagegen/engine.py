"""Low-level rendering primitives used to build rich, non-flat card backgrounds:
gradient meshes, soft bokeh blobs, film grain, vignette and glow."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def linear_gradient(size, color_top, color_bottom, angle=90):
    """Smooth linear gradient rendered with numpy (angle in degrees, 90 = top->bottom)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    proj = xx * dx + yy * dy
    proj -= proj.min()
    proj /= max(proj.max(), 1e-6)
    top = np.array(color_top, dtype=np.float32)
    bottom = np.array(color_bottom, dtype=np.float32)
    grad = top[None, None, :] + (bottom - top)[None, None, :] * proj[:, :, None]
    return Image.fromarray(grad.astype(np.uint8), mode="RGB")


def multi_stop_gradient(size, stops, angle=90):
    """stops: list of (position 0..1, (r,g,b)) sorted by position."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    proj = xx * dx + yy * dy
    proj -= proj.min()
    proj /= max(proj.max(), 1e-6)

    out = np.zeros((h, w, 3), dtype=np.float32)
    positions = [s[0] for s in stops]
    colors = [np.array(s[1], dtype=np.float32) for s in stops]
    for i in range(len(stops) - 1):
        p0, p1 = positions[i], positions[i + 1]
        c0, c1 = colors[i], colors[i + 1]
        mask = (proj >= p0) & (proj <= p1)
        span = max(p1 - p0, 1e-6)
        t = np.clip((proj - p0) / span, 0, 1)
        seg = c0[None, None, :] + (c1 - c0)[None, None, :] * t[:, :, None]
        out[mask] = seg[mask]
    out[proj < positions[0]] = colors[0]
    out[proj > positions[-1]] = colors[-1]
    return Image.fromarray(out.astype(np.uint8), mode="RGB")


def add_bokeh_blobs(img, count=14, color_palette=None, seed=None, min_r=0.08, max_r=0.32, opacity=(10, 45)):
    """Layer soft, blurred glowing blobs to break up flat gradients (cheap Perlin-like depth)."""
    rng = random.Random(seed)
    w, h = img.size
    base = img.convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if not color_palette:
        color_palette = [(255, 255, 255)]
    for _ in range(count):
        r = rng.uniform(min_r, max_r) * max(w, h)
        cx = rng.uniform(-0.15, 1.15) * w
        cy = rng.uniform(-0.15, 1.15) * h
        color = rng.choice(color_palette)
        alpha = rng.randint(*opacity)
        # canvas is padded well beyond the circle so the Gaussian blur fades to
        # zero alpha before reaching the edge (otherwise a faint rectangular
        # ghost of the canvas boundary shows up once composited).
        pad = r * 1.6
        canvas_r = r + pad
        blob = Image.new("RGBA", (int(canvas_r * 2), int(canvas_r * 2)), (0, 0, 0, 0))
        bd = ImageDraw.Draw(blob)
        bd.ellipse([pad, pad, pad + r * 2, pad + r * 2], fill=(*color, alpha))
        blob = blob.filter(ImageFilter.GaussianBlur(r * 0.45))
        overlay.alpha_composite(blob, (int(cx - canvas_r), int(cy - canvas_r)))
    return Image.alpha_composite(base, overlay).convert("RGB")


def add_film_grain(img, amount=10, seed=None):
    """Subtle luminance noise so the surface doesn't read as flat digital color."""
    rng = np.random.default_rng(seed)
    arr = np.asarray(img).astype(np.int16)
    noise = rng.normal(0, amount, arr.shape[:2])[:, :, None]
    out = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(out, mode="RGB")


def add_vignette(img, strength=0.55, feather=1.3):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2)
    dist = np.clip(dist / feather, 0, 1)
    mask = 1 - strength * (dist ** 2)
    arr = np.asarray(img).astype(np.float32) * mask[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


def add_top_sheen(img, opacity=40, height_ratio=0.5):
    """A soft light sweep from the top, like light falling on glass/paper."""
    w, h = img.size
    overlay = Image.new("L", (1, h), 0)
    for y in range(h):
        t = 1 - min(y / (h * height_ratio), 1)
        overlay.putpixel((0, y), int(opacity * (t ** 2)))
    overlay = overlay.resize((w, h))
    white = Image.new("RGB", (w, h), (255, 255, 255))
    base = img.convert("RGB")
    return Image.composite(white, base, overlay)


def soft_shadow_box(size, radius, blur, opacity=110, color=(0, 0, 0)):
    """Render a blurred rounded-rect shadow to paste behind a text panel."""
    w, h = size
    pad = blur * 3
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([pad, pad, pad + w, pad + h], radius=radius, fill=(*color, opacity))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    return canvas, pad


def radial_glow(size, color, max_opacity=160, falloff=1.0):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2)
    alpha = np.clip(1 - dist ** (1.6 * falloff), 0, 1) * max_opacity
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[:, :, 0] = color[0]
    arr[:, :, 1] = color[1]
    arr[:, :, 2] = color[2]
    arr[:, :, 3] = alpha.astype(np.uint8)
    return Image.fromarray(arr, mode="RGBA")
