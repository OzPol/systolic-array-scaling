PYTHON ?= python3
SIM ?= ghdl

.PHONY: setup vectors unit rtl sweep analysis check
setup:
	bash scripts/bootstrap.sh
vectors:
	$(PYTHON) scripts/gen_vectors.py --check
unit:
	$(PYTHON) -m unittest discover -s tests -v
rtl:
	$(PYTHON) scripts/test_rtl.py --sim $(SIM)
sweep:
	$(PYTHON) scripts/sim.py --sim $(SIM) --sweep
analysis:
	$(PYTHON) -m analysis.report --simulation results/raw/$(SIM)_sim_results.csv --output results/raw/analysis
check: vectors unit rtl sweep analysis
