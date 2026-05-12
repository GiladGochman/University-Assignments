PYTHON = python3
RUNS ?= 1000

.PHONY: help
help:
	@echo "MDP Hurricane Evacuation Solver"
	@echo "================================"
	@echo ""
	@echo "Usage:"
	@echo "  make run-custom FILE=x  - Run custom scenario from file x"
	@echo "  make benchmark          - Generate example output for submission"
	@echo ""
	@echo "Options (pass via command line):"
	@echo "  RUNS=N                  - Number of benchmark runs (default: 1000)"
	@echo "  FILE=path               - Path to custom scenario file"
	@echo ""
	@echo "Examples:"
	@echo "  make run-custom FILE=my_scenario.txt"
	@echo "  make benchmark"

.PHONY: run-custom
run-custom:
ifndef FILE
	$(error FILE is not set. Usage: make run-custom FILE=path/to/scenario.txt)
endif
	$(PYTHON) src/main.py $(FILE) -r $(RUNS)

.PHONY: benchmark
benchmark:
	@echo "Generating example outputs for submission..."
	@mkdir -p output
	$(PYTHON) src/main.py -b --scenario 1 -r 100 -p -o output/scenario1_states.txt > output/scenario1_run.txt 2>&1
	$(PYTHON) src/main.py -b --scenario 2 -r 100 -p -o output/scenario2_states.txt > output/scenario2_run.txt 2>&1
	$(PYTHON) src/main.py -b --scenario 3 -r 100 -p -o output/scenario3_states.txt > output/scenario3_run.txt 2>&1
	@echo "Output files generated in ./output/"
	@ls -la output/