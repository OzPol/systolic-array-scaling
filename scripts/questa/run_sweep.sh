#!/usr/bin/env bash
# Run and validate all 144 cases. A simulator failure stops the sweep.
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 scripts/sim.py --sim questa --sweep
