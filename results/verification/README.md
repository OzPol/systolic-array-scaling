# Independent verification

The recorded GHDL sweep passes all 144 matrix cases. The JSON sidecar identifies the source revision, tool version, and file hashes.

- `ghdl_sim_results.csv`: every case and measured counter.
- `ghdl_sim_results.json`: run provenance.
- `ghdl/`: compile output and per-configuration logs.
- `ghdl_units/`: PE, stager, and synthesis-mode regression logs.

Run `make check` to repeat the workflow. GitHub CI also runs the browser checks and retains the complete artifact bundle.
