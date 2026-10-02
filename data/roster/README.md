# Roster (FICTIONAL demo data)

Every person in this folder is invented. Handles follow the `@demo.creatorNN` pattern and do not
point at real accounts.

## `sample_kol_source.csv` — the raw "export" (input)
Mimics the messy spreadsheet an agency actually keeps: one row per creator *per campaign*, mixed
tier/niche categories, `Rp3,000,000`-style rates, and — deliberately — **PII columns**
(`bank_name`, `bank_account`, `phone`) filled with obviously fake values.

## `kols.csv` — the roster the factory queries (output)
Built by `./run.sh tools/import_roster.py`. Columns (an allowlist — nothing else can be written):
`name, ig_handle, tiktok_handle, tier, niche, est_reach, rate_idr, city, status, notes`
- 27 source rows dedupe to 25 creators; the bank/phone columns are stripped and reported.
- `tier` = Nano / Mikro / Makro / Mega. `est_reach` stays blank on purpose — it is derived from the
  tier at query time and always rendered as an estimate.
- `rate_idr` is blank unless a rate was on file. **Never invent a rate.**
- `status` = `vetted` (imported) or `to-vet` (web-sourced via `scrape_talent.py --record`).

Query it: `./run.sh tools/query_roster.py --keyword coffee --category fnb --available --limit 8 --table`

## `crew.csv` — creative crew (fillable template, sample rows only)
Columns: `name, role, style, rate_idr, city, contact, status, notes`.
