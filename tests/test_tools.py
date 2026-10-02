"""
pytest suite for the deterministic tools. Focus: the pure functions where a silent
bug would quietly corrupt a client deck (money, slugs, number provenance), the
roster filtering, the PII-exclusion guarantee, and the verify gate.

Run: ./.venv/bin/python -m pytest tests/ -q
"""
import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "tools"))
sys.path.insert(0, str(BASE / "templates"))

import _util  # noqa: E402
import import_roster  # noqa: E402
import query_roster  # noqa: E402
import verify_outputs  # noqa: E402
import prep_images  # noqa: E402


# ---- money & formatting ----------------------------------------------------
def test_rp_indonesian_thousands():
    assert _util.rp(1650000000) == "Rp 1.650.000.000"
    assert _util.rp(500000) == "Rp 500.000"
    assert _util.rp(0) == "Rp 0"

def test_rp_bad_input_is_safe():
    assert _util.rp("not a number") == "Rp -"

def test_human_int():
    assert _util.human_int(3379993) == "3.38M"
    assert _util.human_int(169439) == "169K"
    assert _util.human_int(15000) == "15K"
    assert _util.human_int(880) == "880"

def test_slugify():
    assert _util.slugify("Kopi Senja & Friends") == "kopi-senja-friends"
    assert _util.slugify("  Multiple   Spaces ") == "multiple-spaces"
    assert _util.slugify("!!!") == "proposal"


# ---- provenance rendering (the honesty contract) ---------------------------
def test_fmt_stat_verified_is_clean():
    assert _util.fmt_stat({"value": 3379993, "provenance": "verified", "unit": "views"}) == "3.38M views"

def test_fmt_stat_estimate_is_labeled():
    assert _util.fmt_stat({"value": 40000, "provenance": "estimate", "unit": "reach"}) == "~40K reach (est.)"

def test_fmt_stat_target_is_labeled():
    assert _util.fmt_stat({"value": 500000, "provenance": "target", "unit": "views"}) == "500K views (target)"

def test_fmt_stat_plain_passthrough():
    assert _util.fmt_stat("7.4M+") == "7.4M+"

def test_stat_is_labeled():
    assert _util.stat_is_labeled({"value": 1, "provenance": "estimate"}) is True
    assert _util.stat_is_labeled({"value": 1}) is False           # object w/ value but no provenance
    assert _util.stat_is_labeled("plain") is True                  # author-controlled string


# ---- import_roster helpers -------------------------------------------------
def test_norm_tier():
    assert import_roster.norm_tier("Mikro") == "Mikro"
    assert import_roster.norm_tier("micro") == "Mikro"
    assert import_roster.norm_tier("Nnao") == "Nano"      # typo tolerated
    assert import_roster.norm_tier("Lifestyle") == ""     # niche string, not a tier

def test_parse_rate_never_invents():
    assert import_roster.parse_rate("Rp350,000") == "350000"
    assert import_roster.parse_rate("500000") == "500000"
    assert import_roster.parse_rate("") == ""             # blank stays blank, never a made-up number

def test_handle_from_url():
    assert import_roster.handle_from_url("https://www.instagram.com/demo.creator01") == "@demo.creator01"
    assert import_roster.handle_from_url("https://www.tiktok.com/@demo.creator02") == "@demo.creator02"
    assert import_roster.handle_from_url("") == ""


# ---- PII exclusion (security regression guard) -----------------------------
def test_import_refuses_bank_file(monkeypatch, tmp_path):
    out = tmp_path / "kols.csv"
    monkeypatch.setattr(sys, "argv",
                        ["import_roster.py", "--source", "/x/kol-bank-accounts.csv", "--out", str(out)])
    assert import_roster.main() == 2          # refused before reading
    assert not out.exists()

def test_import_never_leaks_bank_columns(monkeypatch, tmp_path):
    # A profiles-style fixture that ALSO carries bank PII columns the importer must ignore.
    src = tmp_path / "kol-profiles.csv"
    with open(src, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kol_name", "category", "ig_link", "tiktok_link", "tiktok_tier",
                    "hj_rate", "available", "source_sheet", "source_campaign",
                    "bank", "no_rekening"])
        w.writerow(["Test Creator", "Mikro", "https://instagram.com/testcreator", "", "",
                    "500000", "Yes", "sheet", "Coffee Launch", "FAKEBANK", "9999000011"])
    out = tmp_path / "kols.csv"
    monkeypatch.setattr(sys, "argv",
                        ["import_roster.py", "--source", str(src), "--out", str(out)])
    assert import_roster.main() == 0

    text = out.read_text(encoding="utf-8")
    header = out.read_text(encoding="utf-8").splitlines()[0].split(",")
    # No bank field names, no bank account number, no bank name in the output — ever.
    assert "9999000011" not in text
    assert "no_rekening" not in header and "bank" not in header
    assert "FAKEBANK" not in text
    # The legitimate creator data DID come through.
    assert "Test Creator" in text and "@testcreator" in text and "500000" in text


# ---- query_roster ----------------------------------------------------------
def test_proof_for_category_is_verified_and_sorted():
    proof = query_roster.proof_for_category("sports")
    assert proof, "expected sports proof from config/campaigns.json"
    # sorted by multiplier desc; the 2.5x sample (Court Days) should lead
    assert proof[0]["brand"].startswith("Sample Brand E")
    assert all(p["category"] == "sports" for p in proof)

def test_matches_keyword_logic():
    row = {"name": "Rara Demo", "niche": "", "notes": "worked: Coffee Launch", "ig_handle": "@demo.creator01", "tiktok_handle": ""}
    assert query_roster.matches(row, ["coffee"]) is True
    assert query_roster.matches(row, ["beauty"]) is False
    assert query_roster.matches(row, []) is True


# ---- verify_outputs gate ---------------------------------------------------
def _write_deck(tmp_path, slides):
    d = tmp_path / "deck.json"
    d.write_text(json.dumps({"meta": {"brand": "X", "campaign_title": "Y"}, "slides": slides}),
                 encoding="utf-8")
    return d

def test_verify_passes_clean_deck(tmp_path):
    slides = [{"type": "cover"}, {"type": "big_idea"}, {"type": "next_steps"}]
    assert verify_outputs.verify(_write_deck(tmp_path, slides)) == []

def test_verify_catches_unlabeled_metric(tmp_path):
    slides = [{"type": "cover"}, {"type": "big_idea"},
              {"type": "proposed_kols", "kols": [{"name": "A", "reach": {"value": 40000}}]}]
    problems = verify_outputs.verify(_write_deck(tmp_path, slides))
    assert any("PROVENANCE" in p for p in problems)

def test_verify_allows_display_pair(tmp_path):
    # {label, value} is author copy, not a metric claim — must NOT be flagged.
    slides = [{"type": "cover"}, {"type": "big_idea"},
              {"type": "about_agency", "stats": [{"label": "Views", "value": "7.4M+"}]}]
    assert verify_outputs.verify(_write_deck(tmp_path, slides)) == []

def test_verify_catches_placeholder(tmp_path):
    slides = [{"type": "cover", "title": "[[FILL THIS IN]]"}, {"type": "big_idea"}, {"type": "next_steps"}]
    problems = verify_outputs.verify(_write_deck(tmp_path, slides))
    assert any("PLACEHOLDER" in p for p in problems)

def test_verify_catches_unknown_slide_type(tmp_path):
    slides = [{"type": "cover"}, {"type": "big_idea"}, {"type": "banana"}]
    problems = verify_outputs.verify(_write_deck(tmp_path, slides))
    assert any("SLIDE" in p or "SCHEMA" in p for p in problems)


# ---- Phase 2: new slide types + image pipeline -----------------------------
def test_verify_accepts_phase2_types(tmp_path):
    slides = [{"type": "cover"},
              {"type": "insider_data"}, {"type": "competitive_landscape"},
              {"type": "trends"}, {"type": "storyline"}, {"type": "content_pillars"},
              {"type": "content_calendar"}, {"type": "content_examples"},
              {"type": "scope_summary"}, {"type": "next_steps"}]
    assert verify_outputs.verify(_write_deck(tmp_path, slides)) == []

def test_prep_images_bad_url_returns_none():
    # .invalid is reserved (RFC 2606) — DNS fails fast; must degrade to None, never raise.
    assert prep_images.image_data_uri("https://nope.invalid/x.jpg") is None

def test_verify_flags_empty_moodboard(tmp_path):
    slides = [{"type": "cover"}, {"type": "big_idea"},
              {"type": "moodboard", "images": [{"src": "/nope/missing.jpg", "kind": "client"}]}]
    problems = verify_outputs.verify(_write_deck(tmp_path, slides))
    assert any("MOODBOARD" in p for p in problems)

def test_prep_images_downscales(tmp_path):
    from PIL import Image
    big = tmp_path / "big.png"
    Image.new("RGB", (3200, 2000), (200, 190, 180)).save(big)
    uri = prep_images.image_data_uri(str(big))
    assert uri and uri.startswith("data:image/jpeg;base64,")
    # downscaled long edge <= MAX_PX means the encoded payload is far smaller than a 3200px raw
    assert len(uri) < 400_000

def test_prep_images_missing_returns_none():
    assert prep_images.image_data_uri("/definitely/not/here.jpg") is None


# ---- PII strip on the SHIPPED sample (fake bank_account / phone columns) -----
def test_shipped_sample_has_pii_and_import_strips_it(monkeypatch, tmp_path, capsys):
    src = BASE / "data/roster/sample_kol_source.csv"
    src_text = src.read_text(encoding="utf-8")
    src_header = src_text.splitlines()[0].split(",")
    # The demo input really does carry PII-shaped columns...
    assert {"bank_name", "bank_account", "phone"} <= set(src_header)
    bank_values = [r["bank_account"] for r in csv.DictReader(open(src, encoding="utf-8"))]
    phones = [r["phone"] for r in csv.DictReader(open(src, encoding="utf-8"))]

    out = tmp_path / "kols.csv"
    monkeypatch.setattr(sys, "argv", ["import_roster.py", "--source", str(src), "--out", str(out)])
    assert import_roster.main() == 0
    report = capsys.readouterr().out
    assert "bank_account" in report and "stripped" in report   # operator sees what was dropped

    # ...and none of it survives into the roster.
    header = out.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert header == import_roster.OUT_COLUMNS
    text = out.read_text(encoding="utf-8")
    for v in bank_values + phones:
        assert v not in text
    assert "Fake Bank" not in text
    # Dedupe: 27 source rows collapse to 25 unique demo creators.
    rows = list(csv.DictReader(open(out, encoding="utf-8")))
    assert len(rows) == 25
    assert all(r["ig_handle"].startswith("@demo.creator") for r in rows)

def test_committed_roster_has_no_pii_columns():
    path = BASE / "data/roster/kols.csv"
    header = path.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert header == import_roster.OUT_COLUMNS
    assert not (set(h.lower() for h in header) & import_roster.KNOWN_PII_COLUMNS)


# ---- provenance survives into the rendered HTML ----------------------------
def test_provenance_tags_render_in_html(tmp_path):
    import build_deck
    deck = {
        "meta": {"brand": "Kopi Test", "campaign_title": "Render check"},
        "slides": [
            {"type": "cover"},
            {"type": "proposed_kols", "kols": [
                {"name": "Rara Demo", "handle": "@demo.creator01", "tier": "Nano",
                 "reach": {"value": 4000, "provenance": "estimate", "unit": "reach"}}]},
            {"type": "kpi", "targets": [
                {"label": "Views", "metric": {"value": 500000, "provenance": "target", "unit": "views"}}]},
            {"type": "campaign_wins", "wins": [
                {"brand": "Sample", "metric": {"value": 512000, "provenance": "verified", "unit": "views"},
                 "goal": {"value": 300000, "provenance": "verified", "unit": "views"}}]},
        ],
    }
    p = tmp_path / "deck.json"
    p.write_text(json.dumps(deck), encoding="utf-8")
    assert verify_outputs.verify(p) == []
    html = build_deck.render_html(p).read_text(encoding="utf-8")
    assert "~4K reach (est.)" in html          # estimate is visibly labeled
    assert "500K views (target)" in html       # target is visibly labeled
    assert "512K views" in html and "512K views (" not in html   # verified renders clean
    assert "Studio Rantai" in html             # agency identity comes from config/brand.json


def test_agency_brand_config_is_swappable():
    b = _util.brand()
    for key in ("name", "philosophy", "contact", "colors", "assets"):
        assert key in b
    for rel in b["assets"].values():
        assert (BASE / rel).exists(), rel
