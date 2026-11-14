#!/usr/bin/env python3
"""Sequential licensed Vivado runs; retain source identity, console logs and reports."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RTL = ['rtl/sys_pkg.vhd','rtl/pe.vhd','rtl/systolic_array.vhd',
       'rtl/input_stager.vhd','rtl/systolic_top.vhd','constraints/clk_10ns.xdc','scripts/vivado/synth.tcl']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--p', type=int, choices=(2,4,8), nargs='+', default=[2,4,8])
    parser.add_argument('--n', type=int, choices=(8,16), default=16)
    parser.add_argument('--output-root', type=Path, default=ROOT/'results/raw')
    parser.add_argument('--resume', action='store_true', help='skip only completed runs with matching source hashes')
    args = parser.parse_args()
    executable = shutil.which('vivado')
    if not executable:
        parser.error('Vivado is not on PATH; source its settings64.sh or use its configured command shell')
    source = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in RTL}
    commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for p in args.p:
        out = args.output_root.resolve()/f'vivado_p{p}_n{args.n}'
        metadata = out/'run.json'
        reports = [out/f'{kind}_{stage}.rpt' for kind in ('util','timing') for stage in ('synth','impl')]
        if out.exists():
            if args.resume and metadata.exists() and all(f.exists() for f in reports):
                old=json.loads(metadata.read_text())
                if old.get('completed') and old.get('source_sha256') == source:
                    print(f'SKIP completed matching P={p} N={args.n}'); continue
            raise RuntimeError(f'{out} already exists without matching completion evidence; use a new --output-root')
        out.mkdir(parents=True)
        manifest={'P':p,'N':args.n,'part':'xck26-sfvc784-2LV-c','source_commit':commit,
                  'source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
                  'source_sha256':source,'completed':False}
        metadata.write_text(json.dumps(manifest,indent=2)+'\n')
        command=[executable,'-mode','batch','-nojournal','-nolog','-source','scripts/vivado/synth.tcl',
                 '-tclargs',str(p),str(args.n),out.as_posix()]
        print(f'RUN P={p} N={args.n}; console: {out / "console.txt"}',flush=True)
        with (out/'console.txt').open('w') as console:
            proc=subprocess.run(command,cwd=ROOT,stdout=console,stderr=subprocess.STDOUT)
        log=(out/'console.txt').read_text(errors='replace')
        if proc.returncode or f'VIVADO_DONE P={p} N={args.n}' not in log or not all(f.exists() for f in reports):
            raise RuntimeError(f'Vivado did not complete P={p}; see {out/"console.txt"}')
        manifest['completed']=True
        metadata.write_text(json.dumps(manifest,indent=2)+'\n')
        print(f'COMPLETE P={p} N={args.n}',flush=True)


if __name__ == '__main__':
    try: main()
    except (OSError,RuntimeError) as exc:
        print(f'FAIL: {exc}',file=sys.stderr); sys.exit(1)
