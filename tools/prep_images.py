#!/usr/bin/env python3
"""
prep_images.py — downscale + embed content images as data URIs.

Purpose: moodboard / content images can be 15 MB source photos. Embedding them raw
         would make a huge PDF. This downscales to a web size and returns a data URI,
         so the deck stays self-contained but light. Missing/broken images are
         skipped-and-labeled, never crash the build.
Output:  imported by build_deck.py; CLI prints a data-URI length for a quick check.
Usage:   ./run.sh tools/prep_images.py /path/to/photo.jpg
"""
from __future__ import annotations

import base64
import hashlib
import io
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import BASE  # noqa: E402

from PIL import Image, ImageOps  # noqa: E402

MAX_PX = 1600      # long-edge cap
QUALITY = 82       # JPEG quality
CACHE_DIR = BASE / ".tmp" / "img-cache"
_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DeckTheBuilder/1.0"


def _fetch_url(url: str) -> Path | None:
    """Download a web image into .tmp/img-cache (cached by URL hash). Best-effort → None on failure."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(url.split("?")[0]).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".img"
    dest = CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ext)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = r.read()
        if not data:
            return None
        dest.write_bytes(data)
        return dest
    except Exception as e:  # noqa: BLE001 — a dead link must not break the deck
        print(f"  [prep_images] skip (fetch failed: {e}): {url}", file=sys.stderr)
        return None


def resolve(path: str, proposal_dir: Path | None = None) -> Path | None:
    """Resolve an image reference: http(s) URL (downloaded+cached), absolute path,
    or relative to the proposal dir / repo root."""
    if isinstance(path, str) and path.startswith(("http://", "https://")):
        return _fetch_url(path)
    p = Path(path)
    if p.is_absolute() and p.exists():
        return p
    for base in [proposal_dir, BASE, Path.cwd()]:
        if base and (base / path).exists():
            return base / path
    return p if p.exists() else None


def image_data_uri(path: str, proposal_dir: Path | None = None,
                   max_px: int = MAX_PX, quality: int = QUALITY) -> str | None:
    """Downscale an image and return a data: URI, or None if it can't be read.
    Never raises — a bad image is skipped so the deck still builds."""
    src = resolve(path, proposal_dir)
    if not src:
        print(f"  [prep_images] skip (not found): {path}", file=sys.stderr)
        return None
    try:
        im = Image.open(src)
        im = im.convert("RGB")  # flatten transparency onto its own bg; JPEG-safe
        w, h = im.size
        scale = min(1.0, max_px / max(w, h))
        if scale < 1.0:
            im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    except Exception as e:  # noqa: BLE001 — a broken image must not kill the deck
        print(f"  [prep_images] skip (unreadable: {e}): {src}", file=sys.stderr)
        return None


def image_jpeg_bytes(path: str, proposal_dir: Path | None = None,
                     max_px: int = MAX_PX, quality: int = QUALITY):
    """Downscaled JPEG as a BytesIO (for python-pptx add_picture), or None. Never raises."""
    src = resolve(path, proposal_dir)
    if not src:
        return None
    try:
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        w, h = im.size
        scale = min(1.0, max_px / max(w, h))
        if scale < 1.0:
            im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality, optimize=True)
        buf.seek(0)
        return buf
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: prep_images.py /path/to/image", file=sys.stderr)
        return 1
    uri = image_data_uri(sys.argv[1])
    if uri is None:
        print("could not process image")
        return 1
    print(f"ok — data URI {len(uri) // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
