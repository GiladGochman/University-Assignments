import argparse
import sys
from config import parse_config_string
from bayesian_network import BayesianNetwork
import answers  


def apply_evidence_line(bayesian_network, line):
    line = line.strip()
    if not line:
        return False, "Empty line"

    parts = line.split()

    is_negation = False
    if parts[0].lower() == "not":
        is_negation = True
        parts = parts[1:]

    if not parts:
        return False, f"Warning: Invalid format '{line}'"

    key = parts[0].upper()

    try:
        if key.startswith("W"):
            var_name = "Weather"
            if len(parts) > 1:
                var_value = parts[1].lower()
            else:
                return False, f"Warning: Invalid format '{line}'"

            if var_name in bayesian_network.evidence:
                return False, f"Warning: Evidence for Weather already exists."
            else:
                bayesian_network.add_evidence(var_name, var_value)
                return True, ""

        if key.startswith("F"):
            if len(parts) > 1:
                eid = parts[1].lower()
                variable_name = f"Flooded_{eid}"
                value = not is_negation
            else:
                return False, f"Warning: Invalid format '{line}'"

            if variable_name in bayesian_network.evidence:
                return False, f"Warning: Evidence for {variable_name} already exists."
            else:
                bayesian_network.add_evidence(variable_name, value)
                return True, ""

        if key.startswith("E"):
            if len(parts) > 1:
                vid = parts[1].lower()
                variable_name = f"Evacuees_{vid}"
                value = not is_negation
            else:
                return False, f"Warning: Invalid format '{line}'"

            if variable_name in bayesian_network.evidence:
                return False, f"Warning: Evidence for {variable_name} already exists."
            else:
                bayesian_network.add_evidence(variable_name, value)
                return True, ""

    except ValueError:
        print(f"Warning: ID parsing error in line '{line}'")

    return False, "Unknown format"


def run_interactive_mode(args):
    print("Running in interactive mode...")

    if not args.graph_path:
        print("Error: --graph_path is required for interactive mode.")
        sys.exit(1)

    try:
        with open(args.graph_path, "r") as f:
            config_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.graph_path}' not found.")
        sys.exit(1)

    graph_cfg = parse_config_string(config_content)
    bayesian_network = BayesianNetwork(graph_cfg)

    while True:
        print("\n" + "=" * 30)
        print("Menu:")
        print("i. Show info")
        print("r. Reset evidence")
        print("a. Add evidence")
        print("1. Q1: Evacuees probabilities")
        print("2. Q2: Flooded probabilities")
        print("3. Q3: Weather probabilities")
        print("4. Q4: Specific edges flooding probabilities")
        print("5. Q5: Pathfinding under current evidence")
        print("q. Quit")
        print("=" * 30)

        choice = input("Select: ").strip()

        if choice == "i":
            answers.show_info(bayesian_network)

        elif choice == "r":
            bayesian_network.reset_evidence()
            print("Evidence reset.")

        elif choice == "a":
            print("\nEnter evidence using short codes:")
            print("  F <id>    -> Flooding at edge <id> (e.g., 'F 2')")
            print("  not F <id>-> No flooding at edge <id>")
            print("  E <id>    -> Evacuees at vertex <id> (e.g., 'E 3')")
            print("  not E <id>-> No evacuees at vertex <id>")
            print("  W <state> -> Weather state (mild, stormy, extreme)")
            print("  (Type 'b' to go back)")

            while True:
                line = input("Evidence > ").strip()
                if not line:
                    continue
                if line.lower() == "b":
                    break

                status, msg = apply_evidence_line(bayesian_network, line)
                if status:
                    print("  Evidence processed.")
                else:
                    print(f"  {msg}")

        elif choice == "1":
            answers.answer_q1(bayesian_network)
        elif choice == "2":
            answers.answer_q2(bayesian_network)
        elif choice == "3":
            answers.answer_q3(bayesian_network)

        elif choice == "4":
            line = input("Edges > ").strip()
            edge_ids = [int(eid.strip()) for eid in line.split(",") if eid.strip().isdigit()]
            if not edge_ids:
                print("  Invalid edge IDs.")
                continue
            answers.answer_q4(bayesian_network, edge_ids)

        elif choice == "5":
            start = input("Start Vertex ID > ").strip()
            end = input("End Vertex ID > ").strip()
            if not (start.isdigit() and end.isdigit()):
                print("  Invalid vertex IDs.")
                continue
            answers.answer_q5(bayesian_network, int(start), int(end))

        elif choice == "q":
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid choice.")


def run_non_interactive_mode(args):
    print("Running in non-interactive mode...")

    if not args.graph_path:
        print("Error: --graph_path is required.")
        sys.exit(1)

    try:
        with open(args.graph_path, "r") as f:
            config_content = f.read()
    except FileNotFoundError:
        print(f"Error: Graph file '{args.graph_path}' not found.")
        sys.exit(1)

    graph_cfg = parse_config_string(config_content)
    bayesian_network = BayesianNetwork(graph_cfg)

    if args.events_path:
        try:
            with open(args.events_path, "r") as f:
                lines = f.readlines()

            print(f"Loading evidence from {args.events_path}...")
            for line in lines:
                apply_evidence_line(bayesian_network, line)

        except FileNotFoundError:
            print(f"Error: Events file '{args.events_path}' not found.")
            sys.exit(1)


    original_stdout = sys.stdout
    output_file = None

    if args.output_path:
        try:
            output_file = open(args.output_path, "w")
            sys.stdout = output_file
        except IOError as e:
            print(f"Error opening output file: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        print("\n--- Probabilistic Reasoning Report ---")

        answers.answer_q1(bayesian_network)
        answers.answer_q2(bayesian_network)
        answers.answer_q3(bayesian_network)

        if args.q4_edges:
            edge_ids = [int(eid.strip()) for eid in args.q4_edges.split(",") if eid.strip()]
            if edge_ids:
                answers.answer_q4(bayesian_network, edge_ids)
            else:
                print("\n4. (Skipped) No valid edges provided in --q4_edges")
        else:
            print("\n4. (Skipped) Provide --q4_edges to see path probability.")

        if args.q5_start is not None and args.q5_end is not None:
            answers.answer_q5(bayesian_network, args.q5_start, args.q5_end)
        else:
            print("\n5. (Skipped) Provide --q5_start and --q5_end to find best path.")
    
    finally:
        if output_file:
            sys.stdout = original_stdout
            output_file.close()
            print(f"Results saved to {args.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hurricane Evacuation Simulation Agent Runner"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run interactive mode",
    )
    group.add_argument(
        "-n",
        "--non-interactive",
        action="store_true",
        help="Run non interactive mode",
    )
    parser.add_argument(
        "--graph_path",
        help="Path to a text file containing the scenario configuration",
    )
    parser.add_argument(
        "--events_path",
        help="Path to a text file containing list of evidence events to apply one by one",
    )

    parser.add_argument(
        "--q4_edges",
        help="Comma-separated list of edge IDs for Q4 (e.g., '1,2,3')",
        default=None,
    )
    parser.add_argument(
        "--q5_start", help="Start Vertex ID for Q5 pathfinding", type=int, default=None
    )
    parser.add_argument(
        "--q5_end", help="Goal Vertex ID for Q5 pathfinding", type=int, default=None
    )
    parser.add_argument(
        "--output_path",
        help="Path to save the output report (only for non-interactive/benchmark mode)",
        default=None
    )

    args = parser.parse_args()

    if args.interactive:
        run_interactive_mode(args)
    elif args.non_interactive:
        run_non_interactive_mode(args)
    else:
        print("Please provide a valid mode of operation.")
        sys.exit(1)