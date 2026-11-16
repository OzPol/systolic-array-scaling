#!/usr/bin/env python3
"""Open-source verification in a fresh execution directory."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.run_utils import new_run
from analysis.report import generate
from analysis.replay import build

def main():
    run=new_run(prefix='verification')
    def call(*args):subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True)
    call('scripts/gen_vectors.py','--check')
    call('-m','unittest','discover','-s','tests','-v')
    call('scripts/test_rtl.py','--sim','ghdl')
    call('scripts/sim.py','--sim','ghdl','--sweep','--output',run/'ghdl_sim_results.csv','--trace-dir',run/'traces')
    generate(run/'ghdl_sim_results.csv',ROOT/'results/analysis/summary_vivado.csv',run/'analysis')
    build(run/'traces',run/'visualization')
    (ROOT/'build/latest_check.json').write_text(json.dumps({'run':str(run.relative_to(ROOT))})+'\n')
    print(f'Complete verification outputs: {run}')

if __name__=='__main__':main()
