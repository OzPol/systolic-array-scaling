"""Validate source identity, complete run coverage, and implementation diagnostics."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
from .study import ROOT, HARDWARE_CONFIGS, CORE, PART
from .trace import read_trace

def verify_run(run):
    from scripts.collect_vivado import parse_reports
    from .report import load_measurements
    run = Path(run).resolve()
    directories=list((run/'vivado').glob('vivado_p*_n*'))
    if len(directories)!=len(HARDWARE_CONFIGS):
        raise ValueError('run must contain all six configured FPGA implementations')
    sim_path = run / 'ghdl_sim_results.csv'
    meta = json.loads(sim_path.with_suffix('.json').read_text())
    if meta.get('source_dirty') or meta.get('configurations') != len(CORE) or meta.get('cases_passed') != len(CORE)*8:
        raise ValueError('simulation needs a clean, complete recorded sweep')
    digest = hashlib.sha256(sim_path.read_bytes()).hexdigest()
    if digest != meta['csv_sha256']:
        raise ValueError('simulation CSV checksum mismatch')
    # Compare with the recorded revision, not with later analysis/documentation edits.
    for name, wanted in meta['source_sha256'].items():
        data = subprocess.check_output(['git', 'show', f"{meta['source_commit']}:{name}"], cwd=ROOT)
        if hashlib.sha256(data).hexdigest() != wanted:
            raise ValueError(f'recorded source checksum mismatch: {name}')
    rows = load_measurements(sim_path)
    traces = [read_trace(p) for p in sorted((run/'traces').glob('p*_n*_b*.csv'))]
    if len(traces) != len(CORE) or {(t['N'],t['P'],t['B']) for t in traces} != CORE:
        raise ValueError('run must contain all configured activity traces')
    hardware = []
    for directory in sorted((run/'vivado').glob('vivado_p*_n*')):
        record = json.loads((directory/'run.json').read_text())
        row = parse_reports(directory)
        if record.get('part')!=PART:raise ValueError(f'wrong FPGA part: {directory.name}')
        if not record.get('completed') or record.get('source_dirty'):
            raise ValueError(f'incomplete or modified-source implementation: {directory.name}')
        if record['source_commit'] != meta['source_commit']:
            raise ValueError(f'simulation/hardware revision mismatch: {directory.name}')
        if (record['N'],record['P']) != (row['N'],row['P']):
            raise ValueError(f'configuration identity mismatch: {directory.name}')
        for name,wanted in record['source_sha256'].items():
            data = subprocess.check_output(['git','show',f"{record['source_commit']}:{name}"],cwd=ROOT)
            if hashlib.sha256(data).hexdigest() != wanted:
                raise ValueError(f'hardware source checksum mismatch: {name}')
        log = (directory/'console.txt').read_text()
        if f"VIVADO_DONE P={row['P']} N={row['N']}" not in log or re.search(r'^ERROR:',log,re.M):
            raise ValueError(f'implementation completion/error check failed: {directory.name}')
        for diagnostic in ('drc_impl.rpt','methodology_impl.rpt','check_timing_impl.rpt'):
            if not (directory/diagnostic).is_file():
                raise ValueError(f'missing diagnostic {directory.name}/{diagnostic}')
        if int(row['unconstrained_internal_endpoints']) != 0:
            raise ValueError(f'unconstrained internal timing: {directory.name}')
        hardware.append(row)
    if len(hardware) != len(HARDWARE_CONFIGS) or {(r['N'],r['P']) for r in hardware} != HARDWARE_CONFIGS:
        raise ValueError('run must contain all six configured FPGA implementations')
    return {'source_commit':meta['source_commit'], 'simulation_cases':len(rows)*8,
            'simulation_configurations':len(rows),'validated_traces':len(traces),
            'hardware_configurations':len(hardware),'all_internal_timing_met':all(r['impl_timing_met']=='yes' for r in hardware),
            'source_checksums_verified':True, 'simulation_csv_sha256':digest}


def verify_reference(results=None):
    """Validate the committed 18-configuration simulation and N=16 FPGA study."""
    from .report import load_measurements
    from scripts.collect_vivado import parse_reports
    results=Path(results or ROOT/'results')
    measured=load_measurements(results/'summary_sim.csv')
    raw_path=results/'verification/ghdl_sim_results.csv'
    metadata=json.loads(raw_path.with_suffix('.json').read_text())
    digest=hashlib.sha256(raw_path.read_bytes()).hexdigest()
    if digest!=metadata['csv_sha256']:raise ValueError('simulation CSV checksum mismatch')
    if metadata.get('source_dirty'):raise ValueError('verification source record is modified')
    for name,wanted in metadata['source_sha256'].items():
        data=subprocess.check_output(['git','show',f"{metadata['source_commit']}:{name}"],cwd=ROOT)
        if hashlib.sha256(data).hexdigest()!=wanted:
            raise ValueError(f'recorded source checksum mismatch: {name}')
    independent=load_measurements(raw_path)
    counters=('compute_cycles','total_cycles','stall_cycles','advance_cycles','capture_cycles','useful_macs')
    for original,verified in zip(measured,independent):
        if any(original[k]!=verified[k] for k in ('N','P','B',*counters)):
            raise ValueError('simulation summary and independent verification disagree')
    traces=[read_trace(p) for p in sorted((results/'verification/traces').glob('p*_n*_b*.csv'))]
    if len(traces)!=len(CORE) or {(t['N'],t['P'],t['B']) for t in traces}!=CORE:
        raise ValueError('reference study must contain all 18 configured traces')
    with (results/'summary_vivado.csv').open() as stream:summary=list(csv.DictReader(stream))
    resources=[parse_reports(p) for p in sorted((results/'vivado').glob('p*_n*'))]
    if {(r['N'],r['P']) for r in resources}!={(16,2),(16,4),(16,8)} or len(resources)!=3:
        raise ValueError('reference hardware study requires the three N=16 grid implementations')
    if len(summary)!=3:raise ValueError('reference hardware summary requires three rows')
    by_key={(int(r['N']),int(r['P'])):r for r in summary}
    for report in resources:
        row=by_key[(report['N'],report['P'])]
        for field,value in row.items():
            same=report[field]==value if field.endswith('timing_met') else float(report[field])==float(value)
            if not same:raise ValueError(f'hardware summary/report mismatch: {field}')
        if report['unconstrained_internal_endpoints']!=0:
            raise ValueError('reference implementation has unconstrained internal endpoints')
    return {'basis':'committed study measurements','simulation_configurations':len(measured),
            'simulation_cases':len(measured)*8,'validated_traces':len(traces),
            'simulation_source_commit':metadata['source_commit'],'simulation_source_checksums_verified':True,
            'simulation_csv_sha256':digest,'hardware_configurations':len(resources),'hardware_matrix_orders':[16],
            'all_internal_timing_met':all(r['impl_timing_met']=='yes' for r in resources)}
