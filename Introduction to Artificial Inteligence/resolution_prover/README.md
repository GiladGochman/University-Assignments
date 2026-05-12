Resolution theorem prover (semi-manual)

Usage

- `python run_prover.py examples/example.cnf` to start interactive session.
- CNF syntax: one clause per line, disjunctions separated by `|`.
- Literal syntax: optional `~` then `Pred(term1,term2,...)`.
- Variables: start with Uppercase letter. Constants/functions: start with lowercase letter.
- Example clause: `~At(Agent,loc) | Holds(loc)`

This is a lightweight tool that performs unification and binary resolution given user-chosen literals.
Replace `examples/hurricane.cnf` with your axioms in CNF and run the prover.
