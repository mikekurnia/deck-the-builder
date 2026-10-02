---
name: canva-handoff
description: How to move a finished deck into Canva as a fully editable design. Builds deck.canva.pptx (native shapes, real text), hands it to Canva, and covers what survives the trip and what to fix on arrival. Read when the user asks to export, open, or continue a deck in Canva.
---

# Skill: canva-handoff

The bridge from the Proposal Factory to Canva. Run it **after** the deck is built and reviewed.

## Invoke when
the user asks to get a deck into Canva — to hand a client an editable file, to let a designer keep
working on it, or to restyle a deck with Canva's tools.

## Why a PPTX and not a direct push
The Canva connector's `import-design-from-url` only accepts a URL that is **already public**.
A client proposal is confidential, so publishing one to the open internet to make a URL is not an
option — never do it, and never suggest a pastebin or file host as a workaround. Canva does import
a **local PPTX** from Uploads, and a PPTX import keeps text boxes as real, editable text. That is
the handoff.

`deck.pptx` (from `build_pptx.py`) is **not** the file to use — it is one flat image per slide,
which lands in Canva as six uneditable pictures. Use `to_canva.py`.

## Step 1 — build the editable PPTX
```bash
./run.sh tools/to_canva.py proposals/<slug>            # -> proposals/<slug>/deck.canva.pptx
```
It opens the rendered `deck.html`, measures the live DOM, and rebuilds every slide out of native
PowerPoint objects: real text boxes with real runs, rectangles/rounded-rectangles/ellipses for
panels, rules and dots, and pictures with real crops. Nothing is a flattened slide image.

Both PPTX files can coexist — `deck.pptx` for emailing (pixel-identical to the PDF),
`deck.canva.pptx` for editing. Sanity-check with `./run.sh tools/verify_outputs.py`.

**A folder with more than one deck:** name the HTML explicitly and the output follows its name:
```bash
./run.sh tools/to_canva.py proposals/<slug>/event-deck.html \
    --font-map 'Client Display=RealFontName'          # -> event-deck.canva.pptx
```

**`--font-map` (decks outside the agency's template system):** CSS family names pass through unchanged, which
is correct when the CSS name *is* the font (Plus Jakarta Sans, Space Mono, Archivo, Libre Caslon
Display). Supply a mapping only when the CSS name is an alias — e.g. a client deck that calls its display face
`Client Display` while the file is `RealFontName.otf` — because Canva matches fonts by real name.

## Step 2 — get it into Canva
Canva has no API for uploading a local file, so the user does this bit:
1. canva.com → **Uploads** (or drag the file onto the homepage).
2. Drop in `proposals/<slug>/deck.canva.pptx`. Canva converts it to an editable presentation.

Once it exists in Canva, the connector can take over: `search-designs` to find it,
`read-design` to inspect, `edit-design` to change it, `export-design` to pull a PDF back,
`move-item-to-folder` to file it. Use `list-brand-kits` to find the agency's brand kit id.

## What survives, and what to expect on arrival
Verified by rendering the generated PPTX and diffing it against the HTML:
- **Text stays text** — every headline, body, eyebrow and label is editable, with its font, size,
  colour, letter-spacing and alignment.
- **Fonts map by name.** Plus Jakarta Sans, Space Mono, Archivo and Libre Caslon Display are all
  in Canva's library, so they come across as themselves. A face Canva does NOT have (e.g. a
  client's custom display font) will substitute — upload it to Canva as a brand font (Brand Kit →
  Fonts) BEFORE importing, and it matches by name on the way in.
- **Variable-font axes are lost.** PPTX has no axis support, so the 800-weight display face becomes
  plain **bold**, and condensed `font-variation-settings` headlines render at normal width. Both land
  slightly wider/lighter than the PDF; reset by hand in Canva if it matters for final artwork.
- **Shapes keep their geometry** — radii are preserved, so cards stay rounded, pills stay pills
  and storyline dots and KOL avatars stay circles.
- **Translucency, CSS filters and rounded photo crops are baked into the images**, because PPTX
  transparency is unreliable across renderers. They look right, but they are no longer live
  adjustments — to change the contour texture's 24% or a whitened client logo, edit the deck and
  rebuild rather than tweaking in Canva.
- **Slide backgrounds are a full-bleed rectangle** (as well as the real page background), so the
  dark bands survive importers that ignore PPTX page backgrounds. Selecting a dark slide in Canva
  selects that rectangle first.
- **Text can re-wrap.** PowerPoint tracks slightly tighter than the browser, so an occasional line
  that wrapped in the PDF fits on one line here. Skim the deck after import; it is cosmetic.

## Rules
- Never publish a proposal to a public URL to make the connector ingest it. Uploads only.
- Never send `deck.pptx` to Canva and call it editable — check the filename.
- The PDF stays the source of truth for what the client was sent. Canva edits diverge from it;
  if the deck changes for real, change `deck.json` and rebuild so all outputs stay in sync.
