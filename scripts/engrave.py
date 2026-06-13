#!/usr/bin/env python3
"""
engrave.py — Convert any image into a vintage copperplate-engraving illustration
in the Hermes Agent / Nous Research aesthetic (ink lines on parchment).

Three styles:
  hatch    - crosshatched line engraving (default, closest to the Hermes mythic figures)
  stipple  - dot/stipple etching (Atkinson-style dither, enlarged dots)
  contour  - luminance-following wavy line engraving (banknote / currency look)

Usage:
  python engrave.py input.jpg output.png
  python engrave.py input.jpg output.png --style hatch --period 7 --ink "#16140f" --paper "#f2efe6"
  python engrave.py input.jpg bg.png --background        # faded, ready as a hero/section background
  python engrave.py input.jpg bg.png --background --fade-direction left

Requires: Pillow, numpy  (pip install pillow numpy)
"""
import argparse
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

# Hermes / Nous default palette
DEFAULT_INK = "#16140f"      # warm near-black ink
DEFAULT_PAPER = "#f2efe6"    # parchment cream

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def load_luminance(path, max_size, contrast, detail, gamma=1.0):
    img = Image.open(path).convert("L")
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    if detail > 0:
        # unsharp mask keeps edges crisp so hatching reads as form, not mush
        img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=int(120 * detail), threshold=2))
    L = np.asarray(img, dtype=np.float32) / 255.0
    if gamma != 1.0:
        # tone curve before hatching. gamma<1 lifts shadows (dark photos stop
        # blocking up into solid ink); gamma>1 deepens a flat / hazy image.
        L = np.clip(L, 0.0, 1.0) ** gamma
    return L

def edge_map(L):
    """Sobel-ish edge magnitude in [0,1] — used to add outline strokes."""
    gx = np.zeros_like(L); gy = np.zeros_like(L)
    gx[:, 1:-1] = L[:, 2:] - L[:, :-2]
    gy[1:-1, :] = L[2:, :] - L[:-2, :]
    e = np.sqrt(gx ** 2 + gy ** 2)
    e = e / (e.max() + 1e-6)
    return e

def style_hatch(L, period, jitter, rng):
    """Classic crosshatch: progressively darker tones gain more hatch layers,
    line width modulated by local darkness (like burin pressure)."""
    h, w = L.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # organic wobble so lines don't look laser-printed
    wob = rng.normal(0, 1, (h // 16 + 2, w // 16 + 2)).astype(np.float32)
    wob = np.asarray(Image.fromarray(wob).resize((w, h), Image.BICUBIC)) * jitter * period

    dark = 1.0 - L
    ink = np.zeros((h, w), dtype=bool)
    # angle, tone threshold at which this hatch layer appears
    layers = [(22.5, 0.18), (112.5, 0.40), (67.5, 0.62), (157.5, 0.82)]
    for ang, thresh in layers:
        a = np.deg2rad(ang)
        phase = (xx * np.cos(a) + yy * np.sin(a) + wob) % period
        # line width grows with darkness beyond the layer threshold
        excess = np.clip((dark - thresh) / (1 - thresh + 1e-6), 0, 1)
        width = np.where(dark >= thresh, 1.0 + excess * (period * 0.45), 0.0)
        ink |= phase < width
    # crisp outlines on strong edges
    ink |= edge_map(L) > 0.32
    return ink

def style_stipple(L, period, jitter, rng):
    """Stipple etching: Atkinson dither at low res, dots enlarged back up."""
    h, w = L.shape
    scale = max(2, int(period * 0.6))
    small = np.asarray(
        Image.fromarray((L * 255).astype(np.uint8)).resize((w // scale, h // scale), Image.LANCZOS),
        dtype=np.float32) / 255.0
    sh, sw = small.shape
    buf = small.copy()
    out = np.zeros((sh, sw), dtype=bool)
    for y in range(sh):
        for x in range(sw):
            old = buf[y, x]
            new = 1.0 if old > 0.5 else 0.0
            out[y, x] = new == 0.0
            err = (old - new) / 8.0
            for dy, dx in ((0, 1), (0, 2), (1, -1), (1, 0), (1, 1), (2, 0)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < sh and 0 <= nx < sw:
                    buf[ny, nx] += err
    big = Image.fromarray((out * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)
    big = big.filter(ImageFilter.MaxFilter(3))  # round the dots slightly
    ink = np.asarray(big) > 127
    ink |= edge_map(L) > 0.35
    return ink

def style_contour(L, period, jitter, rng):
    """Wavy parallel lines whose path is displaced by luminance —
    the banknote / 'engraved portrait' technique."""
    h, w = L.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    blur_r = max(3, int(min(h, w) / 120))
    smooth = np.asarray(
        Image.fromarray((L * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur_r)),
        dtype=np.float32) / 255.0
    displaced = yy + (1.0 - smooth) * period * 2.4  # dark areas push the line path
    phase = displaced % period
    dark = 1.0 - L
    width = 0.8 + dark * (period * 0.55)
    ink = phase < width
    ink &= dark > 0.06           # blow out highlights to bare paper
    ink |= edge_map(L) > 0.34
    return ink

STYLES = {"hatch": style_hatch, "stipple": style_stipple, "contour": style_contour}

def render(ink_mask, ink_rgb, paper_rgb, softness=0.6):
    h, w = ink_mask.shape
    a = ink_mask.astype(np.float32)
    if softness > 0:
        a = np.asarray(Image.fromarray((a * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(softness)), dtype=np.float32) / 255.0
    out = np.empty((h, w, 3), dtype=np.float32)
    for c in range(3):
        out[..., c] = paper_rgb[c] * (1 - a) + ink_rgb[c] * a
    return Image.fromarray(out.astype(np.uint8))

def apply_background_fade(img, paper_rgb, direction="bottom", strength=0.55):
    """Fade toward paper so the engraving works as a hero/section background
    with text on top — exactly how the Hermes site uses its mythic figures."""
    w, h = img.size
    arr = np.asarray(img, dtype=np.float32)
    if direction in ("bottom", "top"):
        g = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        if direction == "top":
            g = g[::-1]
    else:
        g = np.linspace(0, 1, w, dtype=np.float32)[None, :]
        if direction == "left":
            g = g[:, ::-1]
    g = np.broadcast_to(g, (h, w))
    # global wash + directional fade
    alpha = np.clip(strength * 0.5 + g * strength, 0, 0.92)[..., None]
    paper = np.array(paper_rgb, dtype=np.float32)[None, None, :]
    out = arr * (1 - alpha) + paper * alpha
    return Image.fromarray(out.astype(np.uint8))

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--style", choices=STYLES, default="hatch")
    p.add_argument("--period", type=float, default=7.0, help="line/dot spacing in px (5=fine, 10=coarse)")
    p.add_argument("--contrast", type=float, default=1.35)
    p.add_argument("--gamma", type=float, default=1.0,
                   help="tone curve before hatching: <1 lifts shadows on dark photos, >1 deepens flat ones")
    p.add_argument("--detail", type=float, default=1.0, help="edge sharpening 0..2")
    p.add_argument("--jitter", type=float, default=0.35, help="organic line wobble 0..1")
    p.add_argument("--ink", default=DEFAULT_INK)
    p.add_argument("--paper", default=DEFAULT_PAPER)
    p.add_argument("--max-size", type=int, default=1600)
    p.add_argument("--background", action="store_true", help="fade output for use as a page background")
    p.add_argument("--fade-direction", choices=["bottom", "top", "left", "right"], default="bottom")
    p.add_argument("--fade-strength", type=float, default=0.55)
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    L = load_luminance(args.input, args.max_size, args.contrast, args.detail, args.gamma)
    ink_mask = STYLES[args.style](L, args.period, args.jitter, rng)
    img = render(ink_mask, hex_to_rgb(args.ink), hex_to_rgb(args.paper))
    if args.background:
        img = apply_background_fade(img, hex_to_rgb(args.paper), args.fade_direction, args.fade_strength)
    img.save(args.output)
    print(f"saved {args.output} ({img.size[0]}x{img.size[1]}, style={args.style})")

if __name__ == "__main__":
    main()
