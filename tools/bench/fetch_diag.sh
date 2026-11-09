#!/usr/bin/env bash
# Neueste Diagnose(n) aus dem privaten Archiv holen und auswerten.
# usage: tools/bench/fetch_diag.sh [ANZAHL=1] [REPO=felixferar/klavier-diagnose]
set -e
N=${1:-1}; REPO=${2:-felixferar/klavier-diagnose}; OUT=/tmp/diagrepo; mkdir -p $OUT
gh api "repos/$REPO/contents/diag" --jq '.[] | select(.name|test("^_test_")|not) | .name' | sort | tail -n "$N" | while read -r f; do
  echo "== $f"
  gh api -H "Accept: application/vnd.github.raw" "repos/$REPO/contents/diag/$f" > "$OUT/$f"
  case "$f" in
    *.ktd.gz) python3 "$(dirname "$0")/diag.py" "$OUT/$f" --out "$OUT/${f%.ktd.gz}" --replay ;;
    *) cat "$OUT/$f" ;;
  esac
done
