#!/usr/bin/env python3
"""
new_proposal.py — scaffold a proposal folder + an empty deck.json skeleton.

Purpose: give the designer stage a valid starting deck.json so it fills content
         rather than inventing structure. Creates proposals/<slug>/.
Output:  proposals/<slug>/deck.json (skeleton) and prints the folder path.
Usage:   ./run.sh tools/new_proposal.py "Kopi Senja" --title "Stay for the Golden Hour" --accent "#D9822B"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import PROPOSALS_DIR, slugify, brand as brand_cfg  # noqa: E402


def skeleton(brand: str, title: str, accent: str, language: str) -> dict:
    agency_name = brand_cfg()["name"]
    return {
        "meta": {
            "brand": brand,
            "brand_slug": slugify(brand),
            "campaign_title": title or f"{brand} × {agency_name}",
            "date": "2026",
            "language": language,
            "accent_hex": accent,
        },
        "slides": [
            {"type": "cover", "eyebrow": "Campaign Proposal", "title": title or brand},
            {"type": "about_agency"},
            {"type": "understanding_brand"},
            {"type": "big_idea"},
            {"type": "strategic_approach"},
            {"type": "phases_timeline"},
            {"type": "service_breakdown"},
            {"type": "proposed_kols"},
            {"type": "investment"},
            {"type": "why_agency"},
            {"type": "next_steps"},
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a proposal folder.")
    ap.add_argument("brand")
    ap.add_argument("--title", default="")
    ap.add_argument("--accent", default="#C99A45", help="client brand colour hex to blend")
    ap.add_argument("--language", default="en", choices=["en", "id"])
    args = ap.parse_args()

    slug = slugify(args.brand)
    pdir = PROPOSALS_DIR / slug
    pdir.mkdir(parents=True, exist_ok=True)
    deck_path = pdir / "deck.json"
    if deck_path.exists():
        print(f"NOTE: {deck_path} already exists — leaving it untouched.")
    else:
        deck_path.write_text(json.dumps(skeleton(args.brand, args.title, args.accent, args.language),
                                        indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Scaffolded {deck_path}")
    print(pdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
