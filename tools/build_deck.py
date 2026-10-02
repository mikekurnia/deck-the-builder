#!/usr/bin/env python3
"""
build_deck.py — render deck.json into a self-contained deck.html.

Purpose: turn the deck content model into a single HTML file with the brand
         tokens, fonts, logos and contour texture all inlined as data URIs, so
         the PDF renderer (Chrome) reproduces the brand exactly and offline.
Output:  <proposal_dir>/deck.html
Usage:   ./run.sh tools/build_deck.py proposals/<slug>/deck.json
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import (BASE, ASSETS_DIR, TEMPLATES_DIR, MissingAssetError,  # noqa: E402
                   fmt_stat, rp, load_deck, brand)
from prep_images import image_data_uri  # noqa: E402

from jinja2 import Environment, FileSystemLoader, select_autoescape  # noqa: E402


def _embed(img: dict, proposal_dir: Path) -> bool:
    """Resolve one image dict ({src|url}) into a data URI on img['uri']. True if it worked."""
    if not isinstance(img, dict):
        return False
    src = img.get("src") or img.get("url")
    if not src:
        return False
    uri = image_data_uri(src, proposal_dir=proposal_dir)
    if uri:
        img["uri"] = uri
        return True
    return False


def resolve_slide_images(slides: list, proposal_dir: Path) -> None:
    """Downscale + embed every image reference as a data URI: slide-level `images` lists
    (moodboard) AND per-post `image` (content_examples). Client photos or http(s) URLs both work.
    Anything that can't be read is dropped/skipped, so the deck still builds."""
    for s in slides:
        imgs = s.get("images")
        if isinstance(imgs, list):
            s["images"] = [img for img in imgs if _embed(img, proposal_dir)]
        for post in s.get("posts", []) or []:
            if isinstance(post, dict) and isinstance(post.get("image"), dict):
                if not _embed(post["image"], proposal_dir):
                    post.pop("image", None)  # fall back to concept cover-text


def data_uri(path: Path, mime: str) -> str:
    if not path.exists():
        raise MissingAssetError(f"required asset missing: {path}")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build_assets(meta: dict, agency: dict) -> dict:
    a = {
        "font_pjs": data_uri(ASSETS_DIR / "fonts/PlusJakartaSans-VariableFont_wght.ttf", "font/ttf"),
        "font_mono": data_uri(ASSETS_DIR / "fonts/SpaceMono-Regular.ttf", "font/ttf"),
        "font_mono_bold": data_uri(ASSETS_DIR / "fonts/SpaceMono-Bold.ttf", "font/ttf"),
        "logo_color": data_uri(BASE / agency["assets"]["logo_color"], "image/png"),
        "logo_white": data_uri(BASE / agency["assets"]["logo_white"], "image/png"),
        "texture": data_uri(BASE / agency["assets"]["texture"], "image/png"),
        "brand_logo": None,
    }
    # Optional client logo: meta.brand_logo = a path relative to the proposal dir or absolute.
    bl = meta.get("brand_logo")
    if bl:
        p = Path(bl)
        if p.exists():
            a["brand_logo"] = data_uri(p, "image/png")
    return a


def render_html(deck_path: Path) -> Path:
    deck = load_deck(deck_path)
    meta = deck["meta"]
    slides = deck["slides"]
    resolve_slide_images(slides, deck_path.parent)

    tokens_css = (TEMPLATES_DIR / "tokens.css").read_text(encoding="utf-8")
    deck_css = (TEMPLATES_DIR / "deck.css").read_text(encoding="utf-8")
    agency = brand()
    assets = build_assets(meta, agency)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True, lstrip_blocks=True,
    )
    tpl = env.get_template("deck.html.j2")
    html = tpl.render(meta=meta, slides=slides, assets=assets, agency=agency,
                      tokens_css=tokens_css, deck_css=deck_css,
                      fmt_stat=fmt_stat, rp=rp)

    out = deck_path.parent / "deck.html"
    out.write_text(html, encoding="utf-8")
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: build_deck.py proposals/<slug>/deck.json", file=sys.stderr)
        return 1
    deck_path = Path(sys.argv[1])
    if not deck_path.exists():
        print(f"ERROR: {deck_path} not found", file=sys.stderr)
        return 1
    out = render_html(deck_path)
    print(f"Rendered {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
