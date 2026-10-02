---
name: competitive-research
description: Read the Indonesian category landscape and distil 2-4 "moves we adapt" (not a competitor roll-call), plus current IG/TikTok trends. Feeds the competitive_landscape and trends slides. Every claim sourced or marked inferred.
---

# Skill: competitive-research

Shows the client we know the category and we're current — as a sharp POV, not a competitor lecture.
Part of the researcher's job; runs during research.

## Invoke when
After intake, alongside brand research, before ideation.

## Inputs
The brand + category + intake. Read `config/competitors.json` for starting points (hypotheses only).

## Part 1 — The landscape (MOVE-CENTRIC, not a competitor list)
Study 3–4 comparables (global + **at least one Indonesian/local** brand) — but the deck does NOT list
each competitor's strengths. Instead, synthesise:
1. **One-line market read** — what's happening in the Indonesian [category] scene right now.
2. **2–4 "moves we adapt"** — each a tactic we'll borrow and bend for THIS client. For each: the
   `move` (headline), `why` it works, `seen_in` (a light evidence line naming 1–2 brands), `source`.
Competitors appear only as brief evidence, never as the headline. **Source or mark inferred** every claim.

Output (maps to `competitive_landscape`):
```json
{"type":"competitive_landscape","title":"What we adapt from the [category] landscape",
 "landscape":"one-line market read",
 "moves":[{"move":"Own a philosophy, not a product feed","why":"...","seen_in":"Brand X, Brand Y","source":"<source, date>; observed"}]}
```

## Part 2 — Trends now (stay sharp)
WebSearch current **Instagram/TikTok trends for the category** (formats, sounds, hashtags, challenges).
Pick 3–4 that fit the brand. For each: `name`, `what` it is, `our_play` (how this brand rides it),
`source`. **Date it** — trends age fast.

Output (maps to `trends`):
```json
{"type":"trends","title":"What's trending — and how we ride it","as_of":"Jul 2026",
 "trends":[{"name":"GRWM","what":"...","our_play":"...","source":"TikTok trend reports, Jul 2026"}]}
```

## Notes
Don't knock competitors — borrow from them. Re-pull trends every pitch (they're dated). Feed the trends
into the content calendar + example posts too, so the plan actually rides them.
