---
name: brainstorm
description: The idea engine. Generate 2–3 distinct, named campaign concepts for a brand — each with a core insight, a hook, why it fits, and a rough service mix. Leads in cold mode, sharpens the client's ask in notes mode.
---

# Skill: brainstorm

Where the narrative comes from. Runs inline in `/pitch` after research.

## Invoke when
After the researcher returns its brief and before strategy. the user will pick a direction (or you
auto-pick the strongest and say why) before the full deck is built.

## Inputs
The intake (from meeting-notes-intake) + the research brief (brand, category, audience, competitors,
cultural hooks). Read `agency-brand` first for voice.

## Produce 2–3 concepts. Each concept:
- **Name** — a short, ownable campaign name (this becomes the Big Idea).
- **Insight** — the human truth about the audience the idea is built on.
- **Narrative** — 2–3 sentences: the story we tell, tied to a lifestyle, not the product.
- **Hook** — one quotable line a creator could actually say.
- **Why it fits** — why THIS brand, THIS audience, now.
- **Service mix** — which of the 5 services the idea needs (only the ones that fit).
- **Risk / watch-out** — one honest caveat.

## Modes
- **Cold mode:** you lead. Push distinct territories, not three flavours of one idea.
- **Notes mode:** sharpen and elevate what the client asked for; don't ignore their must-haves.

## Output format
A markdown list of the concepts, then a one-line recommendation ("Strongest = X because …").
Always tie back to "we build narratives."

## Notes
Keep concepts genuinely different (different insight, different mechanic). Don't propose a fourth as
filler. After the user confirms, hand the chosen concept to `strategy`.
