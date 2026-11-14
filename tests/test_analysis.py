import csv
from pathlib import Path
import tempfile
import unittest
from analysis.model import predict
from analysis.report import ROOT, load_measurements, load_hardware
from scripts.sim import HEADER, validate_rows


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'input.csv'
        with (ROOT/'results/summary_sim.csv').open(newline='') as stream:
            self.rows = list(csv.DictReader(stream))

    def write(self, rows):
        with self.path.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(self.rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_complete_measured_sweep(self):
        self.write(self.rows)
        measured = load_measurements(self.path)
        self.assertEqual(len(measured), 18)
        wide = next(r for r in measured if (r['N'],r['P'],r['B']) == (16,8,16))
        self.assertAlmostEqual(wide['speedup_vs_2x2'], 1216/124)
        self.assertEqual(wide['useful_equivalent_cycles']+wide['fill_drain_cycles']+wide['capture_cycles'],124)

    def test_partial_sweep_rejected(self):
        self.write(self.rows[:-1])
        with self.assertRaisesRegex(ValueError, 'missing configurations'):
            load_measurements(self.path)

    def test_duplicate_summary_rejected(self):
        self.write(self.rows + [self.rows[0]])
        with self.assertRaisesRegex(ValueError, 'duplicate summary'):
            load_measurements(self.path)

    def test_counter_tampering_rejected(self):
        self.rows[0]['compute_cycles'] = '175'
        self.write(self.rows)
        with self.assertRaisesRegex(ValueError, 'compute_cycles'):
            load_measurements(self.path)

    def test_failed_summary_rejected(self):
        self.rows[0]['cases_passed'] = '7'
        self.write(self.rows)
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            load_measurements(self.path)

    def raw_rows(self):
        names = {'compute':'compute_cycles','total':'total_cycles','stall':'stall_cycles',
                 'adv':'advance_cycles','cap':'capture_cycles','macs':'useful_macs'}
        return [dict(P=r['P'],N=r['N'],B=r['B'],case=str(case), **{'pass':'1'},
                     **{k:r[v] for k,v in names.items()}) for r in self.rows for case in range(8)]

    def write_raw(self, rows):
        with self.path.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=HEADER.strip().split(','))
            writer.writeheader(); writer.writerows(rows)

    def test_raw_case_completeness_and_integrity(self):
        rows=self.raw_rows(); self.write_raw(rows)
        configs=[(p,n,b) for n in (8,16) for p in (2,4,8) for b in (4,8,16)]
        self.assertEqual(len(validate_rows(self.path,configs)),144)
        self.assertEqual(len(load_measurements(self.path)),18)
        for invalid in (rows[:-1],rows+[rows[0]], [dict(r, **{'pass':'0'}) if i==0 else r for i,r in enumerate(rows)]):
            self.write_raw(invalid)
            with self.assertRaises(ValueError): validate_rows(self.path,configs)
            with self.assertRaises(ValueError): load_measurements(self.path)

    def test_missing_hardware_is_not_estimated(self):
        self.assertEqual(load_hardware(Path(self.temp.name)/'missing.csv'), [])
        hardware = load_hardware(ROOT/'results/summary_vivado.csv')
        self.assertTrue(any(int(r['P']) == 2 and int(r['N']) == 16 for r in hardware))


class ModelTests(unittest.TestCase):
    def test_documented_counts_and_budget_limit(self):
        self.assertEqual([predict(16,p,16).compute_cycles for p in (2,4,8)],[1216,368,124])
        self.assertEqual([predict(16,8,b).stall_cycles for b in (4,8,16)],[180,60,0])
        self.assertEqual(predict(8,8,16).total_cycles,87)

    def test_bad_parameters(self):
        for params in ((32,8,16),(8,3,4),(8,2,0)):
            with self.assertRaises(ValueError): predict(*params)


if __name__ == '__main__': unittest.main()
