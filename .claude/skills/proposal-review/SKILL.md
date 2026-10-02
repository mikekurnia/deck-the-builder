---
name: proposal-review
description: The final QA gate before a deck goes to the client. Checks brand fidelity, the narrative-first principle, number provenance, internal consistency, and the "avoid these" list. Runs inline after the deck is built.
---

# Skill: proposal-review

The last look before hand-off. Runs inline in `/pitch` after `deck-build`.

## Invoke when
`deck.pdf`, `deck.pptx`, and `brief.md` exist and `verify_outputs.py` has passed.

## Do this first (deterministic gate)
```bash
./run.sh tools/verify_outputs.py proposals/<slug>/deck.json
```
If it fails, stop and fix — do not review further until it passes.

## Then review by eye (read the deck.pdf / deck.json)
Score each; anything failing is a fix, not a note.
1. **Narrative-first** — does the deck lead with the Big Idea, not a price list? Is the idea named and sharp?
2. **Brand fidelity** — white/ink surfaces, the primary + accent from `templates/tokens.css`, Plus Jakarta Sans
   headlines, Space Mono eyebrows, contour texture on dark bands, correct contact block.
3. **KOLs as cards** — every proposed creator has handle + tier + reach (est.) + fit. No plain-text lists.
4. **Provenance** — every metric is labeled; no AI guess printed as fact; proof slide uses verified only.
5. **Investment** — IDR line items, agency fee + tax, 50/30/20 terms, honest "final after availability" note.
6. **Consistency** — service mix on the cover/about matches the breakdown; KOL count matches the stat strip;
   totals add up; dates align across phases/timeline.
7. **Avoid-these** — no placeholder imagery, no typos, no broken/duplicated TOC, Big Idea + Investment present.
8. **Per-client blend** — `meta.accent_hex` set to the client's colour so it reads as Agency × client.

## Output format
`[P1|P2|P3] slide/field — issue — fix`, then a verdict: APPROVE / APPROVE WITH FIXES / REQUEST CHANGES,
plus one line on what to tweak. P1 blocks hand-off.

## Notes
This is a read-only QA pass; propose fixes, let the designer apply them, then re-run the deterministic
gate. When clean, tell the user what was produced and where.
