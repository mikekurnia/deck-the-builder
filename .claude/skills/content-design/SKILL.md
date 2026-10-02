---
name: content-design
description: Turn strategy into CONCRETE deliverables — the storyline, content pillars, a day-by-day content calendar, designed example posts with real captions, and a moodboard direction. This is how we "show the narrative" instead of claiming it.
---

# Skill: content-design

Makes "we'll run a social campaign" tangible. Runs inline after strategy, before deck build.
Read `agency-brand` (voice) + the research/intake first.

## Invoke when
The concept + strategy are locked and you're specifying what actually gets posted.

## Produce these (each maps to a slide type)

### 1. `storyline` — the narrative, shown (this is the differentiator)
The campaign as an arc of **beats**. Each beat: `name`, `what` happens, the audience `feeling`.
4–5 beats. This is the on-page proof that "we build narratives."

### 2. `content_pillars` — 3–4 pillars
Each: `name`, `why` it matters for this brand/audience, `formats` (Reel / Carousel / UGC / Story / GRWM…).

### 3. `content_calendar` — day/week × format
`rows` of `{day, platform, format, content, cta}` across the campaign window. Be concrete about the
posting rhythm; group days for longer campaigns (e.g. "Day 5–7").

### 4. `content_examples` — real post mockups (show, don't tell)
3–6 `posts`, each `{platform, format, concept, caption, cta, image}`. These render as realistic
IG/TikTok post frames (avatar, `@handle`, engagement icons) — so set **`meta.ig_handle`** (e.g.
`@kopisenja.demo`). Rules:
- **Every post gets a real image** so the card isn't blank. `image` = `{src|url, kind}`:
  - Client owns photos → use them (`kind:"client"`, a path). e.g. the client's product shots.
  - No owned photo → **WebSearch a representative reference image** and use its URL
    (`kind:"reference"` → renders a small "reference" tag). The pipeline downloads + downscales it;
    a dead link falls back to the concept as on-cover text, so it never breaks.
- The **caption must be in the brand's real voice** (read `agency-brand` + the client tone) — proves craft.
- `concept` is the one-line visual idea (becomes the on-cover text). Make posts you could publish tomorrow.
- Ride the current **trends** (from competitive-research) where they fit.

### 5. `moodboard` — aesthetic direction (D4: client photos + labeled refs)
- `images`: `[{src, kind}]` — HERO images are the **client's own photos** (`kind:"client"`); add 2–4
  outside references (`kind:"reference"` — they render with a "Reference" badge, so nobody mistakes
  them for our work). Use `span:"wide"|"tall"` for a dynamic grid. The build downscales them.
- `caption` (the one-line direction), `swatches` (hex list — pull the client's palette), `direction`
  (3 bullets: light/texture, palette, energy).

## Rules
- Captions and concepts are OUR proposed creative — author-controlled, shown clean. But any metric
  (predicted reach/views) is an `estimate`/`target` stat and must be labeled.
- Moodboard: never present a web reference as our own shot — the "Reference" badge handles this.
- Concrete beats generic. "3 ways to style the Ivy Bra" > "styling content."
