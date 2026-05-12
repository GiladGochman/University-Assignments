# Resolution Theorem Prover - Assignment B1

A **partial resolution theorem prover** for first-order logic in CNF (Conjunctive Normal Form). Implements Robinson's unification algorithm and binary resolution for semi-manual proof construction.

## Project Overview

This assignment implements:

1. **Unification algorithm** with occurs-check
2. **Binary resolution** for CNF formulas
3. **Semi-manual interface** where user selects which clauses/literals to resolve
4. **Hurricane evacuation domain** axiomatized in situation calculus
5. **Multiple examples** with proof traces

## Quick Start

### Interactive Mode

```bash
python run_prover.py examples/example.cnf
```

Commands:

- `r i li j lj` - resolve clause i at literal li with clause j at literal lj
- `a` - add new clause
- `q` - quit

### Scripted Proof (with trace output)

```bash
python run_proof_script.py examples/example.cnf proofs/example.script
```

## Syntax Guide

**CNF Format:**

- One clause per line
- Disjunction: `|` (OR operator)
- Negation: `~` (prefix)
- Variables: UPPERCASE (X, Y, Z)
- Constants: lowercase (alice, loc1, s0)
- Functions: `f(X,Y)` or `result(s)`

**Example:**

```
Parent(alice, bob) | ~Ancestor(alice, bob)
~Parent(X, Y) | Ancestor(X, Y)
~Ancestor(alice, bob)
```

## Examples Provided

### 1. Simple Logical Proof (`examples/example.cnf`)

**Domain:** Parent-Ancestor relationships  
**Goal:** Prove Ancestor(alice, bob)  
**Resolution steps:** 2

```bash
python run_prover.py examples/example.cnf
# r 3 0 1 0
# r 5 0 4 0
# Empty clause derived → Goal proved
```

### 2. Hurricane Evacuation (`examples/hurricane.cnf`)

**Domain:** Based on HW1 hurricane evacuation problem  
**Scenario:**

- 4-vertex graph
- Agent starts at vertex 1
- People stranded at vertices 2 and 4
- Amphibian kit at vertex 1 (required for flooded edge 1-2)

**Goal:** Prove all people can be rescued

**Axioms (Situation Calculus):**

- Initial state: `At(agent, loc1, s0)`, `HasPeople(loc2, s0)`, `HasPeople(loc4, s0)`, etc.
- Static facts: `Flooded(loc1, loc2)` (edge is flooded)
- Preconditions: Can traverse flooded edge only if equipped with kit
- Effects: Moving to a location with people rescues them
- Goal: `~HasPeople(L, s)` for all locations L

**Proof strategy:**

1. Equip kit at loc1
2. Traverse flooded edge 1→2 (now possible)
3. Rescue people at loc2
4. Traverse 2→4
5. Rescue people at loc4
6. Negated goal contradicted → All people rescued ✓

### 3. Quiz Scenario (`examples/quiz.cnf`)

**Domain:** Simplified 3-vertex evacuation  
**Setup:** People at vertices 2, 3; Kit at vertex 1; Edge 1-2 flooded  
**Goal:** Prove evacuation possible

## Deliverables Checklist

- ✅ **Prover code:** `resolution_prover/` module with term.py, parser.py, unify.py, resolution.py
- ✅ **Executable:** `run_prover.py` (interactive), `run_proof_script.py` (scripted)
- ✅ **FOL axioms:** `AXIOMS.md` documenting situation calculus formulation
- ✅ **CNF formulas:** `examples/*.cnf` files for 3 scenarios
- ✅ **Proof traces:** `proofs/*.script` files showing resolution steps
- ✅ **Documentation:** README.md and inline code comments

## Project Structure

```
resolution_prover/
├── resolution_prover/          # Main package
│   ├── __init__.py
│   ├── term.py                 # Term, Variable, Constant, Function, Literal, Clause
│   ├── parser.py               # CNF parser (parses .cnf files)
│   ├── unify.py                # Unification with occurs-check
│   └── resolution.py           # Binary resolution operator
├── run_prover.py               # Interactive mode
├── run_proof_script.py          # Scripted mode with trace
├── AXIOMS.md                   # Domain axiomatization docs
├── examples/                   # CNF input files
│   ├── example.cnf             # Simple logical proof
│   ├── hurricane.cnf           # Hurricane evacuation (4-vertex)
│   └── quiz.cnf                # Quiz scenario (3-vertex)
├── proofs/                     # Proof scripts
│   ├── example.script
│   ├── hurricane.script
│   └── quiz.script
└── README.md                   # This file
```

## Implementation Notes

### Unification Algorithm

- Robinson's algorithm with **occurs-check** to prevent infinite structures
- Handles variables, constants, and function symbols
- Returns MGU (most general unifier) or None if unification fails

### Binary Resolution

- Resolves two clauses on one pair of complementary literals
- Applies MGU to eliminate resolved literals
- Detects and rejects **tautologies** (clauses with both p and ~p)
- Removes duplicate literals from resolvent

### Proof by Contradiction

To prove goal P:

1. Add `~P` (negated goal) to KB
2. Perform resolution steps until empty clause is derived
3. Empty clause = contradiction → P is proved

### Example Trace (Simple)

```
Initial KB:
[0] Parent(alice, bob) | ~Ancestor(alice, bob)
[1] ~Parent(X, Y) | Ancestor(X, Y)
[2] ~Ancestor(X, Y) | Ancestor(X, Z) | Ancestor(Z, Y)
[3] Parent(alice, bob)
[4] ~Ancestor(alice, bob)

Step 1: Resolve [3] and [1] on literals [0,0]
        Unify Parent(alice,bob) with ~Parent(X,Y)
        MGU: {X→alice, Y→bob}
        Resolvent: Ancestor(alice, bob) → [5]

Step 2: Resolve [5] and [4] on literals [0,0]
        Unify Ancestor(alice,bob) with ~Ancestor(alice,bob)
        MGU: {} (empty, they match exactly)
        Resolvent: <empty clause> → Proof complete!
```

## Testing

### Verify Example

```bash
python run_proof_script.py examples/example.cnf proofs/example.script
```

Expected: `Proof SUCCESS: CNF formula is unsatisfiable (goal proved)`

### Interactive Verification

```bash
python run_prover.py examples/hurricane.cnf
# Manually perform resolution steps guided by the .script file
```

## Design Decisions

1. **Simple syntax** - No complex parsing; variables/constants distinguished by case
2. **Semi-manual control** - User specifies which clauses/literals to resolve (avoids full search)
3. **No closed-world assumption** - Explicitly state facts and negations
4. **Equality as predicate** - Add axioms like `X=X` manually if needed
5. **Situation calculus** - Natural for modeling actions and state changes in domain

## Limitations

- No automatic clause selection (user guides resolution)
- No support for equality unification (use explicit predicates)
- No arithmetic constraints
- Single-agent assumption (though could be extended)

## References

- Situation calculus: McCarthy & Hayes (1969)
- Resolution theorem proving: Robinson (1965)
- Unification: Robinson (1965), Occurs-check: not always necessary but safer

## Assignment Due Date

February 17, 2025 (Monday)

---

**For detailed axiomatization, see [AXIOMS.md](AXIOMS.md)**
