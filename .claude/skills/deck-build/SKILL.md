---
name: deck-build
description: The step-by-step SOP for turning approved proposal content into deck.json and running the tools to produce the PDF, editable PPTX, and 1-page brief. Read before the designer subagent assembles a deck.
---

# Skill: deck-build

How the designer turns everything into files. Deterministic tools do the rendering; you author the
content in `deck.json`.

## Invoke when
Strategy + talent are done and the user has confirmed the concept. This is the final build step.

## Step 1 — scaffold
```bash
./run.sh tools/new_proposal.py "<Brand>" --title "<Campaign Theme>" --accent "#RRGGBB" --language en
```
Creates `proposals/<slug>/deck.json` (a skeleton) and the folder. `--accent` = the client's brand
colour to blend with the agency.

## Step 2 — author deck.json
Fill the skeleton using `proposal-structure` (slide order + vocabulary) and `agency-brand` (voice).
Key rules for numbers (the provenance contract, enforced by verify):
- A **metric claim** (reach, views, followers) is an object: `{"value": 30000, "provenance":
  "estimate|verified|target", "unit": "reach"}`. Renders as `~30K reach (est.)`, `3.38M views`, etc.
- A **display pair** (stat strip, hero stats) is `{"label": "...", "value": "..."}` — author copy, no
  provenance needed.
- **Prices** you quote are plain numbers (your offer), shown clean.
KOL cards: pull from the `talent-roster` query output. Proof slide: only `verified` numbers.
- **Images (moodboard):** give a slide an `images:[{src,kind,span}]` list — `src` is a path (absolute,
  or relative to the proposal folder), `kind` is `client` or `reference` (reference gets a badge),
  `span` is `wide`/`tall`/omitted. `build_deck.py` downscales + embeds them; missing images are dropped.
- **Pricing deferred:** if pricing isn't ready, use a `scope_summary` slide ("what's included —
  investment to follow") INSTEAD of `investment`. Never include both.

## Step 3 — render all three deliverables (each isolated; one failing won't block the others)
```bash
./run.sh tools/build_deck.py   proposals/<slug>/deck.json   # -> deck.html
./run.sh tools/html_to_pdf.py  proposals/<slug>/deck.html   # -> deck.pdf  (send-ready)
./run.sh tools/build_pptx.py   proposals/<slug>/deck.json   # -> deck.pptx (renders each slide from the HTML; matches the PDF exactly)
# Only when the deck is headed for Canva (see the canva-handoff skill) — not part of the default build:
./run.sh tools/to_canva.py     proposals/<slug>             # -> deck.canva.pptx (native shapes; editable in Canva)
./run.sh tools/build_brief.py  proposals/<slug>/deck.json   # -> brief.md  (1-page)
```

## Step 4 — verify before hand-off (mandatory gate)
```bash
./run.sh tools/verify_outputs.py proposals/<slug>/deck.json
```
Must print `✓ VERIFY PASSED`. It checks the schema, that every metric carries provenance, that no
placeholder text leaked, and that the PDF/PPTX are valid files. Fix any failure and re-render.

## Notes
- The PPTX now matches the PDF exactly — each slide is a high-res render of the same HTML. Slides are
  images (not editable text in PowerPoint); to change content, edit `deck.json` and regenerate.
- Assets (logo, texture, fonts) are inlined automatically — don't hand-reference them.
- To output in Bahasa Indonesia, set `meta.language: "id"` and write the copy in Bahasa.
