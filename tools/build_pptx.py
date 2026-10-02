#!/usr/bin/env python3
"""
build_pptx.py — render deck.json into a PPTX that matches the PDF exactly.

Approach: each slide is rendered from the SAME HTML the PDF uses (deck.html) to a
high-resolution image via headless Chrome, then placed full-bleed on a 16:9
PowerPoint slide. The .pptx is therefore pixel-identical to the PDF.
Trade-off: slides are images, not editable text — to change content, edit deck.json
and regenerate (or edit the HTML/templates).
Output:  <proposal_dir>/deck.pptx
Usage:   ./run.sh tools/build_pptx.py proposals/<slug>/deck.json
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "templates"))
from _util import PptxBuildError  # noqa: E402
import pptx_theme as T  # noqa: E402

from pptx import Presentation  # noqa: E402

SCALE = 2  # device pixel ratio → 2560x1440 per slide (crisp at PowerPoint size)


def render_slide_images(html_path: Path, out_dir: Path) -> list[Path]:
    """Screenshot every .slide element from the rendered deck HTML at high DPI."""
    from playwright.sync_api import sync_playwright

    pngs: list[Path] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720},
                                device_scale_factor=SCALE)
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        slides = page.query_selector_all(".slide")
        for i, sl in enumerate(slides):
            f = out_dir / f"slide_{i:03d}.png"
            sl.screenshot(path=str(f))
            pngs.append(f)
        browser.close()
    return pngs


def build(deck_path: Path) -> Path:
    html_path = deck_path.parent / "deck.html"
    if not html_path.exists():
        # Ensure the HTML exists (normally build_deck runs first in the pipeline).
        from build_deck import render_html  # noqa: PLC0415
        render_html(deck_path)
    try:
        with tempfile.TemporaryDirectory() as td:
            pngs = render_slide_images(html_path, Path(td))
            if not pngs:
                raise PptxBuildError("no .slide elements found in deck.html")
            prs = Presentation()
            prs.slide_width = T.EMU_W
            prs.slide_height = T.EMU_H
            blank = prs.slide_layouts[6]
            for png in pngs:
                slide = prs.slides.add_slide(blank)
                slide.shapes.add_picture(str(png), 0, 0, width=T.EMU_W, height=T.EMU_H)
            out = deck_path.parent / "deck.pptx"
            prs.save(str(out))  # save inside the tempdir so the PNGs still exist
    except PptxBuildError:
        raise
    except Exception as e:  # noqa: BLE001
        raise PptxBuildError(f"failed to build image-matched PPTX for {deck_path.name}: {e}") from e
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: build_pptx.py proposals/<slug>/deck.json", file=sys.stderr)
        return 1
    deck_path = Path(sys.argv[1])
    if not deck_path.exists():
        print(f"ERROR: {deck_path} not found", file=sys.stderr)
        return 1
    out = build(deck_path)
    print(f"Built {out} ({out.stat().st_size // 1024} KB) — one image per slide, matches the PDF exactly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
