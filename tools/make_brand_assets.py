#!/usr/bin/env python3
"""
make_brand_assets.py — generate the agency's logo wordmarks + contour texture from code.

Purpose: the public demo ships no real agency artwork. Everything visual that the
         deck inlines (wordmark PNGs + the topographic texture on dark slides) is
         generated deterministically from config/brand.json, so a fork can re-skin
         the factory by editing one JSON file and re-running this script.
Output:  assets/logo/<slug>-wordmark-color.png, <slug>-wordmark-white.png,
         <slug>-wordmark.svg, assets/texture/contour-texture.png
Usage:   ./run.sh tools/make_brand_assets.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import ASSETS_DIR, brand, slugify  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

FONT = ASSETS_DIR / "fonts/PlusJakartaSans-VariableFont_wght.ttf"
MONO = ASSETS_DIR / "fonts/SpaceMono-Bold.ttf"


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _font(size: int, weight: int = 800) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:  # noqa: BLE001 — static font fallback
        pass
    return f


def _mark(draw: ImageDraw.ImageDraw, x: int, y: int, s: int, c1, c2) -> None:
    """Two interlocking chain links ('rantai' = chain)."""
    w, h, r, t = int(s * 0.62), int(s * 0.40), int(s * 0.20), max(4, s // 11)
    draw.rounded_rectangle([x, y + s * 0.12, x + w, y + s * 0.12 + h], radius=r, outline=c1, width=t)
    draw.rounded_rectangle([x + s * 0.38, y + s * 0.46, x + s * 0.38 + w, y + s * 0.46 + h],
                           radius=r, outline=c2, width=t)


def wordmark(name: str, ink, primary, accent, out: Path, scale: int = 4) -> None:
    H = 64 * scale
    big = _font(34 * scale, 800)
    small = ImageFont.truetype(str(MONO), 9 * scale)
    word = name.split()[-1].upper()
    pre = " ".join(name.split()[:-1]).upper() or "STUDIO"
    tw = int(big.getlength(word))
    W = H + 14 * scale + tw + 8 * scale
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    _mark(d, 4 * scale, 6 * scale, 52 * scale, primary, accent)
    tx = H + 10 * scale
    d.text((tx, 2 * scale), pre, font=small, fill=accent)
    d.text((tx - 2 * scale, 12 * scale), word, font=big, fill=ink)
    im = im.crop(im.getbbox())  # trim transparent margins
    pad = 2 * scale
    canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    canvas.paste(im, (pad, pad))
    canvas.save(out, optimize=True)


def wordmark_svg(name: str, primary: str, accent: str, ink: str, out: Path) -> None:
    word = name.split()[-1].upper()
    pre = " ".join(name.split()[:-1]).upper() or "STUDIO"
    out.write_text(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 64" role="img" aria-label="{name}">
  <rect x="4" y="12" width="32" height="21" rx="10" fill="none" stroke="{primary}" stroke-width="5"/>
  <rect x="24" y="30" width="32" height="21" rx="10" fill="none" stroke="{accent}" stroke-width="5"/>
  <text x="74" y="14" font-family="Space Mono, monospace" font-weight="700" font-size="9" letter-spacing="2" fill="{accent}">{pre}</text>
  <text x="72" y="48" font-family="Plus Jakarta Sans, sans-serif" font-weight="800" font-size="34" fill="{ink}">{word}</text>
</svg>
""", encoding="utf-8")


def contour_texture(primary, accent, out: Path, w: int = 1600, h: int = 900) -> None:
    """Procedural topographic contour lines (sum of radial waves), light on black for
    a screen-blend overlay on dark slides."""
    im = Image.new("RGB", (w, h), (0, 0, 0))
    px = im.load()
    centers = [(0.22, 0.30, 1.0, 9), (0.78, 0.62, 0.9, 7), (0.52, 0.05, -0.5, 14),
               (0.08, 0.90, 0.6, 12), (0.95, 0.10, 0.5, 10), (0.50, 0.75, -0.4, 16)]
    step = 0.045
    for y in range(h):
        for x in range(w):
            u, v = x / w, y / h * (h / w)
            z = 0.0
            for cx, cy, a, k in centers:
                cy *= h / w
                z += a * math.exp(-((u - cx) ** 2 + (v - cy) ** 2) * k)
            z += 0.09 * math.sin(u * 7 + v * 3) * math.cos(v * 9 - u * 2)
            frac = (z / step) % 1.0
            if frac < 0.06 or frac > 0.94:
                band = int(z / step)
                px[x, y] = accent if band % 4 == 0 else primary
    im.save(out, optimize=True)


def main() -> int:
    b = brand()
    c = b["colors"]
    primary, accent, ink = _hex(c["primary"]), _hex(c["accent"]), _hex(c["ink"])
    slug = slugify(b["name"])
    (ASSETS_DIR / "logo").mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "texture").mkdir(parents=True, exist_ok=True)
    wordmark(b["name"], ink, primary, accent, ASSETS_DIR / f"logo/{slug}-wordmark-color.png")
    wordmark(b["name"], (255, 255, 255), (255, 255, 255), accent,
             ASSETS_DIR / f"logo/{slug}-wordmark-white.png")
    wordmark_svg(b["name"], c["primary"], c["accent"], c["ink"], ASSETS_DIR / f"logo/{slug}-wordmark.svg")
    light_primary = tuple(min(255, int(v * 1.9) + 40) for v in primary)
    contour_texture(light_primary, accent, ASSETS_DIR / "texture/contour-texture.png")
    print(f"Generated brand assets for {b['name']} in {ASSETS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
