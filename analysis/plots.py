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

    fig, ax = plt.subplots(figsize=(5.3, 3.6), layout='constrained')
    selected_hardware = sorted((hw for hw in hardware if int(hw['N']) == 16), key=lambda hw:int(hw['P']))
    for b in (4, 8, 16):
        points = []
        for hw in selected_hardware:
            n, p, dsps = int(hw['N']), int(hw['P']), int(hw['impl_dsps'])
            r = next((r for r in rows if (r['N'],r['P'],r['B']) == (n,p,b)), None)
            if r:
                points.append((dsps, r['macs_per_cycle']))
        if points:
            ax.plot([x for x,y in points], [y for x,y in points], marker='o', color=COLORS[b], label=f'B={b} words/clock')
    count = len(selected_hardware)
    ax.set(title=f'Throughput versus measured DSP use\nN=16 · {count}/3 measured grid implementations',
           xlabel='DSPs from post-route report', ylabel='Useful MACs / simulated compute clock')
    if selected_hardware:
        ax.set_xticks([int(hw['impl_dsps']) for hw in selected_hardware],
                     [f"{hw['impl_dsps']} DSPs\n{hw['P']}×{hw['P']} grid" for hw in selected_hardware])
        ax.legend(frameon=False, loc='upper left')
    else:
        ax.text(.5,.5,'Awaiting measured DSP counts',ha='center',va='center',transform=ax.transAxes)
    ax.grid(alpha=.2)
    save(fig, 'throughput_vs_dsp')

    fig, axes = plt.subplots(2, 2, figsize=(8, 5.5), layout='constrained')
    for ax, (field, label) in zip(axes.flat, (
        ('impl_luts','LUTs'), ('impl_ffs','Flip-flops'),
        ('impl_dsps','DSPs'), ('impl_bram_tiles','BRAM tiles'),
    )):
        values = [float(hw[field]) for hw in selected_hardware]
        bars = ax.bar(range(len(values)), values, color='#35749c', width=.55)
        ax.bar_label(bars, labels=[f'{v:,.0f}' if v.is_integer() else f'{v:g}' for v in values], padding=3)
        ax.set(title=label, ylabel='Post-route count', xticks=range(len(values)))
        ax.set_xticklabels([f"{hw['P']}×{hw['P']}" for hw in selected_hardware])
        ax.set_ylim(0, max(values, default=0)*1.22 or 1)
        ax.grid(axis='y', alpha=.15)
    fig.suptitle('Measured FPGA resources · N=16 · same 10 ns internal clock target')
    save(fig, 'fpga_resources')
