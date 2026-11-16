import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from analysis.evidence import verify_run, verify_reference
from analysis.report import generate, load_hardware
from analysis.study import ROOT
from scripts.experiment import refresh
from scripts.run_utils import new_run

def reference_copy(target):
    target=Path(target);target.mkdir()
    for name in ('summary_sim.csv','summary_vivado.csv'):shutil.copy2(ROOT/'results'/name,target/name)
    for name in ('verification','vivado'):shutil.copytree(ROOT/'results'/name,target/name)
    return target


class EvidenceTests(unittest.TestCase):
    def test_selected_evidence_is_complete_and_identified(self):
        result=verify_reference()
        self.assertEqual(result['simulation_cases'],144)
        self.assertEqual(result['hardware_configurations'],3)
        self.assertTrue(result['simulation_source_checksums_verified'])
        self.assertTrue(result['all_internal_timing_met'])

    def test_partial_run_cannot_replace_generated_results(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run=root/'run';run.mkdir();(run/'vivado').mkdir()
            output=root/'analysis';output.mkdir();(output/'report.md').write_text('published evidence')
            with self.assertRaisesRegex(ValueError,'six configured'):
                refresh(run,output,False)
            self.assertEqual((output/'report.md').read_text(),'published evidence')

    def test_modified_csv_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run=reference_copy(Path(temp)/'reference')
            with (run/'verification/ghdl_sim_results.csv').open('a') as stream:stream.write('\n')
            with self.assertRaisesRegex(ValueError,'checksum mismatch'):verify_reference(run)

    def test_source_identity_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run=reference_copy(Path(temp)/'reference')
            path=run/'verification/ghdl_sim_results.json';record=json.loads(path.read_text())
            record['source_sha256']['rtl/pe.vhd']='0'*64;path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError,'source checksum mismatch'):verify_reference(run)

    def test_timestamp_collisions_preserve_both_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            first=new_run(temp);(first/'evidence').write_text('keep')
            second=new_run(temp)
            self.assertNotEqual(first,second)
            self.assertEqual((first/'evidence').read_text(),'keep')

    def test_document_build_failure_preserves_current_views(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);output=root/'analysis';output.mkdir()
            (output/'report.md').write_text('reviewed report')
            visualization=root/'visualization';visualization.mkdir()
            (visualization/'replay.html').write_text('reviewed replay')
            with patch('scripts.experiment.generate',side_effect=lambda *a,**kw:generate(*a,plots=False)), \
                 patch('analysis.replay.build',side_effect=lambda source,target:target.mkdir()), \
                 patch('scripts.build_documents.build',side_effect=RuntimeError('document tool failed')):
                with self.assertRaisesRegex(RuntimeError,'document tool failed'):
                    refresh(None,output,True,build_pdfs=True)
            self.assertEqual((output/'report.md').read_text(),'reviewed report')
            self.assertEqual((visualization/'replay.html').read_text(),'reviewed replay')

    def test_default_vivado_sweep_includes_both_matrix_sizes(self):
        from scripts.vivado import run as runner
        calls=[]
        def capture(command,**kwargs):
            p,n=map(int,command[-3:-1]);out=Path(command[-1]);calls.append((n,p))
            for kind in ('util','timing'):
                for stage in ('synth','impl'):(out/f'{kind}_{stage}.rpt').write_text('test report')
            kwargs['stdout'].write(f'VIVADO_DONE P={p} N={n}\n')
            class Completed: returncode=0
            return Completed()
        def tool_output(command,**kwargs):
            if command[0]=='git':return '' if 'status' in command else 'test-revision\n'
            return 'test Vivado version\n'
        with tempfile.TemporaryDirectory() as temp, \
             patch('sys.argv',['run.py','--output-root',temp]), \
             patch.object(runner.shutil,'which',return_value='/tool/vivado'), \
             patch.object(runner.subprocess,'check_output',side_effect=tool_output), \
             patch.object(runner.subprocess,'run',side_effect=capture):
            runner.main()
        self.assertEqual(calls,[(8,2),(8,4),(8,8),(16,2),(16,4),(16,8)])

    def test_negative_hold_cannot_produce_timed_throughput(self):
        from scripts.collect_vivado import parse_reports
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);rows=[parse_reports(p) for p in sorted((ROOT/'results/vivado').iterdir())]
            row=rows[0];row['impl_whs_ns']='-0.100';row['impl_ths_ns']='-1.000';row['impl_timing_met']='no'
            path=root/'hw.csv'
            with path.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(row));writer.writeheader();writer.writerows(rows)
            generate(ROOT/'results/summary_sim.csv',path,root/'analysis',False)
            with (root/'analysis/hardware_metrics.csv').open() as stream:metrics=list(csv.DictReader(stream))
            failed=[r for r in metrics if (int(r['N']),int(r['P']))==(row['N'],row['P'])]
            self.assertTrue(failed)
            self.assertTrue(all(r['modeled_compute_gmac_s_100mhz']=='' for r in failed))

if __name__=='__main__':unittest.main()
