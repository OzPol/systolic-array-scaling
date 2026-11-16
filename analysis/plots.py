"""Publication figures from validated measurements; no inferred hardware values."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLORS = {4: '#a34c2b', 8: '#35749c', 16: '#2e7951'}


def render(rows, hardware, output):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'text.color': 'black', 'axes.labelcolor': 'black',
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.hashsalt': 'systolic-study'})
    output = Path(output)

    def save(fig, name):
        for ext in ('png', 'svg'):
            path = output/f'{name}.{ext}'
            fig.savefig(path, dpi=180, bbox_inches='tight',
                        metadata={'Date': None} if ext == 'svg' else None)
            if ext == 'svg':
                path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        plt.close(fig)

    for field, title, ylabel, name in (
        ('compute_cycles', 'Compute latency', 'Clocks per complete matrix product', 'latency'),
        ('pe_utilization', 'Useful PE utilization', 'Useful MACs / available PE clocks (%)', 'utilization'),
    ):
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), layout='constrained')
        for n, ax in zip((8, 16), axes):
            for b in (4, 8, 16):
                selected = sorted((r for r in rows if r['N'] == n and r['B'] == b), key=lambda r:r['P'])
                y = [r[field]*(100 if field == 'pe_utilization' else 1) for r in selected]
                ax.plot([r['P'] for r in selected], y, marker='o', color=COLORS[b], label=f'B={b}')
            ax.set(title=f'{n}×{n} matrix workload', xlabel='PE grid dimension', ylabel=ylabel, xticks=[2,4,8])
            ax.set_xticklabels(['2×2','4×4','8×8'])
            if field == 'pe_utilization': ax.set_ylim(0,100)
            ax.grid(axis='y', alpha=.2)
            ax.legend(frameon=False)
        fig.suptitle(f'{title} · modeled input budget B in combined words/clock')
        save(fig, name)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout='constrained')
    for n, ax in zip((8, 16), axes):
        selected = [r for r in rows if r['N'] == n]
        bottom = [0]*len(selected)
        for field, label, color in (
            ('useful_equivalent_cycles','Useful-equivalent work','#35749c'),
            ('fill_drain_cycles','Fill/drain','#79a58c'),
            ('capture_cycles','Tile capture','#bdb7ab'),
            ('stall_cycles','Budget stalls','#a34c2b'),
        ):
            values = [r[field] for r in selected]
            ax.bar(range(len(selected)), values, bottom=bottom, label=label, color=color)
            bottom = [a+b for a,b in zip(bottom, values)]
        ax.set(title=f'{n}×{n} matrix workload', ylabel='Compute clocks', xlabel='PE grid / input words per clock')
        ax.set_xticks(range(len(selected)), [f"{r['P']}×{r['P']} / {r['B']}" for r in selected], rotation=45)
        ax.grid(axis='y', alpha=.15)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside lower center', ncol=4, frameon=False)
    fig.suptitle('Capacity-normalized cycle accounting; useful MACs overlap fill/drain')
    save(fig, 'cycle_breakdown')

    fig, ax = plt.subplots(figsize=(9,4.4),layout='constrained')
    for n,style in ((8,'--'),(16,'-')):
        for b in (4,8,16):
            selected=sorted((r for r in rows if r['N']==n and r['B']==b),key=lambda r:r['P'])
            ax.plot([r['P'] for r in selected],[r['compute_cycles'] for r in selected],
                    color=COLORS[b],linestyle=style,marker='s' if n==8 else 'o',label=f'N={n}, B={b}')
    ax.set(title='Both complete matrix workloads on the same scale',xlabel='PE grid dimension',
           ylabel='Compute clocks',xticks=[2,4,8],xticklabels=['2×2','4×4','8×8'],
           ylim=(0,max(r['compute_cycles'] for r in rows)*1.05))
    ax.legend(frameon=False,ncol=2);ax.grid(alpha=.2)
    save(fig,'latency_combined')

    fig, axes = plt.subplots(2, 2, figsize=(10, 6.7), layout='constrained', sharex=True, sharey=True)
    for n, axis_row in zip((8, 16), axes):
        for ax, field, scope in zip(axis_row,
                ('speedup_vs_2x2', 'end_to_end_speedup_vs_2x2'),
                ('Compute only', 'Compute + serial readout')):
            for b in (4, 8, 16):
                selected = sorted((r for r in rows if r['N'] == n and r['B'] == b), key=lambda r:r['P'])
                ax.plot([r['P'] for r in selected], [r[field] for r in selected],
                        marker='o', color=COLORS[b], label=f'B={b}')
            ax.plot([2,4,8], [1,4,16], linestyle='--', color='#777777',
                    linewidth=1.1, label='PE-count scaling')
            ax.set(title=f'N={n} · {scope}', ylabel='Speedup versus 2×2',
                   xlabel='PE grid dimension', xticks=[2,4,8],
                   xticklabels=['2×2','4×4','8×8'], ylim=(0,17))
            ax.grid(alpha=.2)
    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside lower center', ncol=4, frameon=False)
    fig.suptitle('Measured scaling at fixed workload and input budget')
    save(fig, 'speedup')

    fig, axes = plt.subplots(1,2,figsize=(10,3.5),layout='constrained',sharey=True)
    for n,ax in zip((8,16),axes):
        selected=sorted((r for r in rows if r['N']==n and r['B']==16),key=lambda r:r['P'])
        for field,label,color,style in (
                ('speedup_vs_2x2','Compute','#2e7951','-'),
                ('end_to_end_speedup_vs_2x2','Compute + readout','#35749c','-')):
            ax.plot([r['P'] for r in selected],[r[field] for r in selected],
                    marker='o',color=color,linestyle=style,label=label)
        ax.plot([2,4,8],[1,4,16],color='#777777',linestyle='--',label='PE-count scaling')
        ax.set(title=f'N={n}, full supply (B=16)',xlabel='PE grid dimension',
               ylabel='Speedup versus 2×2',xticks=[2,4,8],xticklabels=['2×2','4×4','8×8'],ylim=(0,17))
        ax.grid(alpha=.2)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=3,frameon=False)
    save(fig,'speedup_full_supply')

    orders=sorted({int(h['N']) for h in hardware})
    if orders:
        fig,axes=plt.subplots(1,len(orders),figsize=(6.4*len(orders),3.8),layout='constrained',squeeze=False)
        for n,ax in zip(orders,axes.flat):
            selected_hardware=sorted((h for h in hardware if int(h['N'])==n),key=lambda h:int(h['P']))
            for b in (4,8,16):
                points=[]
                for hw in selected_hardware:
                    p,dsps=int(hw['P']),int(hw['impl_dsps'])
                    r=next(r for r in rows if (r['N'],r['P'],r['B'])==(n,p,b))
                    points.append((dsps,r['macs_per_cycle']))
                ax.plot([x for x,y in points],[y for x,y in points],marker='o',color=COLORS[b],label=f'B={b}')
            ax.set(title=f'N={n}: measured FPGA implementations',xlabel='Post-route DSPs',ylabel='Useful MACs / compute clock',xticks=[4,16,64])
            ax.grid(alpha=.2);ax.legend(frameon=False)
        save(fig,'throughput_vs_dsp')

    fig,axes=plt.subplots(2,2,figsize=(9,6),layout='constrained')
    for ax,(field,label) in zip(axes.flat,(('impl_luts','LUTs'),('impl_ffs','Flip-flops'),('impl_dsps','DSPs'),('impl_bram_tiles','BRAM tiles'))):
        maximum=0
        for index,n in enumerate(orders):
            offset=0 if len(orders)==1 else (index-.5)*.38
            color='#35749c' if n==16 else '#9ac4d5'
            selected=sorted((h for h in hardware if int(h['N'])==n),key=lambda h:int(h['P']))
            values=[float(h[field]) for h in selected];positions=[(2,4,8).index(int(h['P']))+offset for h in selected]
            bars=ax.bar(positions,values,width=.6 if len(orders)==1 else .36,color=color,label=f'N={n}')
            ax.bar_label(bars,labels=[f'{v:,.0f}' for v in values],padding=3,fontsize=8)
            maximum=max([maximum,*values])
        ax.set(title=label,ylabel='Post-route count',xticks=[0,1,2],xticklabels=['2×2','4×4','8×8'],ylim=(0,maximum*1.25 or 1))
        ax.grid(axis='y',alpha=.15)
    axes[0,0].legend(frameon=False)
    fig.suptitle(f'{len(hardware)} measured FPGA implementations at the same 10 ns target')
    save(fig,'fpga_resources')
