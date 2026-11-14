set_param general.maxThreads 1
# Usage (from repo root):
#   vivado -mode batch -nojournal -nolog -source scripts/vivado/synth.tcl -tclargs <P> [N]
# Out-of-context synth + opt/place/route of systolic_top for the KV260 SOM part, 10 ns clock.
# INSTR=false removes simulation counters. Same settings for every P.
if {[llength $argv] < 1} { error "Usage: synth.tcl P ?N? ?output_directory?" }
set P [lindex $argv 0]
set N [expr {[llength $argv] > 1 ? [lindex $argv 1] : 16}]
set part xck26-sfvc784-2LV-c
if {$P ni {2 4 8} || $N ni {8 16}} { error "Supported P=2/4/8, N=8/16" }
set out [expr {[llength $argv] > 2 ? [lindex $argv 2] : "results/raw/vivado_p${P}_n${N}"}]
file mkdir $out

read_vhdl -vhdl2008 [list rtl/sys_pkg.vhd rtl/pe.vhd rtl/systolic_array.vhd \
                          rtl/input_stager.vhd rtl/systolic_top.vhd]
read_xdc constraints/clk_10ns.xdc

synth_design -top systolic_top -part $part -mode out_of_context \
    -generic P=$P -generic N=$N -generic INSTR=false
report_utilization -file $out/util_synth.rpt
report_timing_summary -file $out/timing_synth.rpt

opt_design
place_design
route_design
report_utilization -file $out/util_impl.rpt
report_timing_summary -file $out/timing_impl.rpt
report_drc -file $out/drc_impl.rpt
report_methodology -file $out/methodology_impl.rpt
check_timing -verbose -file $out/check_timing_impl.rpt
write_checkpoint -force $out/routed.dcp
puts "VIVADO_DONE P=$P N=$N part=$part version=[version -short]"
