#!/usr/bin/env bash
# Usage: bash scripts/questa/run_one.sh P N B [result_csv]
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 scripts/sim.py --sim questa --p "$1" --n "$2" --b "$3" \
    --output "${4:-results/raw/questa_sim_results.csv}"
