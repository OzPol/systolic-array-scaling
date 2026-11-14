from pathlib import Path
import tempfile
import unittest
from scripts.collect_vivado import ROOT, parse_reports, collect


class VivadoReportTests(unittest.TestCase):
    def test_parse_existing_measured_reports(self):
        row=parse_reports(ROOT/'results/vivado/p2_n16')
        self.assertEqual(int(row['impl_luts']),7260)
        self.assertEqual(int(row['impl_dsps']),4)
        self.assertEqual(float(row['impl_wns_ns']),3.955)
        self.assertEqual(row['impl_timing_met'],'yes')

    def test_missing_reports_do_not_overwrite_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'raw/vivado_p4_n16').mkdir(parents=True)
            summary=root/'summary_vivado.csv';summary.write_text('existing evidence\n')
            with self.assertRaisesRegex(ValueError,'no complete reports'):
                collect(root/'raw',root/'vivado')
            self.assertEqual(summary.read_text(),'existing evidence\n')


if __name__=='__main__':unittest.main()
