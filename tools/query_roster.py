#!/usr/bin/env python3
"""
query_roster.py — shortlist KOLs from the roster + pull matching proof.

Purpose: the talent step's engine. Filter data/roster/kols.csv by tier / niche /
         availability / keyword, rank by actionability, attach an ESTIMATE reach
         band from the tier, and pull VERIFIED past-campaign proof for the
         client's category (for the Campaign-Wins slide and to justify picks).
Output:  JSON (default) or a readable table (--table) to stdout.
Usage:   ./run.sh tools/query_roster.py --category sports --tier Mikro,Makro --available --limit 8 --json

If zero KOLs match, exits 3 (EmptyRosterError) so the caller falls back to a
manual web-sourced 'to-vet' pick — never an empty KOL slide.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import ROSTER_DIR, config, tier_est_reach, EmptyRosterError  # noqa: E402


def load_kols() -> list[dict]:
    path = ROSTER_DIR / "kols.csv"
    if not path.exists():
        print(f"ERROR: roster not found at {path}. Run: ./run.sh tools/import_roster.py", file=sys.stderr)
        raise SystemExit(1)
    return list(csv.DictReader(open(path, encoding="utf-8")))


def matches(row: dict, keywords: list[str]) -> bool:
    if not keywords:
        return True
    hay = " ".join([
        row.get("name", ""), row.get("niche", ""), row.get("notes", ""),
        row.get("ig_handle", ""), row.get("tiktok_handle", ""),
    ]).lower()
    return all(k.lower() in hay for k in keywords)


def rank_key(row: dict):
    avail = 0 if "availability: available" in row.get("notes", "") else 1
    has_rate = 0 if row.get("rate_idr", "").strip() else 1
    return (avail, has_rate, row.get("name", "").lower())


def proof_for_category(category: str) -> list[dict]:
    if not category:
        return []
    out = []
    for c in config("campaigns")["campaigns"]:
        if c["category"].lower() != category.lower():
            continue
        if not c.get("achieved_views"):
            continue
        mult = round(c["achieved_views"] / c["goal_views"], 2) if c.get("goal_views") else None
        out.append({**c, "multiplier": mult})
    out.sort(key=lambda c: (c.get("multiplier") or 0, c["achieved_views"]), reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Shortlist KOLs + pull matching proof.")
    ap.add_argument("--keyword", "--niche", dest="keywords", action="append", default=[],
                    help="substring filter (repeatable) across name/niche/notes/handles")
    ap.add_argument("--tier", default="", help="comma-separated tiers: Nano,Mikro,Makro,Mega")
    ap.add_argument("--category", default="", help="client category for proof matching: beauty/fnb/sports/nightlife/spa/spirits")
    ap.add_argument("--available", action="store_true", help="only KOLs marked available")
    ap.add_argument("--with-rate", action="store_true", help="only KOLs with a known rate")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--table", action="store_true", help="human table instead of JSON")
    args = ap.parse_args()

    tiers_wanted = {t.strip().lower() for t in args.tier.split(",") if t.strip()}
    rows = load_kols()

    filtered = []
    for r in rows:
        if tiers_wanted and r.get("tier", "").lower() not in tiers_wanted:
            continue
        if args.available and "availability: available" not in r.get("notes", ""):
            continue
        if args.with_rate and not r.get("rate_idr", "").strip():
            continue
        if not matches(r, args.keywords):
            continue
        filtered.append(r)

    filtered.sort(key=rank_key)
    total = len(filtered)
    shortlist = filtered[: args.limit]

    if total == 0:
        msg = "No roster KOLs matched — fall back to a manual web-sourced (to-vet) pick."
        if args.table:
            print(msg)
            return 3
        print(json.dumps({"error": "EmptyRosterError", "message": msg,
                          "query": vars(args), "kols": [], "proof": proof_for_category(args.category)},
                         indent=2, ensure_ascii=False))
        return 3

    def shape(r: dict) -> dict:
        reach = tier_est_reach(r.get("tier", ""))
        return {
            "name": r["name"],
            "ig_handle": r.get("ig_handle", ""),
            "tiktok_handle": r.get("tiktok_handle", ""),
            "tier": r.get("tier", ""),
            "niche": r.get("niche", ""),
            "est_reach": reach,  # provenance=estimate band; render as 'est.'
            "rate_idr": int(r["rate_idr"]) if r.get("rate_idr", "").strip().isdigit() else None,
            "status": r.get("status", "vetted"),
            "available": "availability: available" in r.get("notes", ""),
            "notes": r.get("notes", ""),
        }

    result = {
        "query": {"keywords": args.keywords, "tier": args.tier, "category": args.category,
                  "available_only": args.available},
        "counts": {"matched": total, "returned": len(shortlist)},
        "kols": [shape(r) for r in shortlist],
        "proof": proof_for_category(args.category),
    }

    if args.table:
        print(f"Matched {total} KOLs (showing {len(shortlist)}):\n")
        for k in result["kols"]:
            rate = f"Rp {k['rate_idr']:,}".replace(",", ".") if k["rate_idr"] else "rate TBD"
            av = "✓avail" if k["available"] else "  ?   "
            print(f"  {av}  {k['name'][:28]:28}  {k['tier'] or '-':6}  {k['ig_handle'][:22]:22}  {rate}")
        if result["proof"]:
            print(f"\nProof (verified, category={args.category}):")
            for p in result["proof"][:5]:
                m = f"{p['multiplier']}x" if p.get("multiplier") else "—"
                print(f"  {p['brand'][:34]:34}  goal {p['goal_views']:>9,} -> {p['achieved_views']:>9,}  ({m})")
        return 0

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
