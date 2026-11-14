import csv
from pathlib import Path
import tempfile
import unittest
from analysis.trace import read_trace

FIXTURE=Path(__file__).resolve().parents[1]/'tb/traces/trace_p8_n8_b4.csv'


class TraceTests(unittest.TestCase):
    def test_actual_trace_covers_every_mac_and_phase(self):
        trace=read_trace(FIXTURE)
        self.assertEqual((trace['P'],trace['N'],trace['B']),(8,8,4))
        self.assertEqual(trace['macs'],512)
        self.assertEqual(trace['stalls'],21)
        self.assertEqual(len(trace['frames']),108)

    def mutate(self, change):
        with FIXTURE.open(newline='') as stream: rows=list(csv.DictReader(stream))
        change(rows)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'trace.csv'
            with path.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
            with self.assertRaises(ValueError):read_trace(path)

    def test_partial_trace_rejected(self):
        self.mutate(lambda rows:rows.pop())

    def test_activity_during_stall_rejected(self):
        self.mutate(lambda rows:next(r for r in rows if r['phase']=='2').update(mac_mask='1'))

    def test_missing_pe_work_rejected(self):
        self.mutate(lambda rows:rows[0].update(mac_mask='0'))


if __name__=='__main__':unittest.main()
