"""Validate complete sweeps, derive metrics, and write reproducible study artifacts."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from .model import predict
from .study import CORE, CLOCK_NS, HARDWARE_CONFIGS

ROOT = Path(__file__).resolve().parents[1]


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
            'end_to_end_speedup_vs_2x2': predict(n,2,b).total_cycles/values['total_cycles'],
            'compute_time_us_100mhz': compute*CLOCK_NS/1000,
            'total_time_us_100mhz': values['total_cycles']*CLOCK_NS/1000,
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
        if row['impl_timing_met'] == 'yes' and any(float(row.get(k,0)) < 0 for k in ('impl_wns_ns','impl_whs_ns','impl_ths_ns')):
            raise ValueError(f'inconsistent timing result: {row}')
    return rows


def table(rows, fields):
    def fmt(value):
        return f'{value:.4f}' if isinstance(value, float) else str(value)
    return '\n'.join(['| ' + ' | '.join(fields) + ' |', '|' + '|'.join('---' for _ in fields) + '|'] +
                     ['| ' + ' | '.join(fmt(r[k]) for k in fields) + ' |' for r in rows])


def generate(simulation, hardware, output, plots=True):
    from .writing import write_results
    measurements = load_measurements(simulation)
    resources = load_hardware(hardware)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    by_cfg = {(r['N'],r['P'],r['B']):r for r in measurements}
    hardware_metrics=[]
    for hw in resources:
        n,p=int(hw['N']),int(hw['P'])
        if (n,p) not in HARDWARE_CONFIGS:
            raise ValueError(f'unexpected hardware configuration {(n,p)}')
        for b in (4,8,16):
            measured=by_cfg[(n,p,b)]
            dsps=int(hw['impl_dsps'])
            timing_ok=(hw['impl_timing_met']=='yes' and float(hw.get('impl_whs_ns',0))>=0)
            hardware_metrics.append({
                'N':n,'P':p,'B':b,'compute_cycles':measured['compute_cycles'],
                'total_cycles':measured['total_cycles'],'macs_per_cycle':measured['macs_per_cycle'],
                'impl_luts':int(hw['impl_luts']),'impl_ffs':int(hw['impl_ffs']),
                'impl_dsps':dsps,'impl_bram_tiles':float(hw['impl_bram_tiles']),
                'impl_wns_ns':float(hw['impl_wns_ns']),'impl_timing_met':hw['impl_timing_met'],
                'macs_per_cycle_per_dsp':measured['macs_per_cycle']/dsps if dsps else None,
                'modeled_compute_gmac_s_100mhz':measured['macs_per_cycle']/CLOCK_NS if timing_ok else None,
                'modeled_total_gmac_s_100mhz':n**3/measured['total_cycles']/CLOCK_NS if timing_ok else None,
                'modeled_compute_gops_100mhz':2*measured['macs_per_cycle']/CLOCK_NS if timing_ok else None,
                'modeled_products_s_100mhz':1e9/CLOCK_NS/measured['total_cycles'] if timing_ok else None,
            })
    for name,rows in [('metrics.csv',measurements),('hardware_metrics.csv',hardware_metrics)]:
        if rows:
            with (output/name).open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
                writer.writeheader();writer.writerows(rows)
    hardware_orders=sorted({int(r['N']) for r in resources})
    expected_hardware={(n,p) for n in hardware_orders for p in (2,4,8)}
    missing=sorted(expected_hardware-{(int(r['N']),int(r['P'])) for r in resources})
    write_results(measurements,resources,hardware_metrics,output,simulation,missing)
    paths=[Path(simulation),Path(hardware),ROOT/'docs/configurations.csv']
    manifest={'generator_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'generator_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
              'inputs_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()},
              'measured_configurations':len(measurements),'measured_hardware_configurations':len(resources),
              'hardware_matrix_orders':hardware_orders,'missing_hardware_configurations':missing,'clock_period_ns':CLOCK_NS}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if plots:
        from .plots import render
        render(measurements,resources,output)
    return measurements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simulation', type=Path, help='explicit CSV input; also provide --hardware')
    parser.add_argument('--hardware', type=Path, help='explicit hardware CSV; also provide --simulation')
    parser.add_argument('--output', type=Path, help='defaults to a new timestamped analysis directory')
    parser.add_argument('--no-plots', action='store_true')
    args = parser.parse_args()
    from scripts.run_utils import new_run
    output=args.output or new_run(prefix='analysis')/'analysis'
    if output.resolve()==ROOT/'results/analysis':
        parser.error('Use scripts/experiment.py --publish to refresh the selected deliverables together')
    if args.simulation is None and args.hardware is None:
        from scripts.experiment import refresh
        refresh(None,output,with_replay=False,plots=not args.no_plots)
        return
    if args.simulation is None or args.hardware is None:
        parser.error('Explicit CSV analysis needs both --simulation and --hardware; omit both to use the selected run')
    generate(args.simulation, args.hardware, output, not args.no_plots)
    print(f'Validated {len(CORE)} configurations; wrote {output}')


if __name__ == '__main__':
    main()
