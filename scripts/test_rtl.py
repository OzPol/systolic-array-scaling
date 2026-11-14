#!/usr/bin/env python3
"""Directed component tests, using the same sources and simulators as the sweep."""
import argparse
import os
from pathlib import Path
import sys
from sim import ROOT, SOURCES, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sim', choices=('ghdl', 'questa'), default='ghdl')
    args = parser.parse_args()
    work = ROOT / 'build' / f'{args.sim}_units'
    work.mkdir(parents=True, exist_ok=True)
    benches = sorted((ROOT / 'tb').glob('tb_*.vhd'))
    benches = [p for p in benches if p.name != 'tb_systolic.vhd']
    sources = SOURCES[:-1] + [p.relative_to(ROOT).as_posix() for p in benches]
    executable = os.environ.get('GHDL', 'ghdl')
    if args.sim == 'ghdl':
        run([executable, '-a', '--std=08', f'--workdir={work}', *sources], work / 'compile.txt')
    else:
        if not (work / '_info').exists():
            run(['vlib', work])
        run(['vcom', '-2008', '-work', work, *sources], work / 'compile.txt')
    for bench in benches:
        if args.sim == 'ghdl':
            cmd = [executable, '-r', '--std=08', f'--workdir={work}', bench.stem, '--assert-level=error']
        else:
            cmd = ['vsim', '-c', '-work', work, bench.stem, '-do',
                   'onerror {quit -code 1}; onbreak {quit -code 1}; run -all; quit -code 0']
        output = run(cmd, work / f'{bench.stem}.txt')
        if f'TB PASS {bench.stem}' not in output:
            raise RuntimeError(f'missing PASS marker for {bench.stem}')
        print(f'PASS: {bench.stem}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
