"""Study axes read from the checked-in experiment configuration table."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGURATION_FILE = ROOT / 'docs/configurations.csv'
with CONFIGURATION_FILE.open(newline='') as stream:
    CONFIGURATIONS = tuple(csv.DictReader(stream))
CORE = {(int(r['n']), int(r['p']), int(r['input_budget_words'])) for r in CONFIGURATIONS}
if len(CORE) != len(CONFIGURATIONS):
    raise ValueError('duplicate study configuration')
MATRIX_SIZES = sorted({n for n, _, _ in CORE})
GRID_SIZES = sorted({p for _, p, _ in CORE})
BUDGETS = sorted({b for _, _, b in CORE})
HARDWARE_CONFIGS = {(n, p) for n, p, _ in CORE}
CLOCK_NS = 10.0
PART = 'xck26-sfvc784-2LV-c'
