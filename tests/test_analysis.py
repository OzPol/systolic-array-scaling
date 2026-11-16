import csv
from itertools import product
from pathlib import Path
import tempfile
import unittest
from analysis.model import predict
from analysis.report import ROOT, load_measurements, load_hardware
from scripts.sim import HEADER, validate_rows

# Fixed regression observations, independent of analysis.model.predict().
# Keys are (matrix order, grid dimension, combined input budget).
EXPECTED = {
    (8,2,4):(176,0), (8,2,8):(176,0), (8,2,16):(176,0),
    (8,4,4):(88,28), (8,4,8):(60,0), (8,4,16):(60,0),
    (8,8,4):(44,21), (8,8,8):(30,7), (8,8,16):(23,0),
    (16,2,4):(1216,0), (16,2,8):(1216,0), (16,2,16):(1216,0),
    (16,4,4):(608,240), (16,4,8):(368,0), (16,4,16):(368,0),
    (16,8,4):(304,180), (16,8,8):(184,60), (16,8,16):(124,0),
}
# Useful-equivalent, fill/drain, and capture clocks for each workload/grid pair.
STRUCTURAL = {(8,2):(128,32,16), (8,4):(32,24,4), (8,8):(8,14,1),
              (16,2):(1024,128,64), (16,4):(256,96,16), (16,8):(64,56,4)}


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
        combinations = set(product((8,16),(2,4,8),(4,8,16)))
        self.assertEqual(set(EXPECTED), combinations)
        self.assertEqual(len(measured), len(combinations))
        self.assertEqual({(r['N'],r['P'],r['B']) for r in measured}, combinations)
        for row in measured:
            n,p,b = row['N'],row['P'],row['B']
            with self.subTest(N=n,P=p,B=b):
                compute,stalls = EXPECTED[(n,p,b)]
                useful,fill,capture = STRUCTURAL[(n,p)]
                baseline = EXPECTED[(n,2,b)][0]
                total = compute+n*n
                self.assertEqual(row['compute_cycles'],compute)
                self.assertEqual(row['total_cycles'],total)
                self.assertEqual(row['stall_cycles'],stalls)
                self.assertEqual(row['advance_cycles'],useful+fill)
                self.assertEqual(row['useful_equivalent_cycles'],useful)
                self.assertEqual(row['fill_drain_cycles'],fill)
                self.assertEqual(row['capture_cycles'],capture)
                self.assertEqual(row['readout_cycles'],n*n)
                self.assertEqual(row['useful_macs'],n**3)
                self.assertEqual(useful+fill+capture+stalls,compute)
                self.assertAlmostEqual(row['speedup_vs_2x2'],baseline/compute)
                self.assertAlmostEqual(row['end_to_end_speedup_vs_2x2'],(baseline+n*n)/total)
                self.assertAlmostEqual(row['scaling_efficiency'],baseline/compute/(p*p/4))
                self.assertAlmostEqual(row['macs_per_cycle'],n**3/compute)
                self.assertAlmostEqual(row['pe_utilization'],n**3/(p*p*compute))
                self.assertAlmostEqual(row['stall_fraction'],stalls/compute)
                self.assertAlmostEqual(row['readout_fraction_of_total'],n*n/total)

    def test_partial_sweep_rejected(self):
        for index,row in enumerate(self.rows):
            with self.subTest(N=row['N'],P=row['P'],B=row['B']):
                self.write(self.rows[:index]+self.rows[index+1:])
                with self.assertRaisesRegex(ValueError, 'missing configurations'):
                    load_measurements(self.path)

    def test_duplicate_summary_rejected(self):
        for row in self.rows:
            with self.subTest(N=row['N'],P=row['P'],B=row['B']):
                self.write(self.rows+[row])
                with self.assertRaisesRegex(ValueError, 'duplicate summary'):
                    load_measurements(self.path)

    def test_counter_tampering_rejected(self):
        for index,row in enumerate(self.rows):
            for field in ('compute_cycles','total_cycles','stall_cycles',
                          'advance_cycles','capture_cycles','useful_macs'):
                with self.subTest(N=row['N'],P=row['P'],B=row['B'],counter=field):
                    damaged=[dict(r) for r in self.rows]
                    damaged[index][field]=str(int(row[field])+1)
                    self.write(damaged)
                    with self.assertRaisesRegex(ValueError,field):
                        load_measurements(self.path)

    def test_failed_summary_rejected(self):
        for index,row in enumerate(self.rows):
            with self.subTest(N=row['N'],P=row['P'],B=row['B']):
                damaged=[dict(r) for r in self.rows]
                damaged[index]['cases_passed']='7'
                self.write(damaged)
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
        for index,row in enumerate(rows):
            for kind in ('missing','duplicate','failed'):
                with self.subTest(N=row['N'],P=row['P'],B=row['B'],case=row['case'],damage=kind):
                    if kind=='missing':invalid=rows[:index]+rows[index+1:]
                    elif kind=='duplicate':invalid=rows+[row]
                    else:invalid=[dict(r,**{'pass':'0'}) if i==index else r for i,r in enumerate(rows)]
                    self.write_raw(invalid)
                    with self.assertRaises(ValueError): validate_rows(self.path,configs)
                    with self.assertRaises(ValueError): load_measurements(self.path)

    def test_missing_hardware_is_not_estimated(self):
        self.assertEqual(load_hardware(Path(self.temp.name)/'missing.csv'), [])
        hardware = load_hardware(ROOT/'results/summary_vivado.csv')
        self.assertTrue(any(int(r['P']) == 2 and int(r['N']) == 16 for r in hardware))


class ModelTests(unittest.TestCase):
    def test_documented_counts_and_budget_limit(self):
        for (n,p,b),(compute,stalls) in EXPECTED.items():
            with self.subTest(N=n,P=p,B=b):
                model=predict(n,p,b)
                self.assertEqual(model.compute_cycles,compute)
                self.assertEqual(model.stall_cycles,stalls)
                self.assertEqual(model.total_cycles,compute+n*n)
                self.assertEqual((model.useful_equivalent_cycles,model.fill_drain_cycles,model.capture_cycles),STRUCTURAL[(n,p)])

    def test_bad_parameters(self):
        for params in ((32,8,16),(8,3,4),(8,2,0)):
            with self.assertRaises(ValueError): predict(*params)


if __name__ == '__main__': unittest.main()
