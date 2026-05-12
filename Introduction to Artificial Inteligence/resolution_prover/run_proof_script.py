"""
Script to run a pre-defined sequence of resolution steps and output a trace.
Usage: python run_proof_script.py <cnf_file> <script_file>
"""

import sys
from src import parser, resolution

def run_proof_script(cnf_path, script_path):
    """Load CNF and execute resolution steps from a script."""
    # Load CNF clauses
    clauses = parser.load_cnf(cnf_path)
    kb = list(clauses)
    
    print(f"=== Resolution Proof Trace ===")
    print(f"CNF File: {cnf_path}")
    print(f"Script: {script_path}\n")
    
    print("Initial Knowledge Base:")
    for i, c in enumerate(kb):
        print(f"  [{i}] {c}")
    print()
    
    # Parse and execute script
    step_count = 0
    contradiction_found = False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                if line.startswith('#'):
                    print(f"[Step {step_count}] Comment: {line[1:].strip()}")
                continue
            
            # Parse resolution command: i li j lj
            parts = line.split()
            if len(parts) < 4:
                print(f"Warning: line {line_num} invalid, skipping: {line}")
                continue
            
            try:
                i, li, j, lj = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            except ValueError:
                print(f"Warning: line {line_num} has non-integer values, skipping: {line}")
                continue
            
            # Check bounds
            if i < 0 or j < 0 or i >= len(kb) or j >= len(kb):
                print(f"Warning: line {line_num} index out of range: {line}")
                continue
            
            # Perform resolution
            step_count += 1
            print(f"Step {step_count}:")
            print(f"  Resolve clause [{i}] and clause [{j}]")
            print(f"    Clause [{i}]: {kb[i]}")
            print(f"    Clause [{j}]: {kb[j]}")
            print(f"    On literals [{li}] and [{lj}]")
            
            resolvent = resolution.resolve(kb[i], li, kb[j], lj)
            
            if resolvent is None:
                print(f"    Result: No resolvent (not unifiable, not complementary, or tautology)")
            else:
                print(f"    Result: {resolvent}")
                new_clause_idx = len(kb)
                kb.append(resolvent)
                print(f"    Added as clause [{new_clause_idx}]")
                
                if len(resolvent.lits) == 0:
                    contradiction_found = True
                    print(f"\n*** CONTRADICTION DERIVED ***")
                    print(f"Empty clause (NIL) obtained at step {step_count}")
                    break
            print()
    
    print("\n=== Final Knowledge Base ===")
    for i, c in enumerate(kb):
        print(f"  [{i}] {c}")
    
    print(f"\n=== Summary ===")
    print(f"Steps executed: {step_count}")
    print(f"Contradiction found: {contradiction_found}")
    if contradiction_found:
        print(f"Proof SUCCESS: CNF formula is unsatisfiable (goal proved)")
    else:
        print(f"Proof INCOMPLETE: more steps needed")
    
    return contradiction_found

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_proof_script.py <cnf_file> <script_file>")
        print("Example: python run_proof_script.py examples/hurricane.cnf proofs/hurricane.script")
        return
    
    cnf_path = sys.argv[1]
    script_path = sys.argv[2]
    
    try:
        success = run_proof_script(cnf_path, script_path)
        sys.exit(0 if success else 1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
