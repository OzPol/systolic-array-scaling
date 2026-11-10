#!/usr/bin/env bash
# Runs all 18 core configurations (P in 2,4,8 x N in 8,16 x B in 4,8,16).
# Output: results/raw/sim_results.csv (one row per case per configuration)
set -e
cd "$(dirname "$0")/../.."
CSV=results/raw/sim_results.csv
mkdir -p results/raw
echo "P,N,B,case,pass,compute,total,stall,adv,cap,macs" > "$CSV"
for N in 8 16; do for P in 2 4 8; do for B in 4 8 16; do
  echo "== P=$P N=$N B=$B"
  scripts/questa/run_one.sh $P $N $B "$CSV"
done; done; done
echo "rows: $(($(wc -l < "$CSV") - 1)); failures: $(awk -F, 'NR>1 && $5!=1' "$CSV" | wc -l)"
