#!/usr/bin/env python3
"""
build_brief.py — write the 1-page text brief from deck.json.

Purpose: the send-ready one-pager the account lead can paste into WhatsApp/email — the deck's
         argument in plain text. Deterministic, so it always matches the deck.
Output:  <proposal_dir>/brief.md
Usage:   ./run.sh tools/build_brief.py proposals/<slug>/deck.json
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import rp, fmt_stat, load_deck, brand  # noqa: E402


def find(slides, t):
    for s in slides:
        if s.get("type") == t:
            return s
    return {}


def build(deck_path: Path) -> Path:
    deck = load_deck(deck_path)
    meta, slides = deck["meta"], deck["slides"]
    idea = find(slides, "big_idea")
    appr = find(slides, "strategic_approach")
    kols = find(slides, "proposed_kols")
    inv = find(slides, "investment")
    svc = find(slides, "service_breakdown")

    agency = brand()
    c = agency["contact"]
    L = []
    L.append(f"# {meta['brand']} × {agency['name']} — 1-Page Brief")
    L.append(f"**{meta.get('campaign_title','')}**  ·  {meta.get('date','2026')}  ·  Prepared for {meta['brand']}\n")

    if idea:
        L.append(f"## The Big Idea — {idea.get('idea_name', idea.get('title',''))}")
        if idea.get("tagline"):
            L.append(f"*{idea['tagline']}*")
        if idea.get("narrative"):
            L.append(idea["narrative"])
        if idea.get("hook"):
            L.append(f"> “{idea['hook']}”")
        L.append("")

    if appr:
        L.append(f"## How We Tackle It — {appr.get('framework', appr.get('title',''))}")
        for i, p in enumerate(appr.get("pillars", []), 1):
            L.append(f"{i}. **{p.get('label','')}** — {p.get('desc','')}")
        L.append("")

    if svc:
        L.append("## Service Mix")
        for s in svc.get("services", []):
            L.append(f"- **{s.get('name','')}** — {s.get('tagline','')}")
        L.append("")

    if kols:
        L.append(f"## Proposed KOLs ({len(kols.get('kols', []))} shown)")
        for k in kols.get("kols", []):
            reach = f" · reach {fmt_stat(k['reach'])}" if k.get("reach") else ""
            L.append(f"- **{k.get('name','')}** {k.get('handle','')} · {k.get('tier','')}{reach} — {k.get('fit','')}")
        L.append("")

    if inv:
        L.append("## Investment (IDR)")
        for li in inv.get("line_items", []):
            est = " (est.)" if li.get("provenance") == "estimate" else ""
            L.append(f"- {li.get('label','')}: {rp(li.get('amount',0))}{est}")
        if inv.get("total") is not None:
            L.append(f"- **Total: {rp(inv['total'])}**")
        terms = "  ·  ".join(f"{t.get('pct')}% {t.get('label')}" for t in inv.get("terms", []))
        if terms:
            L.append(f"- Terms: {terms}")
        if inv.get("note"):
            L.append(f"- _{inv['note']}_")
        L.append("")

    L.append(f"## Why {agency['short_name']}")
    pillars = " · ".join(p["label"] for p in agency.get("pillars", []))
    L.append(f"{agency['philosophy']} {pillars}.\n")
    L.append(f"**{agency['name']}** · {c['address']} · IG {c['ig']} · WA {c['wa']} · {c['email']}")

    out = deck_path.parent / "brief.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: build_brief.py proposals/<slug>/deck.json", file=sys.stderr)
        return 1
    deck_path = Path(sys.argv[1])
    if not deck_path.exists():
        print(f"ERROR: {deck_path} not found", file=sys.stderr)
        return 1
    out = build(deck_path)
    print(f"Wrote {out} ({len(out.read_text().splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
