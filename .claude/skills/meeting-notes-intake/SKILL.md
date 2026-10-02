---
name: meeting-notes-intake
description: Parse messy meeting notes (or a cold brief with no notes) into a structured intake so the pipeline builds around what the client actually wants. Handles both notes mode and cold/ideation mode.
---

# Skill: meeting-notes-intake

Turn whatever the user pastes into a clean intake the rest of the pipeline builds on.

## Invoke when
At the start of `/pitch`, before research. the user either pastes notes or says the client "doesn't
know what they want yet."

## Two modes
- **Notes mode** — notes are present. Extract intent; quote their own phrasing where useful.
- **Cold / ideation mode** — no notes, or the client is undecided. Infer intent from the brand,
  category, and audience; flag that the big idea is the agency-originated.

## Produce this intake (structured)
- **Brand + category + market** (default: Indonesia / Jakarta).
- **Objective** — what success looks like (awareness / launch / conversion / repositioning).
- **Budget signals** — any numbers or ranges hinted; else "not stated → propose indicative".
- **Timeline** — dates, launch windows, seasonality/cultural hooks (Ramadan, year-end, etc.).
- **Must-haves** — non-negotiables (specific channels, a spokesperson, a product).
- **Brand sensitivities** — tone limits, competitors to avoid, compliance.
- **Service hints** — which of the 5 services the notes point to (or infer for cold mode).
- **Open questions** — gaps or contradictions to confirm with the user before the full deck.
- **Mode** — `notes` or `cold`.

## Output format
A short markdown block with the fields above. If notes contradict themselves or leave a critical gap
(budget, timeline, objective), list it under Open questions and ask the user before building the deck.

## Notes
Never invent a budget or a hard commitment the client didn't make. In cold mode, say so plainly so
the big idea is presented as our proposal, not their request.
