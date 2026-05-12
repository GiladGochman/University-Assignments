
# HW 4

## Project Structure

```text
.
├── Makefile                # Automation commands
├── README.md               # Documentation
└── src
    ├── benchmark_data.py   # Built-in scenarios
    ├── config.py           # File parser
    ├── graph.py            # Graph/Vertex/Edge classes
    ├── main.py             # Entry point
    └── mdp.py              # BeliefState and Value Iteration logic

```
## Methodology

### 1. Agent State Representation
The agent's state is defined by the tuple $(L, K, B)$:
* **Location ($L$):** The vertex ID where the agent is currently located.
* **Kit Status ($K$):** A boolean indicating whether the agent is currently carrying the amphibian kit.
* **Belief Vector ($B$):** A mapping of every edge in the graph to its known status:
    * `0`: **Clear** (observed safe).
    * `1`: **Flooded** (observed blocked).
    * `-1`: **Uncertain** (not yet observed).

### 2. Algorithm: Value Iteration
The solver computes the optimal policy by minimizing the expected cost to reach the target using **Value Iteration**.

1.  **State Space Pruning:** Instead of generating all possible states including the unreachable ones, we perform a forward search from the start to build only the reachable belief states.
2.  **Bellman Update:** We iteratively calculate the utility $V(s)$ for every state until convergence. The value is updated based on the maximum expected return (or minimum expected cost) of available actions:
    $$V(s) = \max_{a} \left[ -Cost(a) + \sum_{s'} P(s' | s, a) V(s') \right]$$
    * **Immediate Cost:** The cost to traverse an edge (weighted by the flood factor if carrying the kit) or the cost to equip/unequip.
    * **Expected Future Value:** If a move leads to "Uncertain" edges, the transition splits into multiple outcomes. The algorithm calculates the weighted average of future state values based on the probability of those edges being flooded.

## How to Run

**1. Run Built-in Benchmarks**
Generates results for standard scenarios in `output/`.

```bash
make benchmark

```

**2. Run Custom Scenario**

```bash
make run-custom FILE=tests/my_scenario.txt RUNS=1000

```

**3. Interactive Mode**
Step-through execution for debugging.

```bash
python3 src/main.py tests/my_scenario.txt --interactive

```

## Configuration Format

```text
V 1              # Vertex
E 1 1 2 10 0.5   # Edge: ID, From, To, Weight, Prob
K 1              # Kit Location
EC 5             # Equip Cost
UC 5             # Unequip Cost
FF 3.0           # Flood Factor (cost multiplier)
Start 1
Target 2

```
