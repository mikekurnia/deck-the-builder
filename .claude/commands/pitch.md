---
description: Generate a tailored the agency campaign proposal (deck PDF + editable PPTX + 1-page brief) for a brand. Works from pasted meeting notes or cold from just the brand name.
argument-hint: <Brand name>   (then paste meeting notes, or say the client doesn't know what they want)
---

# /pitch — the agency proposal pipeline

Brand: **$ARGUMENTS**

You are the orchestrator. Keep your own context lean: delegate heavy work, hold only the through-line,
and follow the house rules in `CLAUDE.md`. Read `.claude/skills/agency-brand/SKILL.md` before writing
any copy. Currency is IDR. Lead with the idea, never the price.

Run this pipeline. Pause where told — do not build the full deck before the user confirms the concept.

## 1. Intake  (skill: meeting-notes-intake)
If the user pasted notes, parse them into the structured intake (objective, budget signals, timeline,
must-haves, sensitivities, service hints, open questions, mode). If there are no notes, run **cold /
ideation mode** and infer intent from the brand + category + audience. Confirm any critical gap now.

## 2. Research  (subagent: researcher)
Dispatch the **researcher** subagent with the brand + intake. It returns a tight research brief
(brand, category, audience, competitors, cultural hooks, verified the agency proof, open questions).

## 3. Brainstorm  (skill: brainstorm)
Generate 2–3 distinct, named campaign concepts (insight, narrative, hook, why-it-fits, service mix,
watch-out). Present them to the user.

## 4. ⏸ CONFIRM THE CONCEPT  (STOP)
Ask the user to pick a direction, or auto-pick the strongest and say why — but **wait for his go-ahead**
before building the full deck. This is a house rule.

## 5. Strategy  (skill: strategy)
Turn the chosen concept into the plan: objectives, approach/framework, phases & timeline, per-service
deliverables, KPIs (targets labeled), and an indicative IDR budget frame (agency fee 10%, tax 0.5%,
50/30/20 terms from `config/pricing.json`).

## 6. Talent plan  (skill: talent-roster)
Run `./run.sh tools/query_roster.py --category <cat> [--keyword <niche>] --available --limit 8`.
Build KOL cards (handle, tier, reach as estimate, fit, proof) from the roster; gap-fill thin niches
with manual web-sourced `to-vet` picks (no invented rates). Pull verified `proof[]` for the
Campaign-Wins slide. Add creative crew from `data/roster/crew.csv` if Content Production is in scope.

## 7. Build the deck  (subagent: designer)
Dispatch the **designer** subagent with the strategy + talent plan. It authors `deck.json`, renders
`deck.pdf` + `deck.pptx` + `brief.md`, and runs the verify gate. Each renderer is isolated.

## 8. Review  (skill: proposal-review)
Run the QA pass (deterministic `verify_outputs.py` + the by-eye checklist: narrative-first, brand
fidelity, KOL cards, provenance, investment, consistency, avoid-these). Apply P1 fixes and re-render
until clean.

## 9. Summarize
Tell the user what was produced and where:
```
✓ Proposal ready — proposals/<slug>/
  deck.pdf   (send-ready)   ·   deck.pptx (editable)   ·   brief.md (1-page)
  Concept: <name>  ·  Services: <mix>  ·  KOLs: <n>  ·  Total: Rp …
  Flags: <anything to-vet / to confirm>
```
