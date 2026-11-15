# Development history and verification

## Development sequence

| Commit | Contributor(s) | Change |
|---|---|---|
| [`0e448a3`](https://github.com/OzPol/systolic-array-scaling/commit/0e448a3) | OP | Initial commit |
| [`d7780d2`](https://github.com/OzPol/systolic-array-scaling/commit/d7780d2) | OP | Add project documentation for systolic array scaling |
| [`964f9ea`](https://github.com/OzPol/systolic-array-scaling/commit/964f9ea) | OP, TM | Document the project proposal |
| [`dc476d1`](https://github.com/OzPol/systolic-array-scaling/commit/dc476d1) | OP | Enhance README with project information and status |
| [`2b61d82`](https://github.com/OzPol/systolic-array-scaling/commit/2b61d82) | OP | Update README.md |
| [`b334b48`](https://github.com/OzPol/systolic-array-scaling/commit/b334b48) | OP | Create architecture.md |
| [`027e038`](https://github.com/OzPol/systolic-array-scaling/commit/027e038) | OP | Add experiment plan for matrix multiplication evaluation |
| [`a38d114`](https://github.com/OzPol/systolic-array-scaling/commit/a38d114) | OP | Add development setup documentation |
| [`240a639`](https://github.com/OzPol/systolic-array-scaling/commit/240a639) | OP | Update README.md |
| [`28d30bf`](https://github.com/OzPol/systolic-array-scaling/commit/28d30bf) | OP | Upload project reference documents |
| [`f983b0f`](https://github.com/OzPol/systolic-array-scaling/commit/f983b0f) | OP | Update configurations.csv |
| [`2269d2c`](https://github.com/OzPol/systolic-array-scaling/commit/2269d2c) | TM | Fix doc links, add .gitignore, record tool and board info |
| [`3459a9f`](https://github.com/OzPol/systolic-array-scaling/commit/3459a9f) | TM | Add parameterized systolic array RTL, testbench, and first sim/Vivado results |
| [`d771fc7`](https://github.com/OzPol/systolic-array-scaling/commit/d771fc7) | TM | Add explanatory comments to RTL and testbench VHDL files |
| [`62835f0`](https://github.com/OzPol/systolic-array-scaling/commit/62835f0) | OP | Fix cross-platform vector checksum reproducibility |
| [`ef24e20`](https://github.com/OzPol/systolic-array-scaling/commit/ef24e20) | OP | Add portable simulation runner and independent clock checks |
| [`0cbd84c`](https://github.com/OzPol/systolic-array-scaling/commit/0cbd84c) | OP | Mask useful MAC events during reset and clear |
| [`ab72cae`](https://github.com/OzPol/systolic-array-scaling/commit/ab72cae) | OP | Test boundary staging across budgets and sparse input steps |
| [`056ade7`](https://github.com/OzPol/systolic-array-scaling/commit/056ade7) | OP | Add validated cycle analysis and measured scaling plots |
| [`889e145`](https://github.com/OzPol/systolic-array-scaling/commit/889e145) | OP | Add PR verification pipeline and reproducible environment bootstrap |
| [`22eb6a6`](https://github.com/OzPol/systolic-array-scaling/commit/22eb6a6) | OP | Prepare sequential Vivado runs and preserve measured report evidence |
| [`9f040af`](https://github.com/OzPol/systolic-array-scaling/commit/9f040af) | OP | Verify synthesis-mode datapath matches instrumented simulation |
| [`3733d6f`](https://github.com/OzPol/systolic-array-scaling/commit/3733d6f) | OP | Pin the clean-environment dependency set and analysis provenance |
| [`f17cf0f`](https://github.com/OzPol/systolic-array-scaling/commit/f17cf0f) | OP | Document installation, interfaces, CI, and reproducible experiments |
| [`5e9ad38`](https://github.com/OzPol/systolic-array-scaling/commit/5e9ad38) | OP | Route legacy summarization through validated analysis |
| [`4ca2014`](https://github.com/OzPol/systolic-array-scaling/commit/4ca2014) | OP | Add development review and completion documentation |
| [`785b762`](https://github.com/OzPol/systolic-array-scaling/commit/785b762) | OP | Draft IEEE manuscript and five-minute video storyboard |
| [`a6a3c5f`](https://github.com/OzPol/systolic-array-scaling/commit/a6a3c5f) | OP | Export and validate actual per-clock PE activity traces |
| [`4d12c38`](https://github.com/OzPol/systolic-array-scaling/commit/4d12c38) | OP | Simplify project status and report wording |
| [`4549d20`](https://github.com/OzPol/systolic-array-scaling/commit/4549d20) | OP | Add topology replay and 3D views of real PE activity |
| [`5bdbb56`](https://github.com/OzPol/systolic-array-scaling/commit/5bdbb56) | OP | Build replay artifacts and check browser interactions in CI |
| [`f16f803`](https://github.com/OzPol/systolic-array-scaling/commit/f16f803) | OP | Separate source provenance from generated result files |
| [`1e01c23`](https://github.com/OzPol/systolic-array-scaling/commit/1e01c23) | OP | Keep replay configuration values readable on small screens |
| [`8e95e10`](https://github.com/OzPol/systolic-array-scaling/commit/8e95e10) | OP | Keep the report and project notes focused on the results |
| [`e79ec0d`](https://github.com/OzPol/systolic-array-scaling/commit/e79ec0d) | OP | Record verified simulation results and visual story artifacts |
| [`c1da86a`](https://github.com/OzPol/systolic-array-scaling/commit/c1da86a) | OP | Show every array and matrix workload across all 18 configurations |
| [`0a27c58`](https://github.com/OzPol/systolic-array-scaling/commit/0a27c58) | OP | Keep every configuration label and PE slice readable |
| [`daa588d`](https://github.com/OzPol/systolic-array-scaling/commit/daa588d) | OP | Include all 18 configurations in the report comparisons |
| [`7e490ac`](https://github.com/OzPol/systolic-array-scaling/commit/7e490ac) | OP | Publish complete spatial comparisons for all 18 configurations |
| [`fcf8247`](https://github.com/OzPol/systolic-array-scaling/commit/fcf8247) | TM | Add Vivado synthesis/implementation results for P=4, N=16 |
| [`87b297d`](https://github.com/OzPol/systolic-array-scaling/commit/87b297d) | TM | Add Vivado synthesis/implementation results for P=8, N=16 |
| [`994358d`](https://github.com/OzPol/systolic-array-scaling/commit/994358d) | OP | Complete measured FPGA analysis and update project documentation |
| [`bbffed1`](https://github.com/OzPol/systolic-array-scaling/commit/bbffed1) | OP | Transcribe submitted proposal and omit student identifiers |
| [`6af3ee9`](https://github.com/OzPol/systolic-array-scaling/commit/6af3ee9) | OP | Refresh reviewed FPGA figures, hardware tables and IEEE report |

| Initials | Contributor |
|---|---|
| OP | Ozlem Polat |
| TM | Thomas Martin |

## Verification and reporting

The simulation summary covers eighteen configurations and eight passing cases per configuration. The independent GHDL archive provides full-width numerical verification, vector/source hashes, component logs, and the same counter results. The three N=16 FPGA builds provide synthesis/routed resources and constrained internal timing.

| Area | Implemented checks |
|---|---|
| Configuration coverage | Explicit metric assertions for every grid, matrix size, and input budget |
| Failure detection | Missing, duplicate, failed, and altered measurements tested across the complete sweep |
| Activity | Per-clock validation of MAC work, stalls, and tile boundaries |
| Hardware values | Summary fields checked against all three original FPGA report sets |
| Timing | Setup/hold slack and internal endpoint coverage; explicit OOC interface scope |
| Automation | Unique timestamped folders, six-build defaults, and dependency checks before new measurements |
| Documents | Tables and numeric macros generated from the saved measurements |

The original simulation summaries, FPGA reports, console logs, replay, and video outline remain unchanged. New experiments write separate output folders. The synthesis-mode comparison is a directed RTL simulation regression.
