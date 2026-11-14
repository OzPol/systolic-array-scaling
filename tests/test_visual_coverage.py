import json
from pathlib import Path
import unittest
from analysis.trace_figures import activity,configurations

ROOT=Path(__file__).resolve().parents[1]


class VisualCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.traces=json.loads((ROOT/'results/visualization/traces.json').read_text())['traces']

    def test_every_original_configuration_has_the_correct_pe_topology_and_work(self):
        by_key=configurations(self.traces)
        self.assertEqual(len(by_key),18)
        for (n,p,b),trace in by_key.items():
            with self.subTest(matrix=n,grid=p,budget=b):
                volume=activity(trace)
                self.assertEqual(volume.shape,(trace['compute'],p,p))
                self.assertEqual(int(volume.sum()),n**3)
                self.assertTrue((volume.sum(axis=0)==n**3//(p*p)).all())

    def test_partial_visual_comparison_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'all 18'):
            configurations(self.traces[:-1])


if __name__=='__main__':unittest.main()
