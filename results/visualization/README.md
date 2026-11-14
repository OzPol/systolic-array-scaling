# Simulation visuals

Open `replay.html` in a browser to play or scrub the simulation and rotate the 3D views. P is the grid dimension, N the matrix order, and B the combined input words per clock.

| File | Story |
|---|---|
| `work_surface.png` / `.svg` | Work completed at every PE after sixteen clocks |
| `wavefront_surfaces.png` / `.svg` | The first and last MAC clock at each PE |
| `space_time.png` / `.svg` | MAC events distributed across PE row, column, and time |
| `scaling_surface.png` / `.svg` | Throughput across the measured grid/budget combinations |
| `tile_story.gif` | One output tile at full and restricted input supply |
| `traces.json` | The compact per-clock data used by the replay |

The animation compares P=8, N=16 with B=16 and B=4: one tile takes 31 and 76 clocks. Completed tiles remain on screen while their peer finishes.

Regenerate with `python -m analysis.replay` after recording a sweep with `--trace-dir results/raw/traces`.
