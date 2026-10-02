#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# build_example.sh — rebuild the committed Kopi Senja demo end to end.
# Regenerates brand assets + roster, renders every output, runs the verify gate.
# Usage:  ./scripts/build_example.sh [examples/kopi-senja]
# ---------------------------------------------------------------------------
set -euo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE"
EX="${1:-examples/kopi-senja}"

./run.sh tools/make_brand_assets.py
./run.sh tools/import_roster.py
./run.sh tools/verify_outputs.py "$EX/deck.json"          # schema + provenance gate BEFORE render
./run.sh tools/build_deck.py     "$EX/deck.json"
./run.sh tools/html_to_pdf.py    "$EX/deck.html"
./run.sh tools/build_pptx.py     "$EX/deck.json"
./run.sh tools/to_canva.py       "$EX"
./run.sh tools/build_brief.py    "$EX/deck.json"
./run.sh tools/verify_outputs.py "$EX/deck.json"          # and AFTER, to validate the files
