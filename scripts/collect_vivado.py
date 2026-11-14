#!/usr/bin/env python3
"""Collect actual reports; missing/partial runs never acquire invented resource rows."""
import argparse
import csv
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


def required(text, pattern, name):
    match=re.search(pattern,text,re.M)
    if not match: raise ValueError(f'missing {name} in report')
    return match.group(1)


def parse_reports(directory):
    directory=Path(directory)
    match=re.fullmatch(r'(?:vivado_)?p(\d+)_n(\d+)',directory.name)
    if not match: raise ValueError(f'unrecognized report directory {directory.name}')
    p,n=map(int,match.groups())
    row={'P':p,'N':n}
    for stage in ('synth','impl'):
        utilization=(directory/f'util_{stage}.rpt').read_text()
        timing=(directory/f'timing_{stage}.rpt').read_text()
        for key,pattern in {
            'luts':r'^\| CLB LUTs\*?\s+\|\s+(\d+)',
            'ffs':r'^\| CLB Registers\s+\|\s+(\d+)',
            'dsps':r'^\| DSPs\s+\|\s+(\d+)',
            'bram_tiles':r'^\| Block RAM Tile\s+\|\s+([\d.]+)',
        }.items():
            row[f'{stage}_{key}']=required(utilization,pattern,key)
        row[f'{stage}_wns_ns']=required(timing,r'WNS\(ns\).*\n.*-+.*\n\s+(-?[\d.]+)','WNS')
        row[f'{stage}_timing_met']='yes' if 'All user specified timing constraints are met' in timing else 'no'
    return row


def collect(source, destination):
    source,destination=Path(source).resolve(),Path(destination).resolve()
    destination.mkdir(parents=True,exist_ok=True)
    for directory in sorted(source.glob('vivado_p*_n*')):
        metadata=directory/'run.json'
        if metadata.exists() and not json.loads(metadata.read_text()).get('completed'):
            print(f'SKIP incomplete {directory}'); continue
        required_reports=[directory/f'{kind}_{stage}.rpt' for kind in ('util','timing') for stage in ('synth','impl')]
        if not all(p.exists() for p in required_reports):
            print(f'SKIP partial {directory}'); continue
        row=parse_reports(directory)
        target=destination/f"p{row['P']}_n{row['N']}"
        target.mkdir(parents=True,exist_ok=True)
        for path in [*directory.glob('*.rpt'),*directory.glob('*.json'),*directory.glob('*.txt')]:
            shutil.copy2(path,target/path.name)
    # Keep earlier reviewed runs when collecting only the newly completed P values.
    rows=[parse_reports(d) for d in sorted(destination.glob('p*_n*')) if d.is_dir()]
    output=destination.parent/'summary_vivado.csv'
    if not rows: raise ValueError('no complete reports; summary was not overwritten')
    with output.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(f'Collected {len(rows)} measured hardware configurations: {output}')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'results/raw')
    parser.add_argument('--destination',type=Path,default=ROOT/'results/vivado')
    args=parser.parse_args()
    collect(args.source,args.destination)
