"""Validate complete sweeps, derive metrics, and write reproducible study artifacts."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from .model import predict

ROOT = Path(__file__).resolve().parents[1]
CORE = {(n, p, b) for n in (8, 16) for p in (2, 4, 8) for b in (4, 8, 16)}


def load_measurements(path):
    with Path(path).open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError('empty simulation input')
    raw = 'case' in rows[0]
    grouped = {}
    for row in rows:
        key = tuple(int(row[k]) for k in ('N', 'P', 'B'))
        if key not in CORE:
            raise ValueError(f'unexpected configuration {key}')
        grouped.setdefault(key, []).append(row)
    if set(grouped) != CORE:
        raise ValueError(f'missing configurations: {sorted(CORE - set(grouped))}')
    result = []
    names = {'compute_cycles': 'compute', 'total_cycles': 'total', 'stall_cycles': 'stall',
             'advance_cycles': 'adv', 'capture_cycles': 'cap', 'useful_macs': 'macs'}
    for (n, p, b), cases in sorted(grouped.items()):
        if raw:
            if len(cases) != 8 or {int(r['case']) for r in cases} != set(range(8)):
                raise ValueError(f'duplicate or missing cases for {(n, p, b)}')
            if any(r['pass'] != '1' for r in cases):
                raise ValueError(f'failing cases for {(n, p, b)}')
        elif len(cases) != 1 or int(cases[0]['cases_passed']) != 8:
            raise ValueError(f'incomplete or duplicate summary for {(n, p, b)}')
        model = predict(n, p, b)
        values = {}
        for name, short in names.items():
            observed = {int(r[short if raw else name]) for r in cases}
            expected = getattr(model, name)
            if observed != {expected}:
                raise ValueError(f'{(n,p,b)} {name}: measured {observed}, predicted {expected}')
            values[name] = observed.pop()
        baseline = predict(n, 2, b).compute_cycles
        compute = values['compute_cycles']
        result.append({
            'config_id': f'n{n:02d}_p{p:02d}_b{b:02d}', 'N': n, 'P': p, 'B': b,
            'cases_passed': 8, **values,
            'readout_cycles': n*n,
            'useful_equivalent_cycles': model.useful_equivalent_cycles,
            'fill_drain_cycles': model.fill_drain_cycles,
            'macs_per_cycle': n**3/compute,
            'pe_utilization': n**3/(p*p*compute),
            'speedup_vs_2x2': baseline/compute,
            'scaling_efficiency': baseline/compute/(p*p/4),
            'stall_fraction': model.stall_cycles/compute,
            'readout_fraction_of_total': n*n/values['total_cycles'],
            'input_words': model.input_words,
        })
    return result


def load_hardware(path):
    if not Path(path).exists():
        return []
    with Path(path).open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    seen = set()
    for row in rows:
        key = (int(row['N']), int(row['P']))
        if key in seen:
            raise ValueError(f'duplicate hardware row {key}')
        seen.add(key)
        for field in ('impl_luts', 'impl_ffs', 'impl_dsps', 'impl_bram_tiles'):
            if float(row[field]) < 0:
                raise ValueError(f'negative resource count: {row}')
        if row['impl_timing_met'] not in ('yes', 'no'):
            raise ValueError(f'missing timing outcome: {row}')
        if row['impl_timing_met'] == 'yes' and float(row['impl_wns_ns']) < 0:
            raise ValueError(f'inconsistent timing result: {row}')
    return rows


def table(rows, fields):
    def fmt(value):
        return f'{value:.4f}' if isinstance(value, float) else str(value)
    return '\n'.join(['| ' + ' | '.join(fields) + ' |', '|' + '|'.join('---' for _ in fields) + '|'] +
                     ['| ' + ' | '.join(fmt(r[k]) for k in fields) + ' |' for r in rows])


def generate(simulation, hardware, output, plots=True):
    measurements = load_measurements(simulation)
    resources = load_hardware(hardware)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output/'metrics.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(measurements[0]))
        writer.writeheader()
        writer.writerows(measurements)
    missing = [p for p in (2, 4, 8) if not any(int(r['P']) == p and int(r['N']) == 16 for r in resources)]
    by_cfg = {(r['N'], r['P'], r['B']): r for r in measurements}
    wide = by_cfg[(16, 8, 16)]
    limited = by_cfg[(16, 8, 4)]
    q = by_cfg[(16, 8, 8)]
    md = f'''# Measured scaling analysis

Simulation input: `{Path(simulation).as_posix()}`. Every configuration is checked for eight passing cases,
exact N^3 useful MACs, data-independent counters, complete readout, and agreement with a separate cycle model.
The cycle model cross-checks the recorded simulation counts.

## Findings

- At N=16, B=16, compute cycles are 1216 / 368 / 124 for P=2/4/8. The 8×8 achieves {wide['speedup_vs_2x2']:.3f}× speedup with 16× as many PEs: {wide['scaling_efficiency']:.1%} scaling efficiency.
- At N=16, P=8, lowering B from 16 to 8 adds {q['stall_cycles']} stalls (124 → 184 cycles); lowering it to 4 adds {limited['stall_cycles']} stalls (124 → 304 cycles). B=4 costs {limited['compute_cycles']/wide['compute_cycles']:.3f}× the fully supplied compute latency.
- At B=4, P=8 is still 2× faster than P=4 for both matrix sizes. The input limit reduces the benefit of scaling; these measurements do not establish a point where a larger array stops helping.
- At full supply, N=16/P=8 has 64 useful-equivalent cycles, 56 fill/drain cycles, and 4 capture cycles. Thus {wide['pe_utilization']:.1%} PE utilization is explained by the finite workload and per-tile schedule even without budget stalls.
- For N=8/P=8/B=16, compute takes 23 clocks but serial readout adds 64. Compute speedup and end-to-end speedup answer different questions; readout is identical across P for a given N.

## Cycle accounting

For each tile, the grid advances N+2P−2 times and uses one capture clock.
For boundary step t, w(t)=2·count{{i: 0≤t−i<N, 0≤i<P}} words are needed.
Stalls are sum(max(0, ceil(w(t)/B)−1)) over all steps and tiles.
Compute = useful-equivalent + fill/drain + capture + stalls; total = compute + N² readout.

“Useful-equivalent” is N³/P², the capacity-normalized MAC work. This is an accounting decomposition,
not a claim that useful MACs happen exclusively in a separate block of clocks. Useful MACs overlap fill/drain.

{table(measurements, ['N','P','B','compute_cycles','stall_cycles','useful_equivalent_cycles','fill_drain_cycles','capture_cycles','pe_utilization','speedup_vs_2x2'])}

## FPGA evidence

{table(resources, ['P','N','impl_luts','impl_ffs','impl_dsps','impl_bram_tiles','impl_wns_ns','impl_timing_met']) if resources else 'No post-route FPGA reports are available.'}

Missing N=16 hardware configurations: {', '.join('P='+str(p) for p in missing) or 'none'}.
The existing P=2 evidence was generated by Thomas before these follow-up changes.
The P=4/P=8 Vivado runs will complete the DSP comparison.
The existing out-of-context report constrains the internal clock but reports 71 inputs and 63 outputs without delay constraints.
The reported slack covers the constrained internal paths; board I/O timing is a separate implementation step.
The registered result store uses 9216 bits for N=16 and dominates FF use; zero BRAM is a measured mapping outcome.
The study compares RTL cycle behavior and FPGA implementation cost.

## Figures

- `latency.png` / `.svg`: compute latency by grid, workload, and input budget.
- `utilization.png` / `.svg`: useful PE utilization with the same comparisons.
- `cycle_breakdown.png` / `.svg`: useful-equivalent work, fill/drain, capture, and budget stalls.
- `throughput_vs_dsp.png` / `.svg`: only actual measured DSP counts; explicitly incomplete until P=4/8 are available.
'''
    (output/'report.md').write_text(md)
    paths = [Path(simulation), Path(hardware)]
    manifest = {'source_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                'source_dirty': bool(subprocess.check_output(['git','status','--porcelain'], cwd=ROOT, text=True).strip()),
                'inputs_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()},
                'measured_configurations': len(measurements), 'missing_vivado_p': missing}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    if plots:
        from .plots import render
        render(measurements, resources, output)
    return measurements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simulation', type=Path, default=Path('results/summary_sim.csv'))
    parser.add_argument('--hardware', type=Path, default=Path('results/summary_vivado.csv'))
    parser.add_argument('--output', type=Path, default=Path('results/analysis'))
    parser.add_argument('--no-plots', action='store_true')
    args = parser.parse_args()
    generate(args.simulation, args.hardware, args.output, not args.no_plots)
    print(f'Validated 18 configurations; wrote {args.output}')


if __name__ == '__main__':
    main()
