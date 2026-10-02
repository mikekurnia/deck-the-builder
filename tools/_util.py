#!/usr/bin/env python3
"""
_util.py — shared helpers for every Proposal Factory tool.

Purpose: one place for IDR money formatting, slugify, provenance-aware number
         rendering, config/deck loading, tier lookups, and named exceptions —
         so the HTML renderer, the PPTX renderer, and verify_outputs all agree.
Output:  imported by the other tools; not run directly.
Usage:   from _util import rp, slugify, fmt_stat, config, load_deck
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# --- Paths (BASE = repo root, one level up from tools/) ---------------------
BASE = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE / "config"
ASSETS_DIR = BASE / "assets"
TEMPLATES_DIR = BASE / "templates"
SCHEMA_DIR = BASE / "schema"
DATA_DIR = BASE / "data"
ROSTER_DIR = DATA_DIR / "roster"
PROPOSALS_DIR = BASE / "proposals"

# --- Named exceptions (loud, specific failures — see failure-modes registry) -
class ProposalError(Exception):
    """Base class for all Proposal Factory tool errors."""


class MissingAssetError(ProposalError):
    """A required brand asset (logo, texture, font) is missing."""


class EmptyRosterError(ProposalError):
    """A roster query returned zero KOLs — caller should fall back to web/to-vet."""


class DeckValidationError(ProposalError):
    """deck.json failed JSON-Schema validation or provenance rules."""


class ChromeRenderError(ProposalError):
    """Playwright/Chrome failed to render the HTML deck to PDF."""


class PptxBuildError(ProposalError):
    """python-pptx failed to build the editable deck."""


# --- Money (IDR) ------------------------------------------------------------
def rp(amount) -> str:
    """Format an IDR amount the Indonesian way: rp(1650000000) -> 'Rp 1.650.000.000'."""
    try:
        n = round(float(amount))
    except (TypeError, ValueError):
        return "Rp -"
    return "Rp " + f"{n:,.0f}".replace(",", ".")


def rp_compact(amount) -> str:
    """Compact IDR for tight stat tiles: 1650000000 -> 'Rp 1,65 M', 12000000 -> 'Rp 12 jt'."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "Rp -"
    if abs(n) >= 1_000_000_000:
        return "Rp " + f"{n / 1_000_000_000:.2f}".rstrip("0").rstrip(".").replace(".", ",") + " M"
    if abs(n) >= 1_000_000:
        return "Rp " + f"{n / 1_000_000:.0f} jt"
    return rp(n)


# --- Numbers ----------------------------------------------------------------
def human_int(n) -> str:
    """View-count style: 3379993 -> '3.38M', 169439 -> '169K', 8800 -> '8.8K'."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    a = abs(n)
    if a >= 1_000_000:
        return f"{n / 1_000_000:.2f}".rstrip("0").rstrip(".") + "M"
    if a >= 10_000:
        return f"{n / 1_000:.0f}K"
    if a >= 1_000:
        return f"{n / 1_000:.1f}".rstrip("0").rstrip(".") + "K"
    return f"{n:.0f}"


# --- Provenance-aware stat rendering ----------------------------------------
# A "stat" in deck.json is either a plain string (rendered as-is) or an object:
#   {"value": 3379993, "provenance": "verified", "unit": "views", "compact": true}
# provenance ∈ {verified, estimate, target}. This is the ONE place that decides
# how each kind is labeled, so no renderer can present a guess as fact.
PROVENANCE = ("verified", "estimate", "target")


def fmt_stat(stat) -> str:
    """Render a provenance-tagged stat to a display string.

    verified -> '3.38M views'
    estimate -> '~40K views (est.)'
    target   -> '500K views (target)'
    """
    if stat is None:
        return ""
    if isinstance(stat, (int, float)):
        return human_int(stat)
    if isinstance(stat, str):
        return stat
    if not isinstance(stat, dict):
        return str(stat)

    value = stat.get("value")
    prov = stat.get("provenance", "verified")
    unit = stat.get("unit", "")
    compact = stat.get("compact", True)

    if isinstance(value, (int, float)):
        num = human_int(value) if compact else f"{int(value):,}"
    else:
        num = str(value)

    prefix = "~" if prov == "estimate" else ""
    core = f"{prefix}{num}"
    if unit:
        core = f"{core} {unit}"
    if prov == "estimate":
        core = f"{core} (est.)"
    elif prov == "target":
        core = f"{core} (target)"
    return core


def stat_is_labeled(stat) -> bool:
    """True if a stat object carries a valid provenance tag (used by verify_outputs).
    Plain strings/numbers are considered author-controlled and pass."""
    if isinstance(stat, dict) and "value" in stat:
        return stat.get("provenance") in PROVENANCE
    return True


# --- Config & deck loading --------------------------------------------------
def load_json(path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def config(name: str) -> dict:
    """Load config/<name>.json (name with or without .json)."""
    name = name if name.endswith(".json") else f"{name}.json"
    return load_json(CONFIG_DIR / name)


def brand() -> dict:
    """Load config/brand.json — the single swappable source of the agency identity
    (name, contact block, philosophy, colours, asset paths)."""
    return config("brand")


def load_deck(path) -> dict:
    """Load a deck.json file (validation lives in verify_outputs)."""
    return load_json(path)


# --- Tiers ------------------------------------------------------------------
def tiers() -> list[dict]:
    return config("tiers")["tiers"]


def tier_info(tier_key: str) -> dict | None:
    key = (tier_key or "").strip().lower()
    for t in tiers():
        if t["key"].lower() == key or t["label"].lower().startswith(key):
            return t
    return None


def tier_est_reach(tier_key: str) -> dict | None:
    """Return an estimate reach band for a tier as a provenance=estimate stat range."""
    t = tier_info(tier_key)
    if not t:
        return None
    return {
        "min": {"value": t["est_reach_per_post_min"], "provenance": "estimate", "unit": "reach/post"},
        "max": {"value": t["est_reach_per_post_max"], "provenance": "estimate", "unit": "reach/post"},
    }


# --- Slug -------------------------------------------------------------------
def slugify(text: str) -> str:
    """'Kopi Senja & Friends' -> 'kopi-senja-friends'."""
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "proposal"


if __name__ == "__main__":  # tiny self-check
    assert rp(1650000000) == "Rp 1.650.000.000", rp(1650000000)
    assert human_int(3379993) == "3.38M", human_int(3379993)
    assert human_int(169439) == "169K", human_int(169439)
    assert slugify("Kopi Senja & Friends") == "kopi-senja-friends"
    assert fmt_stat({"value": 40000, "provenance": "estimate", "unit": "views"}) == "~40K views (est.)"
    assert fmt_stat({"value": 3379993, "provenance": "verified", "unit": "views"}) == "3.38M views"
    print("_util self-check ok")
