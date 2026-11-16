#!/usr/bin/env python3
"""Sequential licensed Vivado runs; retain source identity, console logs and reports."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from analysis.study import GRID_SIZES, MATRIX_SIZES
from scripts.run_utils import new_run
RTL = ['rtl/sys_pkg.vhd','rtl/pe.vhd','rtl/systolic_array.vhd',
       'rtl/input_stager.vhd','rtl/systolic_top.vhd','constraints/clk_10ns.xdc','scripts/vivado/synth.tcl']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--p', type=int, choices=(2,4,8), nargs='+', default=GRID_SIZES)
    parser.add_argument('--n', type=int, choices=(8,16), nargs='+', default=MATRIX_SIZES)
    parser.add_argument('--output-root', type=Path, default=None)
    parser.add_argument('--resume', action='store_true', help='skip only completed runs with matching source hashes')
    args = parser.parse_args()
    executable = shutil.which('vivado')
    if not executable:
        parser.error('Vivado is not on PATH; source its settings64.sh or use its configured command shell')
    source = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in RTL}
    commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if args.output_root is None:
        args.output_root = new_run()/'vivado'
    for n,p in ((n,p) for n in args.n for p in args.p):
        out = args.output_root.resolve()/f'vivado_p{p}_n{n}'
        metadata = out/'run.json'
        reports = [out/f'{kind}_{stage}.rpt' for kind in ('util','timing') for stage in ('synth','impl')]
        if out.exists():
            if args.resume and metadata.exists() and all(f.exists() for f in reports):
                old=json.loads(metadata.read_text())
                if old.get('completed') and old.get('source_sha256') == source and old.get('source_commit') == commit and not old.get('source_dirty'):
                    print(f'SKIP completed matching P={p} N={n}'); continue
            raise RuntimeError(f'{out} already exists without matching completion evidence; use a new --output-root')
        out.mkdir(parents=True)
        manifest={'P':p,'N':n,'part':'xck26-sfvc784-2LV-c','source_commit':commit,
                  'source_dirty':bool(subprocess.check_output(['git','status','--porcelain','--','rtl','tb','scripts','analysis','visualization','constraints','Makefile','requirements.txt','requirements-ci.txt','.github'],cwd=ROOT,text=True).strip()),
                  'source_sha256':source,'completed':False,
                  'started_utc':datetime.now(timezone.utc).isoformat(), 'command':[], 'tool_version':subprocess.check_output([executable,'-version'],text=True).strip()}
        metadata.write_text(json.dumps(manifest,indent=2)+'\n')
        command=[executable,'-mode','batch','-nojournal','-nolog','-source','scripts/vivado/synth.tcl',
                 '-tclargs',str(p),str(n),out.as_posix()]
        manifest['command']=command
        metadata.write_text(json.dumps(manifest,indent=2)+'\n')
        started=time.monotonic()
        print(f'RUN P={p} N={n}; console: {out / "console.txt"}',flush=True)
        with (out/'console.txt').open('w') as console:
            proc=subprocess.run(command,cwd=ROOT,stdout=console,stderr=subprocess.STDOUT)
        log=(out/'console.txt').read_text(errors='replace')
        if proc.returncode or f'VIVADO_DONE P={p} N={n}' not in log or not all(f.exists() for f in reports):
            raise RuntimeError(f'Vivado did not complete P={p}; see {out/"console.txt"}')
        manifest['elapsed_seconds']=round(time.monotonic()-started,3)
        manifest['finished_utc']=datetime.now(timezone.utc).isoformat()
        manifest['completed']=True
        metadata.write_text(json.dumps(manifest,indent=2)+'\n')
        print(f'COMPLETE P={p} N={n}',flush=True)


if __name__ == '__main__':
    try: main()
    except (OSError,RuntimeError) as exc:
        print(f'FAIL: {exc}',file=sys.stderr); sys.exit(1)
