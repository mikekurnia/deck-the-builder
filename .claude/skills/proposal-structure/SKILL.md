---
name: proposal-structure
description: The canonical the agency proposal/deck flow and slide vocabulary, plus rules for adapting it per campaign and the list of quality traps to avoid. Read before assembling deck.json.
---

# Skill: proposal-structure

The agency's proven deck flow, distilled from many real pitch decks. Slide `type` values map
1:1 to the renderer (see `config/deck_structure.json` and `schema/deck.schema.json`).

## Canonical flow (14–18 slides — full order + rules in `config/deck_structure.json`)
1. `cover` — Brand × Agency lockup + the campaign THEME (never an internal title like "KOL Strategy").
2. `about_agency` — who we are + the 5 services (mark the relevant ones `active: true`) + verified stats.
3. `insider_data` — **existing clients only**: real metrics from the account we already run (our edge).
4. `understanding_brand` — their challenge, in their words. Shows we listened.
5. `competitive_landscape` — 3–4 comparable brands + the tactic we adapt (claims sourced).
6. `big_idea` — THE narrative. Name it. Tagline + short story + hook. The heart.
7. `storyline` — the campaign as a narrative arc, beat by beat. SHOW "we build narratives."
8. `strategic_approach` — the framework (Educate/Inspire/Entertain OR Tease→Launch→Sustain→Amplify).
9. `content_pillars` — 3–4 pillars: theme + why + formats.
10. `content_calendar` — day/week × format grid.
11. `content_examples` — DESIGNED post-cards: format + concept + real caption (brand voice) + CTA.
12. `phases_timeline` — phases + timing (fold into the calendar for short campaigns).
13. `service_breakdown` — scope per active service line (drop services not in the mix).
14. `proposed_kols` — KOL CARDS: roster anchors + **fresh to-vet faces**. Plus a 4-box stat strip.
15. `creative_crew` — only if Content Production is in the mix.
16. `moodboard` — aesthetic direction: client photos (hero) + labeled references.
17. `deliverables` — everything the client receives, grouped by service.
18. `campaign_wins` — proof: real past results matched to their category (verified only).
19. `investment` **OR** `scope_summary` — pricing when ready; else "what's included, investment to follow".
20. `why_agency` — "Anyone can book talent. We build narratives." + the 3 pillars.
21. `next_steps` — CTA + the contact block.

Not every slide every time — drop what doesn't earn its place; target 14–18. Lead with craft, not price.

## Adapt per campaign
- **Drop** service sections and slides that don't apply (e.g. no `creative_crew` if no production;
  no `campaign_wins` if you have no verified proof for that category).
- **Order** holds, but you can merge `deliverables` into `service_breakdown` for a short deck.
- **Cold/ideation mode:** lead harder on `big_idea` and `strategic_approach`.
- **Notes mode:** make `understanding_brand` echo their exact language.

## Avoid these (the old-deck failures we beat by construction)
- ❌ A placeholder/stock image repeated across slides. We use no filler imagery.
- ❌ KOLs as plain text. Always cards with handle + tier + reach + fit.
- ❌ A broken/duplicated table of contents. We don't ship a TOC unless it's correct.
- ❌ Missing Big Idea or Investment slide. Both are mandatory.
- ❌ Typos. Proofread copy before rendering.
- ❌ An unverified number shown as fact. Tag every metric `verified | estimate | target`.
