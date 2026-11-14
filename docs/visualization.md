# Visualizing the simulation

The PE grid has a natural geometry: row, column, and time. These views connect that structure to the project's input-supply and scaling results.

## The visual story

| View | Coordinates / encoding | What it explains |
|---|---|---|
| PE topology replay | Row and column; active cells perform a MAC; numbers count completed MACs in the current tile | Operand skew, the moving activity front, stalls, and tile boundaries |
| Work surface | PE row, PE column, fraction of each PE’s full-product MAC work completed | Progress after the same 32 physical clocks, across every configuration |
| First/last-MAC surfaces | PE row, PE column, clock of each PE's first and last MAC | Where execution begins and ends, and how restricted supply bends/stretches that window |
| Space–time point cloud | PE row, PE column, physical tile clock; MAC rate on orthogonal volume slices | How PE activity changes across space and physical compute time |
| Scaling surface | Grid size, input budget, measured useful MACs/clock | The combined effect of adding compute capacity and supplying operands |
| Full-product animation | All PE grids and both matrix workloads on a shared clock | Completion across every grid, matrix, and budget |

The overview includes all 18 configurations: rows group the 2×2, 4×4, and 8×8 PE grids for each matrix workload, and columns show input budgets of 4, 8, and 16 words per clock. Separate nine-panel sheets cover 8×8 and 16×16 matrices. The animation shows all three grids and both complete matrix products, with one chapter per input budget.

The volume slices color each PE by MACs per physical clock averaged over four-clock bins. The work and wavefront surfaces join the discrete PE samples with mesh faces. The scaling surface joins discrete measured configurations. Their coordinates and values come from the trace or summary tables.

## Open or regenerate

Open `results/visualization/replay.html` directly in a browser. No server or frontend package installation is needed. Choose a configuration, use the clock slider or playback buttons, and select a geometry. Drag a 3D view to rotate it.

To generate new views:

```bash
python scripts/sim.py --sim ghdl --sweep --trace-dir results/raw/traces
python -m analysis.replay --output results/raw/visualization
```

The testbench records `mac_fire` and tile/step coordinates before each edge. It identifies the edge action from the counter updates after that edge. Phase codes are 1=advance, 2=budget stall, 3=tile capture, 4=serial readout. The replay focuses on compute clocks.

Before rendering, `analysis/trace.py` checks contiguous clocks, configuration identity, MAC count, zero MACs on stalled edges, N MACs per PE before each tile capture, completed tile count, and phase totals. The generated `traces.json` includes source identity and trace hashes.

`analysis/replay.py` produces the offline replay. `analysis/trace_figures.py` produces PNG/SVG figures and the GIF. CI rebuilds them and checks the replay controls and mobile layout in Chromium.

## Questa waveform GUI

The project normally runs Questa in batch mode. To inspect the waveforms interactively, first compile/run a configuration with the Python runner, then launch its work library without `-c`:

```bash
python scripts/sim.py --sim questa --p 8 --n 16 --b 4
vsim -work build/questa tb_systolic -gP=8 -gN=16 -gB=4 -gVEC_FILE=tb/vectors/vec_n16.txt -gRESULT_FILE=results/raw/questa_gui.csv -do scripts/questa/view.tcl
```

The wave setup adds clocks, request coordinates, useful MAC events, stalls, and readout signals. Expand the DUT hierarchy to inspect individual PE accumulators and forwarded operands.

## Vivado GUI

Vivado provides waveform, schematic, and device views. After one of the batch implementation runs, open its routed checkpoint in Vivado:

```tcl
open_checkpoint results/raw/vivado_p4_n16/routed.dcp
```

The netlist/schematic view shows inferred logic; the device view shows placement and routing. The offline replay answers a different question: what the logical PE grid was doing on each simulation clock.

Tool references: [Vivado waveform window](https://docs.amd.com/r/en-US/ug900-vivado-logic-simulation/Wave-Window), [Vivado schematic view](https://docs.amd.com/r/en-US/ug893-vivado-ide/Schematic-Window-Display-Settings), [Questa Visualizer](https://www.siemens.com/en-us/products/ic/questa-one/debug-analysis/visualizer-debug/).
