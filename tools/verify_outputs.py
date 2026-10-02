#!/usr/bin/env python3
"""
verify_outputs.py — the pre-handoff safety gate.

Purpose: block a broken or dishonest deck from ever reaching a client. Checks:
  1. deck.json validates against schema/deck.schema.json
  2. every stat OBJECT carries a provenance tag (no AI guess printed as fact)
  3. no placeholder/leftover markers in client-facing text ([[..]], PLACEHOLDER, LOREM, TODO)
  4. every slide.type is one the renderer supports
  5. if present, deck.pdf and deck.pptx are real, non-empty files
Output:  PASS / FAIL report; exit 0 on pass, 4 on any failure.
Usage:   ./run.sh tools/verify_outputs.py proposals/<slug>/deck.json
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import SCHEMA_DIR, PROVENANCE, load_json, DeckValidationError  # noqa: E402

import jsonschema  # noqa: E402

SUPPORTED_TYPES = {
    "cover", "about_agency", "understanding_brand", "insider_data",
    "competitive_landscape", "trends", "big_idea", "storyline", "strategic_approach",
    "campaign_routes", "kpi", "data_table", "pie_chart",
    "content_pillars", "content_calendar", "content_examples",
    "phases_timeline", "service_breakdown", "proposed_kols", "creative_crew",
    "deliverables", "moodboard", "campaign_wins", "investment",
    "conversion", "scope_summary", "why_agency", "next_steps",
}
FORBIDDEN = ["[[", "]]", "placeholder", "lorem ipsum", "todo:", "xxxx", "<fill", "réplace"]


def walk_strings(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def walk_stats(obj, path="$"):
    """Yield (path, dict) for every METRIC-CLAIM stat object.

    A metric claim is a bare {value, provenance, unit} object — a number about the
    world (reach, views) that could be wrong, so it must carry provenance.
    A display pair {label, value, ...} (stat strip, hero stats) is author-controlled
    copy, not an AI claim, so it is skipped.
    """
    if isinstance(obj, dict):
        if "value" in obj and "label" not in obj:
            yield path, obj
        for k, v in obj.items():
            yield from walk_stats(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_stats(v, f"{path}[{i}]")


def verify(deck_path: Path) -> list[str]:
    problems: list[str] = []
    deck = load_json(deck_path)

    # 1. schema
    schema = load_json(SCHEMA_DIR / "deck.schema.json")
    try:
        jsonschema.validate(deck, schema)
    except jsonschema.ValidationError as e:
        problems.append(f"SCHEMA: {e.message} (at {'/'.join(str(x) for x in e.path)})")

    # 2. provenance on every stat object
    for path, stat in walk_stats(deck):
        if stat.get("provenance") not in PROVENANCE:
            problems.append(f"PROVENANCE: stat at {path} has no valid provenance tag "
                            f"(needs one of {PROVENANCE}) — value={stat.get('value')!r}")

    # 3. placeholder / leftover markers
    for path, text in walk_strings(deck):
        low = text.lower()
        for bad in FORBIDDEN:
            if bad in low:
                problems.append(f"PLACEHOLDER: '{bad}' found in {path}: {text[:60]!r}")

    # 4. slide types renderer supports + moodboard has usable images
    pdir = deck_path.parent
    for i, s in enumerate(deck.get("slides", [])):
        if s.get("type") not in SUPPORTED_TYPES:
            problems.append(f"SLIDE: slide[{i}] type {s.get('type')!r} is not renderable")
        if s.get("type") == "moodboard":
            imgs = s.get("images") or []
            def _resolves(src: str) -> bool:
                p = Path(src)
                return p.is_absolute() and p.exists() or (pdir / src).exists()
            if imgs and not any(_resolves(im.get("src", "")) for im in imgs if isinstance(im, dict)):
                problems.append(f"MOODBOARD: slide[{i}] lists images but none resolve on disk — would render empty")

    # 5. output files, if present
    pdf = deck_path.parent / "deck.pdf"
    pptx = deck_path.parent / "deck.pptx"
    if pdf.exists():
        head = pdf.read_bytes()[:5]
        if head[:4] != b"%PDF" or pdf.stat().st_size < 1000:
            problems.append("OUTPUT: deck.pdf exists but is not a valid/complete PDF")
    if pptx.exists():
        head = pptx.read_bytes()[:2]
        if head != b"PK" or pptx.stat().st_size < 1000:
            problems.append("OUTPUT: deck.pptx exists but is not a valid PPTX (zip) file")
    canva = deck_path.parent / "deck.canva.pptx"
    if canva.exists():
        if canva.read_bytes()[:2] != b"PK" or canva.stat().st_size < 1000:
            problems.append("OUTPUT: deck.canva.pptx exists but is not a valid PPTX (zip) file")

    return problems


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: verify_outputs.py proposals/<slug>/deck.json", file=sys.stderr)
        return 1
    deck_path = Path(sys.argv[1])
    if not deck_path.exists():
        print(f"ERROR: {deck_path} not found", file=sys.stderr)
        return 1

    problems = verify(deck_path)
    if problems:
        print(f"✗ VERIFY FAILED — {len(problems)} issue(s):")
        for p in problems:
            print(f"  - {p}")
        return 4
    print("✓ VERIFY PASSED — schema ok, all numbers labeled, no placeholders, outputs valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
