#!/usr/bin/env python3
"""Run the existing VHDL testbench with GHDL or Questa; reject missing/failed cases."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['rtl/sys_pkg.vhd', 'rtl/pe.vhd', 'rtl/systolic_array.vhd',
           'rtl/input_stager.vhd', 'rtl/systolic_top.vhd', 'tb/tb_systolic.vhd']
HEADER = 'P,N,B,case,pass,compute,total,stall,adv,cap,macs\n'


def run(command, log=None):
    proc = subprocess.run([str(x) for x in command], cwd=ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log:
        Path(log).write_text(proc.stdout)
    if proc.returncode:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(map(str, command))}\n{proc.stdout[-6000:]}")
    return proc.stdout


def validate_rows(path, configs):
    with Path(path).open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    expected = {(p, n, b, case) for p, n, b in configs for case in range(8)}
    seen = set()
    for row in rows:
        key = tuple(int(row[k]) for k in ('P', 'N', 'B', 'case'))
        if key not in expected or key in seen or row['pass'] != '1':
            raise ValueError(f'unexpected, duplicate, or failing simulation row: {row}')
        seen.add(key)
        p, n, b, _ = key
        v = {k: int(row[k]) for k in ('compute', 'total', 'stall', 'adv', 'cap', 'macs')}
        if (v['macs'] != n**3 or v['total'] != v['compute'] + n*n
                or v['compute'] != v['stall'] + v['adv'] + v['cap']):
            raise ValueError(f'inconsistent counters: {row}')
    if seen != expected:
        raise ValueError(f'missing {len(expected - seen)} of {len(expected)} simulation cases')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sim', choices=('auto', 'ghdl', 'questa'), default='auto')
    parser.add_argument('--p', type=int, choices=(2, 4, 8), default=2)
    parser.add_argument('--n', type=int, choices=(8, 16), default=8)
    parser.add_argument('--b', type=int, choices=(4, 8, 16), default=4)
    parser.add_argument('--sweep', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--trace-dir', type=Path, help='record the actual per-clock PE activity for performance case 5')
    args = parser.parse_args()
    sim = args.sim
    if sim == 'auto':
        sim = 'ghdl' if shutil.which(os.environ.get('GHDL', 'ghdl')) else 'questa'
    executable = os.environ.get('GHDL', 'ghdl') if sim == 'ghdl' else 'vsim'
    if not shutil.which(executable):
        parser.error(f'{executable} is not installed or not on PATH')
    configs = [(p, n, b) for n in (8, 16) for p in (2, 4, 8) for b in (4, 8, 16)] if args.sweep else [(args.p, args.n, args.b)]
    output = (args.output or ROOT / 'results/raw' / f'{sim}_sim_results.csv').resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER)
    if args.trace_dir:
        args.trace_dir = args.trace_dir.resolve()
        args.trace_dir.mkdir(parents=True, exist_ok=True)
    work = ROOT / 'build' / sim
    work.mkdir(parents=True, exist_ok=True)
    if sim == 'ghdl':
        version = run([executable, '--version']).splitlines()[0]
        run([executable, '-a', '--std=08', f'--workdir={work}', *SOURCES], work / 'compile.txt')
        run([executable, '-e', '--std=08', f'--workdir={work}', 'tb_systolic'])
    else:
        version = run(['vsim', '-version']).strip()
        if not (work / '_info').exists():
            run(['vlib', work])
        run(['vcom', '-2008', '-work', work, *SOURCES], work / 'compile.txt')
    logs = []
    for p, n, b in configs:
        generics = [f'-gP={p}', f'-gN={n}', f'-gB={b}',
                    f'-gVEC_FILE=tb/vectors/vec_n{n:02d}.txt', f'-gRESULT_FILE={output.as_posix()}']
        if args.trace_dir:
            generics.append(f'-gTRACE_FILE={(args.trace_dir / f"p{p}_n{n}_b{b}.csv").as_posix()}')
        log = work / f'p{p}_n{n}_b{b}.txt'
        if sim == 'ghdl':
            command = [executable, '-r', '--std=08', f'--workdir={work}', 'tb_systolic', *generics, '--assert-level=error']
        else:
            command = ['vsim', '-c', '-quiet', '-work', work, 'tb_systolic', *generics,
                       '-do', 'onerror {quit -code 1}; onbreak {quit -code 1}; run -all; quit -code 0']
        text = run(command, log)
        marker = f'TB PASS P={p} N={n} B={b} cases=8'
        if marker not in text or 'TB FAIL' in text or re.search(r'\*\* (?:Error|Fatal):', text):
            raise RuntimeError(f'no clean PASS marker in {log}')
        logs.append(log.relative_to(ROOT).as_posix())
        print(marker, flush=True)
    rows = validate_rows(output, configs)
    tracked = run(['git', 'ls-files', 'rtl', 'tb', 'scripts']).splitlines()
    manifest = {
        'source_commit': run(['git', 'rev-parse', 'HEAD']).strip(),
        'source_dirty': bool(run(['git', 'status', '--porcelain']).strip()),
        'simulator': version, 'configurations': len(configs), 'cases_passed': len(rows),
        'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in tracked},
        'csv_sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'logs': logs,
    }
    output.with_suffix('.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'PASS: {len(rows)} cases; {output}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
