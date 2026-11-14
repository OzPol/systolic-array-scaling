"""Create a lightweight offline replay and scientific 3D figures from real RTL traces."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from .trace import read_trace
from .report import CORE, ROOT


STANDALONE_STYLE='''
:root {--foreground:#141414;--background:#fff;--muted:#e7ebee;--border:#b7c0c7;--viz-series-1:#2b7c8b;--viz-series-2:#d99930}
body{font:15px system-ui,sans-serif;color:var(--foreground);background:var(--background);margin:24px auto;max-width:920px;padding:0 16px}
h3{font-size:20px;font-weight:500}.viz-controls,.viz-row{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:12px 0}.form-label{display:block;flex:1;min-width:150px}.form-select{display:block;padding:8px;width:100%;color:#141414;background:white;border:1px solid #bbc2c8;border-radius:4px;font:inherit}.form-range{display:block;width:100%;accent-color:#2b7c8b}.btn{font:inherit;padding:8px 12px;border:1px solid #aeb8bf;border-radius:4px;background:#f4f6f7;color:#141414}.btn-primary{background:#e3edf0}.tabular-nums{font-variant-numeric:tabular-nums}.text-small{font-size:13px}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid #226580;outline-offset:3px}
'''


def build(trace_dir, output, figures=True):
    trace_dir,output=Path(trace_dir),Path(output)
    files=sorted(trace_dir.glob('p*_n*_b*.csv'))
    traces=[read_trace(path) for path in files]
    if {(t['N'],t['P'],t['B']) for t in traces}!=CORE or len(traces)!=18:
        raise ValueError('replay requires one validated trace for each of the 18 configurations')
    payload={'provenance':{
        'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_dirty':bool(subprocess.check_output(['git','status','--porcelain','--','rtl','tb','scripts','analysis','visualization','constraints','Makefile','requirements.txt','requirements-ci.txt','.github'],cwd=ROOT,text=True).strip()),
        'trace_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'frame_fields':['phase','tile_row','tile_col','boundary_step','mac_mask_hex'],
        'mask_order':'MSB is PE(0,0), row-major',
    },'traces':traces}
    data=json.dumps(payload,separators=(',',':'))
    fragment=(ROOT/'visualization/replay-fragment.html').read_text().replace('__TRACE_DATA__',data)
    if len(fragment.encode())>=1_000_000:raise ValueError('replay exceeds the lightweight payload budget')
    output.mkdir(parents=True,exist_ok=True)
    (output/'traces.json').write_text(data+'\n')
    (output/'replay-fragment.html').write_text(fragment)
    (output/'replay.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Systolic array RTL replay</title><style>'+STANDALONE_STYLE+'</style></head><body>'+fragment+'</body></html>')
    if figures:
        from .trace_figures import render
        render(traces,output)
    print(f'Validated 18 actual traces; replay size {len(fragment.encode()):,} bytes; wrote {output}')
    return payload


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace-dir',type=Path,default=Path('results/raw/traces'))
    parser.add_argument('--output',type=Path,default=Path('results/raw/visualization'))
    parser.add_argument('--no-figures',action='store_true')
    args=parser.parse_args();build(args.trace_dir,args.output,not args.no_figures)


if __name__=='__main__':main()
