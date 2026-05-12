# AI Assignment 3 - Hurricane Evacuation Bayesian Network
# Student IDs: 315314799, 318477932

## Description
Solution to homework assigment

**Includes Bonus Question 5 Implementation:**
The agent can find the optimal path from a start vertex to a goal vertex that has the highest probability of being free from flooding.

## How to Run

### 1. Using Make (Recommended)
We have provided a Makefile with shortcuts for all scenarios:

* `make run`       : Starts the Interactive Mode (Menu-based).
* `make scenario1` : Runs Scenario 1 (Basic Diamond) with evidence (Flood at Edge 1).
* `make scenario2` : Runs Scenario 2 (Bridge Graph) with path queries.

### 2. Manual Execution
You can also run the Python script directly from the root folder:

* **Interactive Mode:**
    python3 src/main.py -i --graph_path configs/example.txt

* **Scenario 1 (Basic Graph with Evidence):**
    python3 src/main.py -n --graph_path configs/scenario_1.txt \
        --events_path configs/evidence_1.txt \
        --q4_edges "1,4" \
        --q5_start 1 \
        --q5_end 4

* **Scenario 2 (Complex Bridge Graph):**
    python3 src/main.py -n --graph_path configs/scenario_2.txt \
        --q4_edges "4,5,6" \
        --q5_start 1 \
        --q5_end 6

### Arguments
* `-i` / `--interactive` : Run in interactive menu mode.
* `-n` / `--non-interactive`: Run in benchmark mode.
* `--graph_path`  : Path to the graph configuration file.
* `--events_path` : (Optional) Path to a file containing evidence lines (e.g., "F 1").
* `--q4_edges`    : (Optional) Comma-separated edge IDs for Question 4 (e.g., "1,2").
* `--q5_start`    : (Optional) Start vertex ID for Question 5.
* `--q5_end`      : (Optional) Goal vertex ID for Question 5.

## Project Structure
* `src/`     : Source code (main.py, network.py, etc.)
* `configs/` : Configuration files (scenario_1.txt, evidence_1.txt, etc.)
* `Makefile` : Execution shortcuts.
* `Report.pdf`: Detailed explanation of methods and results.