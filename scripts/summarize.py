#!/usr/bin/env python3
"""Build committed summaries from the (git-ignored) raw outputs. Parses existing files only;
it never launches Questa or Vivado.

Reads : results/raw/sim_results.csv, results/raw/vivado_p<P>_n<N>/*.rpt, build/log_*.txt,
        build/viv_p<P>.log (Vivado console), tb/vectors/MANIFEST.txt
Writes: results/summary_sim.csv, results/summary_vivado.csv, results/summary.md,
        results/logs/*.txt (console output), results/vivado/p<P>_n<N>/*.rpt
"""
import csv
import glob
import pathlib
import re
import shutil
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, RES, LOGS = ROOT / "results" / "raw", ROOT / "results", ROOT / "results" / "logs"
PERF_CASE = 5


def sim_rows():
    rows = list(csv.DictReader(open(RAW / "sim_results.csv")))
    bad = [r for r in rows if r["pass"] != "1"]
    assert not bad, f"{len(bad)} failing simulation rows"
    by_cfg = defaultdict(list)
    for r in rows:
        by_cfg[(int(r["N"]), int(r["P"]), int(r["B"]))].append(r)
    out = {}
    for key, rs in by_cfg.items():
        # cycle counts must be data independent: identical across every case
        assert len({(r["compute"], r["total"], r["stall"]) for r in rs}) == 1, key
        perf = [r for r in rs if int(r["case"]) == PERF_CASE][0]
        out[key] = dict(cases=len(rs), compute=int(perf["compute"]), total=int(perf["total"]),
                        stall=int(perf["stall"]), adv=int(perf["adv"]), cap=int(perf["cap"]),
                        macs=int(perf["macs"]))
    return out


def write_sim(cfgs):
    fields = ["config_id", "N", "P", "B", "cases_passed", "compute_cycles", "total_cycles", "stall_cycles",
              "advance_cycles", "capture_cycles", "useful_macs", "macs_per_cycle", "pe_utilization",
              "speedup_vs_2x2", "scaling_efficiency"]
    table = []
    for (n, p, b) in sorted(cfgs, key=lambda k: (k[0], k[1], k[2])):
        c = cfgs[(n, p, b)]
        base = cfgs[(n, 2, b)]["compute"]
        sp = base / c["compute"]
        table.append({
            "config_id": f"n{n:02d}_p{p:02d}_b{b:02d}", "N": n, "P": p, "B": b,
            "cases_passed": c["cases"], "compute_cycles": c["compute"], "total_cycles": c["total"],
            "stall_cycles": c["stall"], "advance_cycles": c["adv"], "capture_cycles": c["cap"],
            "useful_macs": c["macs"], "macs_per_cycle": f"{c['macs'] / c['compute']:.4f}",
            "pe_utilization": f"{c['macs'] / (p * p * c['compute']):.4f}",
            "speedup_vs_2x2": f"{sp:.3f}", "scaling_efficiency": f"{sp / (p * p / 4):.3f}"})
    with open(RES / "summary_sim.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(table)
    return table


def grab(text, pattern):
    m = re.search(pattern, text, re.M)
    return m.group(1) if m else ""


def vivado_rows():
    rows = []
    for d in sorted(glob.glob(str(RAW / "vivado_p*_n*"))):
        d = pathlib.Path(d)
        m = re.match(r"vivado_p(\d+)_n(\d+)", d.name)
        p, n = int(m.group(1)), int(m.group(2))
        if not (d / "timing_impl.rpt").exists():
            continue  # incomplete run
        row = {"P": p, "N": n}
        for stage in ("synth", "impl"):
            u = (d / f"util_{stage}.rpt").read_text()
            t = (d / f"timing_{stage}.rpt").read_text()
            row[f"{stage}_luts"] = grab(u, r"^\| CLB LUTs\*?\s+\|\s+(\d+)")
            row[f"{stage}_ffs"] = grab(u, r"^\| CLB Registers\s+\|\s+(\d+)")
            row[f"{stage}_dsps"] = grab(u, r"^\| DSPs\s+\|\s+(\d+)")
            row[f"{stage}_bram_tiles"] = grab(u, r"^\| Block RAM Tile\s+\|\s+([\d.]+)")
            hdr = re.search(r"WNS\(ns\).*\n.*-+.*\n\s+(-?[\d.]+)", t)
            row[f"{stage}_wns_ns"] = hdr.group(1) if hdr else ""
            row[f"{stage}_timing_met"] = "yes" if "All user specified timing constraints are met" in t else "no"
        rows.append(row)
        dest = RES / "vivado" / f"p{p}_n{n}"
        dest.mkdir(parents=True, exist_ok=True)
        for rpt in d.glob("*.rpt"):
            shutil.copy(rpt, dest / rpt.name)
        console = ROOT / "build" / f"viv_p{p}.log"
        if console.exists():
            shutil.copy(console, LOGS / f"vivado_p{p}_n{n}_console.txt")
    fields = ["P", "N"] + [f"{s}_{k}" for s in ("synth", "impl")
                           for k in ("luts", "ffs", "dsps", "bram_tiles", "wns_ns", "timing_met")]
    with open(RES / "summary_vivado.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return rows


def md_table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    out += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
    return "\n".join(out)


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    cfgs = sim_rows()
    sim = write_sim(cfgs)
    viv = vivado_rows()

    # Console output kept in a tracked folder (raw/ and build/ are git-ignored)
    with open(LOGS / "questa_sweep_console.txt", "w") as out:
        for f in sorted(glob.glob(str(ROOT / "build" / "log_p*_n*_b*.txt"))):
            out.write(f"\n######## {pathlib.Path(f).name} ########\n")
            out.write(open(f, errors="replace").read())

    qlog = open(ROOT / "build" / "log_p2_n8_b4.txt", errors="replace").read()
    qver = grab(qlog, r"^# //\s+Version (.*?)\s*$")
    vlogs = sorted(glob.glob(str(LOGS / "vivado_p*_n*_console.txt")))
    vtxt = open(vlogs[0], errors="replace").read() if vlogs else ""
    vver = grab(vtxt, r"Vivado (v[\d.]+ \(64-bit\))")
    vbuild = grab(vtxt, r"SW Build (\d+ on [^\n]*?)$")
    manifest = (ROOT / "tb" / "vectors" / "MANIFEST.txt").read_text().strip()

    md = f"""# Results summary

Generated by `scripts/summarize.py` from the raw simulation and Vivado outputs.
Raw outputs are git-ignored; this folder keeps the reviewed summaries and console logs.

## Run settings

| Item | Value |
|---|---|
| Simulator | Siemens Questa Sim-64 {qver}, compiled with `vcom -2008`, run with `vsim -c` |
| Synthesis/implementation | AMD Vivado {vver}, SW Build {vbuild} |
| FPGA target (synthesis only, no board) | `xck26-sfvc784-2LV-c` (Kria KV260 SOM device) |
| Clock constraint | 10 ns (`constraints/clk_10ns.xdc`) |
| Vivado flow | out-of-context `synth_design`, then `opt_design`, `place_design`, `route_design`; `general.maxThreads 1`; default directives |
| Vivado generics | `P` = 2/4/8, `N` = 16, `INSTR` = false (simulation counters removed) |
| Simulation sweep | P in 2,4,8 x N in 8,16 x B in 4,8,16 = 18 configurations, 8 cases each, 10 ns simulated clock |
| Input budget B | combined A/B words per clock, a modeled interface limit (not KV260 DRAM bandwidth) |
| Arithmetic | signed 16-bit operands, signed 36-bit accumulator, compared at full width |
| Performance workload | case index {PERF_CASE} (fixed-seed random); cycle counts were identical for all 8 cases of every configuration |

Test vectors (`scripts/gen_vectors.py`):

```
{manifest}
```

## Simulation results (all 144 runs passed)

Every output word matched the independent Python reference, useful MACs equalled N^3,
and the cycle counters matched closed-form expectations in the testbench.
Compute latency = RUN + CAPTURE cycles (excludes the N*N serial readout); total adds readout.
Speedup and scaling efficiency are relative to the 2x2 grid at the same N and B.

{md_table(sim, ["N", "P", "B", "compute_cycles", "total_cycles", "stall_cycles", "pe_utilization", "macs_per_cycle", "speedup_vs_2x2", "scaling_efficiency"])}

## Vivado results (post-route, N=16)

{md_table(viv, ["P", "N", "impl_luts", "impl_ffs", "impl_dsps", "impl_bram_tiles", "impl_wns_ns", "impl_timing_met"]) if viv else "No complete Vivado run found."}

Status: only the P values listed above have been run through Vivado. Missing rows have **not been run yet**.
About 9.2k of the flip-flops are the 16x16x36-bit result storage, which is the same for every P.

## Files

- `summary_sim.csv`, `summary_vivado.csv`: the tables above
- `vivado/p<P>_n<N>/`: utilization and timing reports (synth and post-route)
- `logs/questa_sweep_console.txt`: full vsim console output for all 18 configurations
- `logs/vivado_p<P>_n<N>_console.txt`: full Vivado console output
"""
    (RES / "summary.md").write_text(md)
    print(f"wrote summary.md, summary_sim.csv ({len(sim)} rows), summary_vivado.csv ({len(viv)} rows)")


if __name__ == "__main__":
    main()
