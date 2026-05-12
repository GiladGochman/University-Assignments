import sys
import os
import random
import argparse
import statistics

from config import parse_config_string
from mdp import MDPSolver, BeliefState
from graph import Graph
from benchmark_data import BUILTIN_SCENARIOS

EPSILON = 1e-9


def print_belief_states(solver, output_file=None):
    output_lines = []

    header = "\n" + "=" * 80
    header += "\n BELIEF STATE VALUES AND OPTIMAL ACTIONS"
    header += "\n" + "=" * 80
    output_lines.append(header)

    sorted_states = sorted(solver.belief_states.items(), key=lambda x: x[0])

    target_states = []
    regular_states = []
    unreachable_states = []

    for bs_id, bs in sorted_states:
        if bs.v_id == solver.target:
            target_states.append((bs_id, bs))
        elif bs.utility_value <= -9999:
            unreachable_states.append((bs_id, bs))
        else:
            regular_states.append((bs_id, bs))

    output_lines.append("\n--- TARGET STATES (Goal Reached) ---")
    for bs_id, bs in target_states:
        output_lines.append(f"\nState: {bs_id}")
        output_lines.append(f"  Location: {bs.v_id} (TARGET)")
        output_lines.append(f"  Has Kit: {bs.has_kit}")
        output_lines.append(f"  Value: {bs.utility_value:.4f}")
        output_lines.append(f"  Optimal Action: None (terminal state)")

    output_lines.append("\n--- REACHABLE STATES ---")
    for bs_id, bs in regular_states:
        output_lines.append(f"\nState: {bs_id}")
        output_lines.append(f"  Location: {bs.v_id}")
        output_lines.append(f"  Has Kit: {bs.has_kit}")

        relevant_beliefs = {k: v for k, v in bs.E_prob.items() if v != 0}
        output_lines.append(f"  Edge Beliefs: {relevant_beliefs}")

        output_lines.append(f"  Value: {bs.utility_value:.4f}")
        output_lines.append(f"  Optimal Action: {bs.optimal_action}")

    if unreachable_states:
        output_lines.append("\n--- IRREGULAR/UNREACHABLE STATES ---")
        for bs_id, bs in unreachable_states:
            output_lines.append(f"\nState: {bs_id}")
            output_lines.append(f"  Location: {bs.v_id}")
            output_lines.append(f"  Has Kit: {bs.has_kit}")
            output_lines.append(
                f"  Value: {bs.utility_value:.4f} (unreachable or no valid path)"
            )
            output_lines.append(
                f"  Optimal Action: {bs.optimal_action} (IRREGULAR - state unreachable)"
            )

    output_lines.append("\n" + "=" * 80)
    output_lines.append(f"Total States: {len(solver.belief_states)}")
    output_lines.append(f"  Target States: {len(target_states)}")
    output_lines.append(f"  Reachable States: {len(regular_states)}")
    output_lines.append(f"  Irregular States: {len(unreachable_states)}")
    output_lines.append("=" * 80 + "\n")

    output_text = "\n".join(output_lines)

    if output_file:
        with open(output_file, "w") as f:
            f.write(output_text)
        print(f"Belief states written to: {output_file}")
    else:
        print(output_text)

    return output_text


def execute_episode(solver, graph, params, verbose=False):
    true_world = {}
    for e in graph.edges.values():
        if e.prob > EPSILON and e.prob < (1.0 - EPSILON):
            true_world[e.id] = 1 if random.random() < e.prob else 0
        else:
            true_world[e.id] = 1 if e.prob >= (1.0 - EPSILON) else 0

    if verbose:
        print("World Instance:")
        for eid, status in true_world.items():
            if graph.edges[eid].prob > EPSILON and graph.edges[eid].prob < (
                1.0 - EPSILON
            ):
                print(f"  {eid}: {'FLOODED' if status else 'CLEAR'}")

    curr = solver.start
    kit = False

    belief = {
        e.id: (
            -1
            if (e.prob > EPSILON and e.prob < (1.0 - EPSILON))
            else (1 if e.prob >= (1.0 - EPSILON) else 0)
        )
        for e in graph.edges.values()
    }

    for e in graph.vertices[curr].edges:
        if belief[e] == -1:
            belief[e] = true_world[e]

    total_cost = 0
    steps = 0
    path = [curr]

    while curr != solver.target and steps < 200:
        bs_id = BeliefState.make_id(curr, kit, belief)
        if bs_id not in solver.belief_states:
            if verbose:
                print(f"Error: Agent reached unknown state: {bs_id}")
            return None

        act = solver.belief_states[bs_id].optimal_action
        if verbose:
            print(f"At {curr} (Kit={kit}) -> Action: {act}")

        if not act:
            if verbose:
                print("Stuck! No optimal action.")
            return None

        if act == "Equip":
            kit = True
            total_cost += params["EC"]
        elif act == "Unequip":
            kit = False
            total_cost += params["UC"]
        else:
            neighbor_id = act
            edge = None
            for e in graph.vertices[curr].edges.values():
                if e.get_other_vertex(graph.vertices[curr]).id == neighbor_id:
                    edge = e
                    break

            w = edge.w * (params["FF"] if kit else 1)
            total_cost += w
            curr = neighbor_id
            path.append(curr)

            for e in graph.vertices[curr].edges:
                if belief[e] == -1:
                    belief[e] = true_world[e]
        steps += 1

    if curr == solver.target:
        if verbose:
            print(f"Success! Path: {path}, Cost: {total_cost}")
        return total_cost
    else:
        if verbose:
            print("Failed (Timeout).")
        return None


def run_benchmark(solver, graph, params, runs):
    costs = []
    failures = 0

    for _ in range(runs):
        try:
            c = execute_episode(solver, graph, params, verbose=False)
            if c is not None:
                costs.append(c)
            else:
                failures += 1
        except Exception:
            failures += 1

    if runs > 0:
        success_rate = ((runs - failures) / runs) * 100
    else:
        success_rate = 0.0

    if costs:
        avg_cost = statistics.mean(costs)
        std_dev = statistics.stdev(costs) if len(costs) > 1 else 0.0
        min_cost = min(costs)
        max_cost = max(costs)
    else:
        avg_cost = 0.0
        std_dev = 0.0
        min_cost = 0.0
        max_cost = 0.0

    return {
        "runs": runs,
        "successes": runs - failures,
        "failures": failures,
        "success_rate": success_rate,
        "avg_cost": avg_cost,
        "std_dev": std_dev,
        "min_cost": min_cost,
        "max_cost": max_cost,
    }


def print_summary_table(results):
    if not results:
        print("\nNo results to display.")
        return

    headers = [
        "Scenario",
        "States",
        "Iters",
        "Runs",
        "Success%",
        "Avg Cost",
        "Std Dev",
        "Min",
        "Max",
    ]
    col_widths = [20, 8, 6, 6, 9, 10, 10, 8, 8]

    row_fmt = "  ".join([f"{{:<{w}}}" for w in col_widths])
    separator = "-" * (sum(col_widths) + len(col_widths) * 2)

    print("\n" + "=" * 40 + " BENCHMARK SUMMARY " + "=" * 40)
    print(separator)
    print(row_fmt.format(*headers))
    print(separator)

    for res in results:
        benchmark = res.get("benchmark", {})
        scenario = res.get("scenario", "Unknown")[:20]

        print(
            row_fmt.format(
                scenario,
                str(res.get("states", 0)),
                str(res.get("iterations", 0)),
                str(benchmark.get("runs", 0)),
                f"{benchmark.get('success_rate', 0):.1f}%",
                f"{benchmark.get('avg_cost', 0):.2f}",
                f"{benchmark.get('std_dev', 0):.2f}",
                f"{benchmark.get('min_cost', 0):.2f}",
                f"{benchmark.get('max_cost', 0):.2f}",
            )
        )

    print(separator + "\n")

def run_simulation(scenario_name, config, runs, print_states=False, output_file=None):
    print(f"\n--- Starting Scenario: {scenario_name} ---")

    v_cfg, e_cfg, k_cfg, params, start, target = parse_config_string(config)

    print(f"  Start: {start}, Target: {target}, Runs: {runs}")

    graph = Graph(v_cfg, e_cfg, k_cfg)
    solver = MDPSolver(graph, start, target, params)

    if not solver.check_legal_scenario():
        print("  WARNING: check_legal_scenario failed (Path may rely on risky edges).")

    print("  Building State Space...")
    solver.build_reachable_states()
    num_states = len(solver.belief_states)

    print(f"  Solving MDP (States: {num_states})...")
    iters = solver.value_iteration()
    print(f"  Converged in {iters} iterations.")

    if print_states:
        print_belief_states(solver, output_file)

    print("\n--- Sample Episode Trace (Agent Actions) ---")
    execute_episode(solver, graph, params, verbose=True)
    print("--------------------------------------------\n")

    print(f"  Running Benchmark ({runs} runs)...")
    benchmark_results = run_benchmark(solver, graph, params, runs)

    print(
        f"  Done. Success Rate: {benchmark_results['success_rate']:.1f}%, Avg Cost: {benchmark_results['avg_cost']:.2f}"
    )

    return {
        "scenario": scenario_name,
        "states": num_states,
        "iterations": iters,
        "benchmark": benchmark_results,
        "solver": solver,
        "graph": graph,
        "params": params,
    }

def get_parsed_args():
    parser = argparse.ArgumentParser(description="MDP Flood Navigation Simulation")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-b",
        "--builtin",
        action="store_true",
        help="Run ALL built-in benchmark scenarios sequentially.",
    )

    group.add_argument(
        "path",
        nargs="?",
        help="Path to a text file containing the scenario configuration.",
    )

    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        default=1000,
        help="Number of benchmark runs per scenario (default: 1000).",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode (single episodes with verbose output).",
    )

    parser.add_argument(
        "-p",
        "--print-states",
        action="store_true",
        help="Print all belief states with their values and optimal actions.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file for belief states (used with --print-states).",
    )

    parser.add_argument(
        "--scenario",
        type=int,
        choices=list(BUILTIN_SCENARIOS.keys()),
        help=f"Run only a specific built-in scenario (1-{len(BUILTIN_SCENARIOS)}).",
    )

    return parser.parse_args()


def run_builtin_case(args):
    all_results = []
    print("\n" + "=" * 80)
    print("RUNNING ALL BUILT-IN SCENARIOS")
    print("=" * 80)

    if args.scenario:
        scenarios_to_run = {args.scenario: BUILTIN_SCENARIOS[args.scenario]}
    else:
        scenarios_to_run = BUILTIN_SCENARIOS

    for scenario_id, scenario in scenarios_to_run.items():
        print(f"\n[Scenario {scenario_id}] {scenario['description']}")

        result = run_simulation(
            scenario["name"],
            scenario["config"],
            args.runs,
            print_states=args.print_states,
            output_file=args.output,
        )
        all_results.append(result)

    print_summary_table(all_results)


def run_file_interactive_case(args):
    if not os.path.exists(args.path):
        print(f"Error: The file '{args.path}' was not found.")
        sys.exit(1)

    try:
        with open(args.path, "r") as f:
            config_content = f.read()

        v_cfg, e_cfg, k_cfg, params, start, target = parse_config_string(config_content)

        graph = Graph(v_cfg, e_cfg, k_cfg)
        solver = MDPSolver(graph, start, target, params)

        if not solver.check_legal_scenario():
            print("WARNING: check_legal_scenario failed.")

        print("Building State Space...")
        solver.build_reachable_states()

        print(f"Solving MDP (States: {len(solver.belief_states)})...")
        iters = solver.value_iteration()
        print(f"Converged in {iters} iterations.")

        if args.print_states:
            print_belief_states(solver, args.output)

        while True:
            print("\n--- New Simulation ---")
            execute_episode(solver, graph, params, verbose=True)
            if input("\nRun another? (y/n): ").lower() != "y":
                break

    except Exception as e:
        print(f"Error reading file or running simulation: {e}")
        sys.exit(1)


def run_file_benchmark_case(args):
    if not os.path.exists(args.path):
        print(f"Error: The file '{args.path}' was not found.")
        sys.exit(1)

    try:
        with open(args.path, "r") as f:
            config_content = f.read()

        scenario_name = os.path.basename(args.path)
        all_results = []

        result = run_simulation(
            scenario_name,
            config_content,
            args.runs,
            print_states=args.print_states,
            output_file=args.output,
        )
        all_results.append(result)
        print_summary_table(all_results)

    except Exception as e:
        print(f"Error reading file or running simulation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    args = get_parsed_args()

    if args.builtin:
        run_builtin_case(args)
    elif args.path and args.interactive:
        run_file_interactive_case(args)
    elif args.path:
        run_file_benchmark_case(args)
