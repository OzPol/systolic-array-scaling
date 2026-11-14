# Focused waveform layout for an interactive Questa session.
add wave sim:/tb_systolic/clk
add wave sim:/tb_systolic/rst
add wave sim:/tb_systolic/start
add wave -radix unsigned sim:/tb_systolic/step_t
add wave -radix unsigned sim:/tb_systolic/tile_row
add wave -radix unsigned sim:/tb_systolic/tile_col
add wave -radix binary sim:/tb_systolic/mac_fire
add wave -radix unsigned sim:/tb_systolic/cnt_stall
add wave -radix unsigned sim:/tb_systolic/cnt_adv
add wave sim:/tb_systolic/out_valid
add wave -radix unsigned sim:/tb_systolic/out_idx
add wave sim:/tb_systolic/done
run 5 us
wave zoom full
