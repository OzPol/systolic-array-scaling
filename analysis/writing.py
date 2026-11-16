"""Data-derived Markdown and LaTeX tables shared by the paper and analysis."""
import csv
from pathlib import Path
from .study import CLOCK_NS, CORE, HARDWARE_CONFIGS, ROOT

def markdown_table(rows, fields):
    def fmt(v):
        if v is None: return 'not applicable'
        return f'{v:.4f}' if isinstance(v,float) else str(v)
    return '\n'.join(['| '+' | '.join(fields)+' |','|'+'|'.join('---' for _ in fields)+'|']+
                     ['| '+' | '.join(fmt(r.get(k)) for k in fields)+' |' for r in rows])

def tex_table(path, headers, rows, formats):
    lines=['\\begin{tabular}{'+'r'*len(headers)+'}',r'\toprule',' & '.join(headers)+r'\\',r'\midrule']
    for row in rows:
        values=[('---' if x is None else (format(x,f) if f else str(x))) for x,f in zip(row,formats)]
        lines.append(' & '.join(values)+r'\\')
    lines.extend([r'\bottomrule',r'\end{tabular}'])
    path.write_text('\n'.join(lines)+'\n')

def comparison_table(cfg, hw, hm, out):
    """Transpose full-supply measurements for direct grid-to-grid comparison."""
    latex=[r'\begin{tabular}{llrrr}', r'\toprule',
           r'Workload & Metric ($B=16$) & $2\times2$ & $4\times4$ & $8\times8$\\', r'\midrule']
    markdown=[]
    for n in (8,16):
        lines=[]
        measures=[
            ('Compute clocks', lambda p: cfg[(n,p,16)]['compute_cycles'], ',.0f'),
            ('Total clocks', lambda p: cfg[(n,p,16)]['total_cycles'], ',.0f'),
            ('Compute speedup', lambda p: cfg[(n,p,16)]['speedup_vs_2x2'], '.3f'),
            ('End-to-end speedup', lambda p: cfg[(n,p,16)]['end_to_end_speedup_vs_2x2'], '.3f'),
            ('Useful utilization (%)', lambda p: 100*cfg[(n,p,16)]['pe_utilization'], '.1f'),
            ('Scaling efficiency (%)', lambda p: 100*cfg[(n,p,16)]['scaling_efficiency'], '.1f'),
            ('Compute GMAC/s', lambda p: hm.get((n,p,16),{}).get('modeled_compute_gmac_s_100mhz'), '.3f'),
            ('Total GMAC/s', lambda p: hm.get((n,p,16),{}).get('modeled_total_gmac_s_100mhz'), '.3f'),
            ('LUTs', lambda p: float(hw[(n,p)]['impl_luts']) if (n,p) in hw else None, ',.0f'),
            ('Flip-flops', lambda p: float(hw[(n,p)]['impl_ffs']) if (n,p) in hw else None, ',.0f'),
            ('DSPs', lambda p: float(hw[(n,p)]['impl_dsps']) if (n,p) in hw else None, ',.0f'),
            ('Setup slack (ns)', lambda p: float(hw[(n,p)]['impl_wns_ns']) if (n,p) in hw else None, '+.3f'),
            ('Hold slack (ns)', lambda p: float(hw[(n,p)]['impl_whs_ns']) if (n,p) in hw else None, '+.3f'),
        ]
        if not any(order==n for order,p in hw):measures=measures[:6]
        for i,(label,get_value,fmt) in enumerate(measures):
            values=[get_value(p) for p in (2,4,8)]
            formatted=['---' if v is None else format(v,fmt) for v in values]
            latex_label=label.replace('%',r'\%')
            latex.append((f'$N={n}$' if i==0 else '')+' & '+latex_label+' & '+' & '.join(formatted)+r'\\')
            lines.append('| '+label+' | '+' | '.join(formatted)+' |')
        markdown.append(f'### N={n}, full supply (B=16)\n\n| Metric | 2×2 | 4×4 | 8×8 |\n|---|---:|---:|---:|\n'+'\n'.join(lines))
        if n==8:latex.append(r'\midrule')
    latex.extend([r'\bottomrule',r'\end{tabular}'])
    (out/'comparison_table.tex').write_text('\n'.join(latex)+'\n')
    (out/'comparison_table.md').write_text('# Configuration comparison\n\n'+
        'Speedups use the 2×2 grid at the same workload and budget. Total metrics include serial readout. '+
        'GMAC/s uses the internally timing-qualified 100 MHz target and excludes external transfers. '+
        'Hardware resources and timed rates are included for the implemented matrix workload; simulation metrics cover both matrix sizes. All measured implementations use zero BRAM tiles. '+
        'The complete budget sweep remains in `metrics.csv` and `hardware_metrics.csv`.\n\n'+
        '\n\n'.join(markdown)+'\n')

def write_results(rows,hardware,hwmetrics,out,simulation,missing):
    out=Path(out)
    cfg={(r['N'],r['P'],r['B']):r for r in rows}
    hw={(int(r['N']),int(r['P'])):r for r in hardware}
    hm={(r['N'],r['P'],r['B']):r for r in hwmetrics}
    comparison_table(cfg,hw,hm,out)
    wide=cfg[(16,8,16)]; limited=cfg[(16,8,4)]
    hardware_orders=sorted({n for n,p in hw})
    complete=bool(hw) and all((n,p) in hw for n in hardware_orders for p in (2,4,8))
    timing_count=sum(r['impl_timing_met']=='yes' for r in hardware)
    latency_order=all(cfg[(n,2,b)]['compute_cycles']>cfg[(n,4,b)]['compute_cycles']>cfg[(n,8,b)]['compute_cycles'] for n in (8,16) for b in (4,8,16))
    dsp_order=complete and all(hm[(n,2,b)]['macs_per_cycle_per_dsp']>hm[(n,4,b)]['macs_per_cycle_per_dsp']>hm[(n,8,b)]['macs_per_cycle_per_dsp'] for n in hardware_orders for b in (4,8,16))
    claims={'larger_grid_reduces_compute_latency':latency_order,'smallest_grid_has_highest_throughput_per_dsp':dsp_order,
            'hardware_matrix_orders':hardware_orders,'reported_hardware_grids_complete':complete,'all_internal_timing_met':complete and timing_count==len(hw)}
    import json
    (out/'claims.json').write_text(json.dumps(claims,indent=2)+'\n')
    simfields=['N','P','B','compute_cycles','total_cycles','stall_cycles','macs_per_cycle','pe_utilization','speedup_vs_2x2','end_to_end_speedup_vs_2x2','scaling_efficiency']
    hwfields=['N','P','impl_luts','impl_ffs','impl_dsps','impl_bram_tiles','impl_wns_ns','impl_whs_ns','impl_timing_met']
    ratefields=['N','P','B','modeled_compute_gmac_s_100mhz','modeled_total_gmac_s_100mhz','modeled_compute_gops_100mhz','modeled_products_s_100mhz','macs_per_cycle_per_dsp']
    findings=[]
    for n in (8,16):
        cycles=[cfg[(n,p,16)]['compute_cycles'] for p in (2,4,8)]
        totals=[cfg[(n,p,16)]['total_cycles'] for p in (2,4,8)]
        findings.append(f'- N={n}, B=16: compute latency {" / ".join(map(str,cycles))} clocks; total latency {" / ".join(map(str,totals))} clocks for P=2/4/8.')
    findings.extend([
        f'- N=16/P=8: reducing B=16 to B=4 adds {limited["stall_cycles"]} budget stalls and changes compute latency from {wide["compute_cycles"]} to {limited["compute_cycles"]} clocks.',
        f'- The N=16/P=8/B=16 compute speedup is {wide["speedup_vs_2x2"]:.3f}, with {100*wide["scaling_efficiency"]:.1f}% scaling efficiency and {100*wide["pe_utilization"]:.1f}% useful PE utilization.',
        '- The largest grid has the lowest compute latency in every measured case.' if latency_order else '- Latency ordering varies across measured configurations.',
        '- The smallest grid has the highest useful throughput per measured DSP for the measured hardware workloads.' if dsp_order else '- Consult the per-configuration throughput/DSP values before selecting a grid.',
        f'- {timing_count}/{len(hardware)} implementations meet the constrained internal {CLOCK_NS:g} ns clock target.'])
    md=f'''# Measured scaling analysis

Simulation input: `{Path(simulation).relative_to(ROOT).as_posix() if Path(simulation).is_relative_to(ROOT) else Path(simulation).as_posix()}`. The analysis validates {len(CORE)} configurations and {len(CORE)*8} passing cases against the cycle model. Hardware values are read from the saved implementation reports.

## Findings

{chr(10).join(findings)}

## Latency, utilization, and scaling

The [configuration comparison](comparison_table.md) places grid sizes in columns for both workloads at full input supply. The complete budget sweep follows below.

{markdown_table(rows,simfields)}

Compute latency includes budget stalls, grid fill/drain, and tile capture. Total latency also includes N² serial-readout clocks. Both speedups use the 2×2 grid at the same matrix size and input budget. Scaling efficiency divides compute speedup by P²/4.

## Implementation cost and timing

{markdown_table(hardware,hwfields) if hardware else 'No implementation evidence selected.'}

The hardware comparison covers matrix order(s) {', '.join(map(str,hardware_orders))} and all three PE grids. The runtime input budget does not require separate synthesis builds. Matrix size is a synthesis generic, so each P/N pair has its own implementation.

These are out-of-context internal timing results. The reports do not constrain external input/output delays. They do not establish board interface timing or measured board throughput. The result store holds N² signed 36-bit values, corresponding to {8*8*36} bits at N=8 and {16*16*36} bits at N=16. Resource mapping is measured separately for each implementation.

## Throughput at the constrained clock

{markdown_table(hwmetrics,ratefields) if hwmetrics else 'No timed throughput estimates available.'}

Rates use the common {1e3/CLOCK_NS:g} MHz target only when the corresponding implementation meets internal setup and hold timing. One MAC is one multiply plus one addition: GOP/s is twice GMAC/s. Compute rates exclude readout; total rates include serial readout but exclude external transfers and software overhead. These are conditional model-derived rates, not measured board rates.

## Cycle accounting

Each tile advances N+2P−2 times and uses one capture clock. Compute = N³/P² useful-equivalent work + fill/drain + capture + budget stalls. Total = compute + N². Useful MACs overlap fill/drain; the decomposition is capacity accounting rather than a partition of physical execution phases.

## Figures

| Figure | Interpretation |
|---|---|
| `latency.png` | Matrix-specific compute latency across grids and budgets |
| `latency_combined.png` | Both workloads on a shared clock axis |
| `speedup.png` | Compute and readout-inclusive speedup against the matching 2×2 grid |
| `speedup_full_supply.png` | Full-supply comparison for a compact presentation view |
| `utilization.png` | Useful MAC events divided by available PE clocks |
| `cycle_breakdown.png` | Finite-workload overhead and input-budget stalls |
| `fpga_resources.png` | Measured FPGA resource configurations |
| `throughput_vs_dsp.png` | Implemented workloads paired with measured DSP counts |

The [trace views](../visualization/README.md) explain operand wavefronts, grid holds, and tile boundaries using recorded events from all configurations. The report interprets these alongside the cycle and resource measurements.
'''
    (out/'report.md').write_text(md)
    tex_table(out/'simulation_table.tex',[r'$N$',r'$P$',r'$B$',r'$C_c$',r'$C_t$',r'$S$',r'MAC/clk',r'$U$ (\%)',r'$S_c$',r'$S_t$',r'$\eta$ (\%)'],
              [[r['N'],r['P'],r['B'],r['compute_cycles'],r['total_cycles'],r['stall_cycles'],r['macs_per_cycle'],100*r['pe_utilization'],r['speedup_vs_2x2'],r['end_to_end_speedup_vs_2x2'],100*r['scaling_efficiency']] for r in rows],['','','','','','','.3f','.1f','.3f','.3f','.1f'])
    tex_table(out/'efficiency_table.tex',[r'$N$',r'$P$',r'$B$',r'$S_c$',r'$S_t$',r'$\eta$ (\%)',r'GMAC/s$_c$',r'GMAC/s$_t$'],
              [[r['N'],r['P'],r['B'],r['speedup_vs_2x2'],r['end_to_end_speedup_vs_2x2'],100*r['scaling_efficiency'],hm.get((r['N'],r['P'],r['B']),{}).get('modeled_compute_gmac_s_100mhz'),hm.get((r['N'],r['P'],r['B']),{}).get('modeled_total_gmac_s_100mhz')] for r in rows if (r['N'],r['P'],r['B']) in hm],['','','','.3f','.3f','.1f','.3f','.3f'])
    tex_table(out/'hardware_table.tex',[r'$N$',r'$P$',r'LUTs',r'FFs',r'DSPs',r'BRAM',r'WNS',r'WHS'],
              [[int(r['N']),int(r['P']),int(r['impl_luts']),int(r['impl_ffs']),int(r['impl_dsps']),float(r['impl_bram_tiles']),float(r['impl_wns_ns']),float(r.get('impl_whs_ns',0))] for r in hardware],['','','', '', '', '.0f','+.3f','+.3f'])
    numbers={'SimulationCases':len(CORE)*8,'SimulationConfigurations':len(CORE),'HardwareConfigurations':len(hardware),
             'TimingPassCount':timing_count,'WideUseful':int(wide['useful_equivalent_cycles']), 'WideFillDrain':wide['fill_drain_cycles'], 'WideCapture':wide['capture_cycles'], 'WideCompute':wide['compute_cycles'],'WideTotal':wide['total_cycles'],
             'WideSpeedup':f'{wide["speedup_vs_2x2"]:.3f}','WideEfficiency':f'{wide["scaling_efficiency"]*100:.1f}',
             'WideUtilization':f'{wide["pe_utilization"]*100:.1f}','LimitedCompute':limited['compute_cycles'],
             'LimitedStalls':limited['stall_cycles'],'LimitedPenalty':f'{limited["compute_cycles"]/wide["compute_cycles"]:.3f}',
             'ReadoutSmall':8**2,'ReadoutLarge':16**2,'SmallWideCompute':cfg[(8,8,16)]['compute_cycles'],
             'SmallWideTotal':cfg[(8,8,16)]['total_cycles'],'SmallEndSpeedup':f'{cfg[(8,8,16)]["end_to_end_speedup_vs_2x2"]:.3f}',
             'LargeEndSpeedup':f'{wide["end_to_end_speedup_vs_2x2"]:.3f}'}
    for n in (8,16):
        for p in (2,4,8):
            suffix=('Small' if n==8 else 'Large')+{2:'Two',4:'Four',8:'Eight'}[p]
            measured=cfg[(n,p,16)]
            for key,field in [('Compute','compute_cycles'),('Total','total_cycles')]:numbers[key+suffix]=measured[field]
            if (n,p) in hw:
                for key,field in [('LUT','impl_luts'),('FF','impl_ffs'),('DSP','impl_dsps')]:numbers[key+suffix]=hw[(n,p)][field]
                numbers['WNS'+suffix]=f'{float(hw[(n,p)]["impl_wns_ns"]):.3f}'
                numbers['DSPRate'+suffix]=f'{hm[(n,p,16)]["macs_per_cycle_per_dsp"]:.3f}'
    (out/'numbers.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+str(v)+'}' for k,v in numbers.items())+'\n')
