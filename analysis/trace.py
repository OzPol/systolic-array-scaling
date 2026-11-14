"""Validate actual per-edge RTL traces before turning them into visual geometry."""
import csv
from collections import Counter
from pathlib import Path
from .model import predict

PHASES={1:'advance',2:'budget stall',3:'tile capture',4:'serial readout'}


def read_trace(path):
    path=Path(path)
    with path.open(newline='') as stream: rows=list(csv.DictReader(stream))
    if not rows: raise ValueError(f'empty trace: {path}')
    p,n,b=(int(rows[0][k]) for k in ('P','N','B'))
    expected=predict(n,p,b)
    frames=[]; phases=Counter(); macs=0; tile_counts={}; captured=set()
    for cycle,row in enumerate(rows,1):
        if tuple(int(row[k]) for k in ('P','N','B')) != (p,n,b) or int(row['case']) != 5:
            raise ValueError('mixed configuration or non-performance case in trace')
        if int(row['cycle']) != cycle: raise ValueError('noncontiguous trace clocks')
        phase=int(row['phase']); mask=int(row['mac_mask'],16)
        tr,tc,t=(int(row[k]) for k in ('tile_row','tile_col','step'))
        if phase not in PHASES or mask < 0 or mask >= 1 << (p*p): raise ValueError('invalid phase or PE mask')
        if phase != 1 and mask: raise ValueError('MAC event during a stall, capture, or readout')
        phases[phase]+=1; macs+=mask.bit_count()
        if phase<=3:
            if not (0<=tr<n//p and 0<=tc<n//p):raise ValueError('tile outside product')
            counts=tile_counts.setdefault((tr,tc),[0]*(p*p))
            for i in range(p*p): counts[i]+=(mask>>(p*p-1-i))&1
            if phase==3:
                if (tr,tc) in captured or counts != [n]*(p*p):
                    raise ValueError('tile captured before each PE completed N MACs')
                captured.add((tr,tc))
        frames.append([phase,tr,tc,t,format(mask,'x')])
    targets={1:expected.advance_cycles,2:expected.stall_cycles,3:expected.capture_cycles,4:expected.readout_cycles}
    if dict(phases) != {k:v for k,v in targets.items() if v} or macs!=n**3 or len(rows)!=expected.total_cycles:
        raise ValueError('trace activity/phase totals disagree with verified configuration')
    if len(captured)!=expected.tiles: raise ValueError('missing completed tiles')
    return {'P':p,'N':n,'B':b,'case':5,'compute':expected.compute_cycles,'total':expected.total_cycles,
            'stalls':phases[2],'macs':macs,'frames':frames}
