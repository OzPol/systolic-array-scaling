# TM-05 speaker notes

Verbatim narration from the selected 11-slide recording presentation. The [technical review](TM-review.md) lists suggested clarifications without changing the archived deck.

## Slide 1

Our project asks a simple architecture question: when we add more computation hardware, how much extra performance do we actually get? We evaluated three systolic array sizes under controlled input limits, using complete matrix multiplications. I'll introduce the array, explain the bottleneck, then show what our measurements reveal.

## Slide 2

A systolic array is a grid of small processing elements. Each element multiplies two incoming numbers and adds the result to a running sum. Values from matrix A flow right and values from B flow down. This arrangement performs many multiply-accumulate operations in parallel, which makes it useful for matrix and AI acceleration.

## Slide 3

The math is straightforward. Each processing element repeatedly multiplies its two incoming operands and adds the product to a local running sum. For example, one output can be one times five, plus two times seven, giving nineteen. The array does many such calculations at once.

## Slide 4

The problem is that simply increasing processing elements doesn't guarantee proportional speedup. The array still needs data delivered at the right time, and its computation must eventually be collected. We compare two-by-two, four-by-four, and eight-by-eight arrays to see where extra compute units help, and where other architectural costs intervene.

## Slide 5

Here is the bottleneck in concrete terms. A two-by-two grid has four processing elements, while an eight-by-eight grid has sixty-four. A full input step may need four, eight, or sixteen operand words, respectively. If an eight-by-eight grid receives only eight words per clock, it may have to stall while a complete step is staged.

## Slide 6

This matters for accelerator design because more arithmetic hardware costs FPGA resources, but may not deliver the same increase in useful throughput. There are also pipeline fill and drain cycles, plus a cost to collect the completed matrix. We wanted to measure the entire tradeoff, not just the array's theoretical peak operations.

## Slide 7

We built one output-stationary VHDL systolic array and generated the three grid sizes from that common design. Each grid computes the same full eight-by-eight or sixteen-by-sixteen matrix product, tiling the output when needed. The testbench enforces input budgets and checks the resulting matrix. Vivado provides a separate FPGA implementation-cost comparison.

## Slide 8

Our controlled sweep covers three grid sizes, two matrix sizes, and three input budgets: eighteen configurations. Each includes eight numerical test cases, or 144 tests total. All passed in Questa, and an independent GHDL run reproduced the results. We then measured cycle counts, stalls, utilization, readout, and FPGA resources.

## Slide 9

The input limit measurably affected the large array. On a sixteen-by-sixteen product using the eight-by-eight grid, computation took 124 cycles at sixteen words per clock, 184 cycles at eight, and 304 cycles at four. The arithmetic hardware didn't change. The extra clocks came from operand staging and stalls.

## Slide 10

At full supply, the eight-by-eight array was 9.81 times faster in compute cycles than our two-by-two baseline, despite having sixteen times as many processing elements. But after including serial result delivery, complete-product speedup dropped to 3.87 times. This shows why it matters to measure more than compute alone.

## Slide 11

Our conclusion is that the largest grid was fastest for these tested workloads, but its additional processing elements yielded diminishing performance returns. Limited input supply, short-workload scheduling, and serial readout each impose different costs. The design question isn't simply how many compute units to add, but how to balance them with the rest of the system. Thank you.
