#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# run.sh — single entry point for every Proposal Factory tool.
# Runs Python through the project venv so deps are always available.
# Usage:  ./run.sh tools/query_roster.py --niche padel --tier Mikro
# ---------------------------------------------------------------------------
set -euo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$BASE/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "ERROR: project venv not found at $PY" >&2
  echo "Create it with:  python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi
exec "$PY" "$@"
