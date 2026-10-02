#!/usr/bin/env python3
"""
import_roster.py — build data/roster/kols.csv from a raw talent export, PII-safe.

Purpose: agencies keep creator lists in messy spreadsheets that often mix public
         profile data with private payout data (bank accounts, phone numbers, ID
         numbers). This tool imports ONLY the public, pitch-relevant fields into the
         roster the factory queries, dedupes creators across campaign rows, and
         normalises tiers / rates / handles / availability.
Output:  data/roster/kols.csv  (name,ig_handle,tiktok_handle,tier,niche,est_reach,rate_idr,city,status,notes)
Usage:   ./run.sh tools/import_roster.py [--source data/roster/sample_kol_source.csv] [--out data/roster/kols.csv]

PII SAFETY (two layers, both covered by tests/test_tools.py):
  1. Allowlist output — the writer only ever emits OUT_COLUMNS. Any other source
     column (bank_account, bank_name, phone, ktp, ...) is dropped, and the dropped
     column names are reported so the operator can see what was stripped.
  2. Refusal — a source file whose NAME says it is a payout/bank export is refused
     before it is even opened. Bank data must never enter the factory.

The shipped sample (data/roster/sample_kol_source.csv) is 100% FICTIONAL and
deliberately includes fake bank_name / bank_account / phone columns to demonstrate
layer 1.
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import ROSTER_DIR  # noqa: E402

DEFAULT_SOURCE = ROSTER_DIR / "sample_kol_source.csv"

# Layer 2: refuse files that are, by name, payout/bank exports.
FORBIDDEN_SOURCE_MARKERS = ("bank", "payout", "rekening", "payment-details")

# Columns we know are PII. Not needed for safety (the output is an allowlist) —
# used to make the strip report explicit.
KNOWN_PII_COLUMNS = {
    "bank", "bank_name", "bank_account", "account_number", "no_rekening",
    "phone", "whatsapp", "email", "ktp", "npwp", "nik", "address",
}

# The ONLY columns that may ever be written.
OUT_COLUMNS = [
    "name", "ig_handle", "tiktok_handle", "tier", "niche",
    "est_reach", "rate_idr", "city", "status", "notes",
]


def is_forbidden_source(path: Path) -> bool:
    n = path.name.lower()
    return any(m in n for m in FORBIDDEN_SOURCE_MARKERS)


def norm_tier(cat: str) -> str:
    c = (cat or "").strip().lower()
    if c.startswith("nano") or c in ("nnao", "almost micro"):
        return "Nano"
    if c.startswith("mikro") or c.startswith("micro"):
        return "Mikro"
    if c.startswith("makro") or c.startswith("macro"):
        return "Makro"
    if c.startswith("mega"):
        return "Mega"
    return ""


def niche_hint(cat: str) -> str:
    """A descriptive (non-tier) category string is a niche hint, e.g. 'Lifestyle', 'Coffee'."""
    c = (cat or "").strip()
    if not c or c.upper() in ("N/A", "NA"):
        return ""
    if norm_tier(c):
        return ""
    return c


def parse_rate(s: str) -> str:
    """'Rp350,000' -> '350000', '500000' -> '500000', '' -> ''. Never invents a rate."""
    digits = re.sub(r"[^0-9]", "", (s or "").strip())
    return digits if digits else ""


def norm_avail(s: str) -> str:
    v = (s or "").strip().lower()
    if v in ("yes", "y", "1", "true", "available"):
        return "available"
    if v in ("no", "n", "0", "false", "not avail", "not available", "x"):
        return "unavailable"
    return ""


def handle_from_url(url: str) -> str:
    """Extract '@name' from an instagram.com/ or tiktok.com/ URL."""
    m = re.search(r"(?:instagram\.com|tiktok\.com)/@?([A-Za-z0-9._]+)", (url or "").strip())
    return "@" + m.group(1) if m else ""


def import_rows(rows: list[dict]) -> list[dict]:
    """Dedupe by normalised name, merging fields across a creator's campaign rows.
    Returns roster rows containing ONLY OUT_COLUMNS keys."""
    merged: dict[str, dict] = collections.OrderedDict()
    for r in rows:
        name = (r.get("kol_name") or "").strip()
        if not name or name.lower() in ("name", "no", "nama"):
            continue
        rec = merged.setdefault(name.lower(), {
            "name": name, "ig_handle": "", "tiktok_handle": "", "tier": "", "city": "",
            "niche": set(), "rate_idr": "", "avail": set(), "campaigns": set(),
        })
        rec["ig_handle"] = rec["ig_handle"] or handle_from_url(r.get("ig_link", ""))
        rec["tiktok_handle"] = rec["tiktok_handle"] or handle_from_url(r.get("tiktok_link", ""))
        rec["tier"] = rec["tier"] or norm_tier(r.get("category", "")) or norm_tier(r.get("tiktok_tier", ""))
        rec["city"] = rec["city"] or (r.get("city") or "").strip()
        for field in ("category", "niche"):
            nh = niche_hint(r.get(field, ""))
            if nh:
                rec["niche"].add(nh)
        rec["rate_idr"] = rec["rate_idr"] or parse_rate(r.get("hj_rate", ""))
        av = norm_avail(r.get("available", ""))
        if av:
            rec["avail"].add(av)
        camp = (r.get("source_campaign") or "").strip()
        if camp:
            rec["campaigns"].add(camp)

    out = []
    for rec in merged.values():
        avail = "available" if "available" in rec["avail"] else (
            "unavailable" if "unavailable" in rec["avail"] else "unknown")
        notes_bits = []
        if avail != "unknown":
            notes_bits.append(f"availability: {avail}")
        camps = sorted(rec["campaigns"])
        if camps:
            notes_bits.append("worked: " + ", ".join(camps[:4]) + (" …" if len(camps) > 4 else ""))
        out.append({
            "name": rec["name"],
            "ig_handle": rec["ig_handle"],
            "tiktok_handle": rec["tiktok_handle"],
            "tier": rec["tier"],
            "niche": "; ".join(sorted(rec["niche"])),
            "est_reach": "",  # derived from tier at query time as an estimate; never baked
            "rate_idr": rec["rate_idr"],  # blank unless real
            "city": rec["city"],
            "status": "vetted",
            "notes": " | ".join(notes_bits),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Import a raw talent export into the roster (PII-safe).")
    ap.add_argument("--source", default=str(DEFAULT_SOURCE), help="raw creator CSV export")
    ap.add_argument("--out", default=str(ROSTER_DIR / "kols.csv"), help="output CSV path")
    args = ap.parse_args()

    src = Path(args.source)
    if is_forbidden_source(src):
        print(f"REFUSING to read {src.name}: looks like a bank/payout export (PII).", file=sys.stderr)
        return 2
    if not src.exists():
        print(f"ERROR: source not found: {src}", file=sys.stderr)
        return 1

    with open(src, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        source_cols = list(reader.fieldnames or [])
        rows = list(reader)

    roster = import_rows(rows)
    dropped = [c for c in source_cols if c.lower() in KNOWN_PII_COLUMNS]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLUMNS, extrasaction="raise")
        w.writeheader()
        w.writerows(roster)

    with_rate = sum(1 for r in roster if r["rate_idr"])
    print(f"Imported {len(roster)} unique creators from {len(rows)} source rows -> {out_path}")
    print(f"  with a known rate: {with_rate} | rest have rate_idr blank (to confirm, never invented)")
    if dropped:
        print(f"  PII columns stripped (never written): {', '.join(dropped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
