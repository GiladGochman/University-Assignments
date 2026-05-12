
PYTHON = python3

# Paths
SRC_DIR = src
CONFIG_DIR = configs
MAIN_SCRIPT = $(SRC_DIR)/main.py
EXAMPLE_CONFIG = $(CONFIG_DIR)/example.txt
SCENARIO1_CONFIG = $(CONFIG_DIR)/scenario_1.txt
SCENARIO2_CONFIG = $(CONFIG_DIR)/scenario_2.txt

all: demo


run:
	@echo "--- Starting Interactive Mode ---"
	$(PYTHON) $(MAIN_SCRIPT) -i --graph_path $(EXAMPLE_CONFIG)


	@echo "--- Running Basic Demo (Q1-Q3) ---"
	$(PYTHON) $(MAIN_SCRIPT) -n --graph_path $(EXAMPLE_CONFIG)


scenario1:
	@echo "--- Running Scenario 1 (Basic) ---"
	$(PYTHON) $(MAIN_SCRIPT) -n --graph_path $(SCENARIO1_CONFIG) \
		--q4_edges "1,4" \
		--q5_start 1 \
		--q5_end 4


scenario2:
	@echo "--- Running Scenario 2 (Complex) ---"
	$(PYTHON) $(MAIN_SCRIPT) -n --graph_path $(SCENARIO2_CONFIG) \
		--q4_edges "4,5,6" \
		--q5_start 1 \
		--q5_end 6


.PHONY: all run demo scenario1 scenario2 clean