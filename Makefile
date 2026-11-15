PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
SIM ?= ghdl

.PHONY: setup vectors unit rtl sweep analysis visualization check study publish
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
	$(PYTHON) scripts/experiment.py
visualization:
	$(PYTHON) scripts/experiment.py
check:
	$(PYTHON) scripts/check.py
study:
	$(PYTHON) scripts/experiment.py --measure
publish:
	$(PYTHON) scripts/experiment.py --publish
