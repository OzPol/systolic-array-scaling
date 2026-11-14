#!/usr/bin/env bash
# Usage: scripts/questa/run_one.sh P N B [result_csv]
# Compiles RTL + testbench (VHDL-2008) and runs one (P,N,B) configuration.
set -e
cd "$(dirname "$0")/../.."
P=$1; N=$2; B=$3
CSV=${4:-results/raw/sim_results.csv}
VEC=$(printf "tb/vectors/vec_n%02d.txt" "$N")
WORK=build/work_p${P}_n${N}_b${B}
mkdir -p "$(dirname "$CSV")" build
rm -rf "$WORK"
vlib "$WORK" >/dev/null
vcom -2008 -quiet -work "$WORK" rtl/sys_pkg.vhd rtl/pe.vhd rtl/systolic_array.vhd \
     rtl/input_stager.vhd rtl/systolic_top.vhd tb/tb_systolic.vhd
vsim -c -quiet -work "$WORK" tb_systolic -gP=$P -gN=$N -gB=$B \
     -gVEC_FILE="$VEC" -gRESULT_FILE="$CSV" -do "run -all; quit -f" | tee "build/log_p${P}_n${N}_b${B}.txt" | grep -E "TB PASS|TB FAIL|Error|Fatal|\*\* " || true
