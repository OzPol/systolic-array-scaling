#!/usr/bin/env python3
"""Compatibility entrypoint for the validated analysis CLI.

Use --simulation to analyze a fresh, complete per-case CSV. Defaults to the reviewed
18-row summary. Collect new Vivado reports first with scripts/collect_vivado.py.
The original baseline summary/logs remain historical evidence.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.report import main

if __name__ == '__main__':
    main()
