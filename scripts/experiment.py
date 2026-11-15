#!/usr/bin/env python3
"""Analyze the committed study or measure a new complete experiment."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.run_utils import new_run
from scripts.collect_vivado import collect
from analysis.evidence import verify_run,verify_reference
from analysis.report import generate


def command(*args):
    subprocess.run([str(x) for x in args],cwd=ROOT,check=True)


def refresh(run,output,with_replay=True,build_pdfs=False,plots=True):
    output=Path(output).resolve()
    reference=run is None
    if reference:
        verified=verify_reference()
        simulation=ROOT/'results/summary_sim.csv'
        hardware=ROOT/'results/vivado'
        traces=ROOT/'results/verification/traces'
    else:
        run=Path(run).resolve();verified=verify_run(run)
        simulation=run/'ghdl_sim_results.csv';hardware=run/'vivado';traces=run/'traces'
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.analysis-',dir=output.parent) as temporary:
        stage=Path(temporary)
        collect(hardware,stage/'hardware')
        generate(simulation,stage/'summary_vivado.csv',stage/'analysis',plots=plots)
        manifest=json.loads((stage/'analysis/manifest.json').read_text())
        manifest['evidence']=verified
        manifest['basis']='committed study' if reference else str(run.relative_to(ROOT) if run.is_relative_to(ROOT) else run)
        inputs=[simulation,ROOT/'docs/configurations.csv',ROOT/'results/summary_vivado.csv']
        manifest['inputs_sha256']={str(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
        manifest['inputs_sha256']['summary_vivado.csv']=hashlib.sha256((stage/'summary_vivado.csv').read_bytes()).hexdigest()
        generators=['analysis/model.py','analysis/report.py','analysis/plots.py','analysis/writing.py',
                    'analysis/evidence.py','analysis/study.py','analysis/replay.py','analysis/trace_figures.py',
                    'scripts/experiment.py','scripts/collect_vivado.py','scripts/build_documents.py',
                    'deliverables/report/main.tex','deliverables/presentation/slides.tex','requirements.txt']
        manifest['generator_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in generators}
        (stage/'analysis/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        (stage/'analysis/evidence_validation.json').write_text(json.dumps(verified,indent=2)+'\n')
        if with_replay:
            if reference and output==ROOT/'results/analysis':
                # Retain the existing reviewed replay and activity figures byte for byte.
                shutil.copytree(ROOT/'results/visualization',stage/'visualization')
            else:
                from analysis.replay import build
                build(traces,stage/'visualization')
        expected=output/'claims.json'
        if output==ROOT/'results/analysis' and expected.exists():
            previous=json.loads(expected.read_text());current=json.loads((stage/'analysis/claims.json').read_text())
            changed=[key for key in previous if previous[key]!=current.get(key)]
            if changed:raise ValueError('Written conclusions require review: '+', '.join(changed))
        if build_pdfs:
            if not with_replay or not plots:raise ValueError('PDFs require matching analysis and replay figures')
            from scripts.build_documents import build
            build(stage/'analysis',stage/'visualization',stage/'documents')
        shutil.copytree(stage/'analysis',output,dirs_exist_ok=True)
        shutil.copy2(stage/'summary_vivado.csv',output/'summary_vivado.csv')
        if with_replay:shutil.copytree(stage/'visualization',output.parent/'visualization',dirs_exist_ok=True)
        if build_pdfs:
            shutil.copy2(stage/'documents/report.pdf',ROOT/'deliverables/report/main.pdf')
            shutil.copy2(stage/'documents/presentation.pdf',ROOT/'deliverables/presentation/slides.pdf')
            shutil.copytree(stage/'documents',ROOT/'build/documents',dirs_exist_ok=True)
    print(f'Validated study; analysis: {output}')
    return verified


def preflight(parser):
    if sys.version_info<(3,12):parser.error('Use the Python 3.12 analysis environment; see docs/setup.md')
    for package in ('numpy','matplotlib','PIL'):
        try:importlib.import_module(package)
        except ImportError:parser.error('Install requirements.txt in the analysis environment before measuring')
    if not shutil.which('vivado'):
        settings=Path.home()/'AMDDesignTools/2025.2.1/Vivado/settings64.sh'
        if settings.is_file():
            data=subprocess.check_output(['bash','-c','source "$1" >/dev/null && env -0','bash',str(settings)])
            os.environ.update(dict(item.decode().split('=',1) for item in data.split(b'\0') if b'=' in item))
    for executable in ('ghdl','vivado'):
        if not shutil.which(executable):parser.error(f'{executable} must be available before measurement starts; see docs/setup.md')
    paths=['rtl','tb','scripts','analysis','visualization','constraints','Makefile','requirements.txt','requirements-ci.txt','.github','docs/configurations.csv']
    if subprocess.check_output(['git','status','--porcelain','--',*paths],cwd=ROOT,text=True).strip():
        parser.error('Commit experiment source changes before measuring a source-identified run')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-run',type=Path,help='analyze a new complete measurement archive')
    parser.add_argument('--measure',action='store_true',help='measure all configured simulations and six sequential FPGA builds')
    parser.add_argument('--output',type=Path,help='otherwise allocate a unique timestamped directory')
    parser.add_argument('--publish',action='store_true',help='refresh report, slides and generated analysis from the committed study')
    parser.add_argument('--no-replay',action='store_true',help='skip replay figure generation in a private analysis')
    args=parser.parse_args()
    if args.measure and args.from_run:parser.error('--measure and --from-run are mutually exclusive')
    if args.publish and (args.measure or args.from_run or args.output or args.no_replay):
        parser.error('--publish refreshes the committed study; new measurements remain in their own output folders')
    run=args.from_run
    if args.measure:
        preflight(parser);run=new_run()
        command(sys.executable,'scripts/gen_vectors.py','--check')
        command(sys.executable,'scripts/test_rtl.py','--sim','ghdl')
        command(sys.executable,'scripts/sim.py','--sim','ghdl','--sweep','--output',run/'ghdl_sim_results.csv','--trace-dir',run/'traces')
        for name in ('ghdl','ghdl_units'):shutil.copytree(ROOT/'build'/name,run/name)
        command(sys.executable,'scripts/vivado/run.py','--output-root',run/'vivado')
    output=ROOT/'results/analysis' if args.publish else args.output or new_run(prefix='analysis')/'analysis'
    if args.measure and not args.output:output=run/'analysis'
    refresh(run,output,not args.no_replay,build_pdfs=args.publish)

if __name__=='__main__':main()
