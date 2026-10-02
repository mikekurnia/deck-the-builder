---
name: talent-roster
description: How to build the people plan — query the vetted KOL roster, proof-rank picks by past results, pull matching campaign proof, add creative crew, and gap-fill with manual web-sourced (to-vet) picks. Enforces the no-fake-rates and no-PII rules.
---

# Skill: talent-roster

Builds the KOL shortlist + creative crew for the deck. Runs inline in `/pitch` after strategy.

## Invoke when
The service mix is set and you need specific creators + crew.

## The tool (do the filtering deterministically)
```bash
./run.sh tools/query_roster.py --category <cat> --tier Mikro,Makro --available --limit 8
```
- `--category` (beauty/fnb/sports/nightlife/spa/spirits) pulls matching **verified** proof AND biases ranking.
- `--keyword` filters by niche/name/notes (e.g. `--keyword padel`).
- Returns JSON: `kols[]` (name, handles, tier, est_reach band, rate_idr or null, availability),
  `proof[]` (verified past campaigns for the category), `counts`.
- Exit code 3 = zero matches → fall back to manual web-add (below), never an empty KOL slide.

## Sourcing rule — DUAL-SOURCE by default (roster + fresh web faces)
1. **Roster first** — vetted KOLs from `data/roster/kols.csv` (`status: vetted`), imported from the
   raw talent export (`data/roster/sample_kol_source.csv` in the demo). Re-import for freshness any time: `./run.sh tools/import_roster.py`.
2. **Fresh faces from the web** — always bring 2–3 NEW creators the roster doesn't have. The
   researcher discovers them (WebSearch + browse); record them with
   `./run.sh tools/scrape_talent.py --record candidates.json`, which adds them as `status: to-vet`.
   Get query ideas via `./run.sh tools/scrape_talent.py --queries --niche <n> --city Jakarta`.
   Web-sourced creators are `to-vet`, follower counts are `estimate`, and carry **no rate** until confirmed.
3. On the KOL slide, mix both: anchor/proven roster names + fresh to-vet faces (badge them clearly).

## Proof-ranking (the moat)
Use `proof[]` from the query to (a) justify the tier/creator choice and (b) fill the `campaign_wins`
slide with real numbers matched to the client's category. Only `verified` figures go on that slide.

## Formatting into the deck (`proposed_kols` slide)
Each KOL card: `name`, `handle`, `tier`, `reach` (as an ESTIMATE stat from the tier band —
`{"value":30000,"provenance":"estimate","unit":"reach"}`), `fit`, and `proof` (e.g. "Vetted — worked
with the agency"). Add a 4-box `stat_strip` (Platform / Creators / Tiers / Audience).

## Creative crew
Pull from `data/roster/crew.csv`. If empty, propose roles ("Photographer", "MUA", …) with
`name: "To be assigned"` — never invent a person or a rate.

## Hard rules
- **Never invent a rate or a reach number.** Rates come from the roster; reach is a tier ESTIMATE, labeled.
- **Never touch bank PII.** `import_roster.py` writes an allowlist of public columns only (bank/phone columns are stripped and reported) and refuses bank/payout exports by name; bank data never enters a deck.
