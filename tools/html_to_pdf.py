#!/usr/bin/env python3
"""
html_to_pdf.py — render deck.html to a send-ready deck.pdf via headless Chrome.

Purpose: produce the polished PDF at exactly 16:9 (1280x720), backgrounds on,
         fonts embedded. Isolated from PPTX so one failure doesn't sink the other.
Output:  <proposal_dir>/deck.pdf
Usage:   ./run.sh tools/html_to_pdf.py proposals/<slug>/deck.html
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import ChromeRenderError  # noqa: E402


def render_pdf(html_path: Path) -> Path:
    out = html_path.with_suffix(".pdf")   # deck.html -> deck.pdf; <name>.html -> <name>.pdf
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise ChromeRenderError("playwright not installed — run ./.venv/bin/pip install playwright") from e

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.emulate_media(media="print")
            page.pdf(
                path=str(out),
                width="1280px", height="720px",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                prefer_css_page_size=True,
            )
            browser.close()
    except ChromeRenderError:
        raise
    except Exception as e:  # noqa: BLE001 — wrap any Playwright/Chrome failure loudly
        raise ChromeRenderError(f"Chrome failed to render {html_path.name}: {e}") from e

    if not out.exists() or out.stat().st_size == 0:
        raise ChromeRenderError("PDF was not produced or is empty")
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: html_to_pdf.py proposals/<slug>/deck.html", file=sys.stderr)
        return 1
    html_path = Path(sys.argv[1])
    if not html_path.exists():
        print(f"ERROR: {html_path} not found", file=sys.stderr)
        return 1
    out = render_pdf(html_path)
    print(f"Rendered {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
