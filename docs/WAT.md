# The WAT pattern (Workflows · Agents · Tools)

This repo separates **probabilistic reasoning** from **deterministic execution**.

| Layer | Lives in | Does |
|---|---|---|
| **Workflows** | `.claude/skills/*/SKILL.md`, `.claude/commands/pitch.md` | Plain-language SOPs: objective, inputs, which tool to run, expected output, edge cases. |
| **Agents** | the orchestrator + `.claude/agents/{researcher,designer}.md` | Read the workflow, decide, call tools in order, recover from failures, ask when a gate requires it. |
| **Tools** | `tools/*.py` | Rendering, validation, roster filtering, money formatting — anything that must be exact and repeatable. Covered by `tests/`. |

**Why:** if each model-driven step is 90% reliable, five chained steps land at ~59%. Moving
formatting, rendering and validation into tested scripts keeps the model on the part it is good at —
insight, narrative, copy — and makes the rest boringly correct.

**Self-improvement loop:** when a tool fails, read the error, fix the tool, add a test, update the
workflow that called it. The system should get harder to break after every incident.
