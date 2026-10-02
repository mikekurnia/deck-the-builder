---
name: strategy
description: Convert the chosen campaign concept into the agency's execution plan — objectives, strategic approach, phases, per-service deliverables, timeline, KPIs, and a rough IDR budget frame. The "how we tackle it" backbone of the deck.
---

# Skill: strategy

Turns the approved idea into a plan the deck can render. Runs inline in `/pitch` after the user confirms
the concept.

## Invoke when
The concept is locked. Before talent planning and deck build.

## Inputs
The chosen concept + intake + research. Read `config/services.json`, `config/pricing.json`,
`config/deck_structure.json`. Read `agency-brand` for voice.

## Produce
- **Objectives** — 2–3, phrased as outcomes (awareness / trial / community / conversion).
- **Strategic approach** — the framework: Educate/Inspire/Entertain OR Tease→Launch→Sustain→Amplify.
  3–4 pillars, each with a one-line rationale.
- **Phases & timeline** — each phase: name, timing, focus, deliverables.
- **Deliverables per service** — only for services in the mix; pull menus from `config/services.json`.
- **KPIs** — success metrics. Anything forward-looking is a `target` (labeled as such, never "fact").
- **Budget frame (IDR)** — indicative line items by service. Apply agency fee (10%) and tax (0.5%)
  from `config/pricing.json`; propose 50/30/20 terms. Real KOL costs come from the roster; other
  lines are indicative estimates. Say "final quote after availability check."

## Output format
A structured markdown plan mapping directly onto the deck slide types (`strategic_approach`,
`phases_timeline`, `service_breakdown`, `deliverables`, `investment`).

## Notes
Prices you quote are your offer (author-controlled, shown clean). Claimed metrics (reach, projected
views) are `estimate`/`target` and must be labeled. Never invent a KOL rate.
