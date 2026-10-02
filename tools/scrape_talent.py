#!/usr/bin/env python3
"""
scrape_talent.py — fresh-face KOL discovery: query helper + to-vet recorder.

Purpose: the deterministic half of web discovery. The researcher agent does the
         fuzzy part (WebSearch to find creators, WebFetch/browse to read public
         profiles). This tool (a) suggests the search queries, and (b) records the
         candidates the agent found into the roster as `to-vet` (no rates ever),
         so fresh faces persist and show up in future query_roster calls.
Output:  --queries prints search strings; --record merges candidates into kols.csv.
Usage:   ./run.sh tools/scrape_talent.py --queries --niche pilates --city Jakarta
         ./run.sh tools/scrape_talent.py --record candidates.json
         (candidates.json: [{"name","ig_handle","tiktok_handle","followers","niche","sample"}])

Discovery is DUAL-SOURCE: the imported roster (data/roster/kols.csv) + these web finds.
Everything web-sourced is status=to-vet with follower counts treated as estimates.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import ROSTER_DIR  # noqa: E402
from import_roster import OUT_COLUMNS  # reuse the roster schema  # noqa: E402


def tier_from_followers(followers) -> str:
    try:
        n = float(str(followers).replace(",", "").replace("k", "000").replace("K", "000")
                  .replace("m", "000000").replace("M", "000000"))
    except (TypeError, ValueError):
        return ""
    if n < 10_000:
        return "Nano"
    if n < 100_000:
        return "Mikro"
    if n < 1_000_000:
        return "Makro"
    return "Mega"


def suggest_queries(niche: str, city: str) -> list[str]:
    city = city or "Jakarta"
    n = niche or "lifestyle"
    return [
        f"{city} {n} micro influencer instagram",
        f"{n} content creator {city} tiktok",
        f"best {n} KOL Indonesia 2026",
        f'site:instagram.com {n} {city} creator',
        f"rising {n} creator {city} endorsement",
    ]


def load_existing_handles() -> set[str]:
    path = ROSTER_DIR / "kols.csv"
    if not path.exists():
        return set()
    out = set()
    for r in csv.DictReader(open(path, encoding="utf-8")):
        for k in ("name", "ig_handle", "tiktok_handle"):
            v = (r.get(k) or "").strip().lower()
            if v:
                out.add(v)
    return out


def record(candidates: list[dict]) -> int:
    path = ROSTER_DIR / "kols.csv"
    existing = load_existing_handles()
    new_rows = []
    for c in candidates:
        name = (c.get("name") or "").strip()
        ig = (c.get("ig_handle") or "").strip()
        tk = (c.get("tiktok_handle") or "").strip()
        key = name.lower() or ig.lower() or tk.lower()
        if not key or key in existing or ig.lower() in existing or tk.lower() in existing:
            continue
        existing.add(key)
        followers = c.get("followers", "")
        sample = c.get("sample", "")
        notes = "web-sourced · TO VERIFY"
        if followers:
            notes += f" · ~{followers} followers (est.)"
        if sample:
            notes += f" · sample: {sample}"
        new_rows.append({
            "name": name or ig or tk,
            "ig_handle": ig, "tiktok_handle": tk,
            "tier": tier_from_followers(followers),
            "niche": (c.get("niche") or "").strip(),
            "est_reach": "", "rate_idr": "", "city": (c.get("city") or "").strip(),
            "status": "to-vet",
            "notes": notes,
        })
    if new_rows:
        write_header = not path.exists()
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=OUT_COLUMNS)
            if write_header:
                w.writeheader()
            w.writerows(new_rows)
    return len(new_rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fresh-face KOL discovery helper.")
    ap.add_argument("--queries", action="store_true", help="print suggested search queries")
    ap.add_argument("--niche", default="")
    ap.add_argument("--city", default="Jakarta")
    ap.add_argument("--record", metavar="candidates.json", help="record discovered candidates as to-vet")
    args = ap.parse_args()

    if args.queries:
        print(f"Suggested searches for '{args.niche or 'lifestyle'}' in {args.city}:")
        for q in suggest_queries(args.niche, args.city):
            print(f"  • {q}")
        print("\nThen WebFetch/browse each public profile for handle + follower band + a sample post,")
        print("and record with:  ./run.sh tools/scrape_talent.py --record candidates.json")
        return 0

    if args.record:
        data = json.load(open(args.record, encoding="utf-8")) if args.record != "-" else json.load(sys.stdin)
        if not isinstance(data, list):
            print("ERROR: candidates JSON must be a list of objects", file=sys.stderr)
            return 1
        added = record(data)
        print(f"Recorded {added} fresh to-vet creator(s) into the roster "
              f"(skipped duplicates). They now appear in query_roster with status=to-vet.")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
