# Development Setup

This page records the verified environment and exact commands once the project runs. It is intentionally incomplete until those values are checked on the machines used by the team.

## Intended tools

| Purpose | Tool | Verified version / location |
|---|---|---|
| VHDL compilation and simulation | Siemens QuestaSim | To be recorded after access check |
| FPGA synthesis and implementation | AMD Vivado | To be recorded after access check |
| Software reference and result analysis | Python | To be recorded with pinned dependencies, if used |

## Fixed experiment settings

| Setting | Value or status |
|---|---|
| RTL language | VHDL; language revision to be confirmed with the installed tools |
| Input arithmetic | Signed 16-bit operands; signed 36-bit accumulated result |
| Grid sizes | 2Ã—2, 4Ã—4, 8Ã—8 |
| Matrix orders | 8, 16 |
| Combined input budgets | 4, 8, 16 words per clock |
| FPGA target | KV260 device; **exact Vivado part string to verify** |
| Clock constraint | 10 ns |
| Board programming | Not required |

## Reproduction checklist

1. Verify access to QuestaSim and Vivado and record each tool's reported version.
2. Confirm the exact KV260 target part in the installed Vivado environment.
3. Settle the VHDL revision and record the compile order in `scripts/questa/`.
4. Record a passing compile and 2Ã—2 smoke test before running the 18 configurations.
5. Add a Vivado Tcl script with the target, 10 ns constraint, source list, and report commands; test all three grid sizes with identical settings.
6. Record actual invocation commands, source commit, fixed input seed, and output locations here.

No simulator installation, license, device-part string, or command output has been verified merely by writing this page.
