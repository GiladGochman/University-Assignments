# Assignment B1 - Resolution Theorem Prover

## Deliverables Checklist

### ✅ 1. Program Code and Executable

**Core Implementation:**

- `resolution_prover/term.py` - Data structures: Variable, Constant, Function, Literal, Clause
- `resolution_prover/parser.py` - CNF parser supporting ~, |, predicates, variables/constants/functions
- `resolution_prover/unify.py` - Robinson's unification algorithm with occurs-check
- `resolution_prover/resolution.py` - Binary resolution operator with tautology detection

**Executables:**

- `run_prover.py` - Interactive theorem prover (user-guided resolution)
- `run_proof_script.py` - Scripted prover with automated trace generation

**Package:**

- `resolution_prover/__init__.py` - Package initialization

### ✅ 2. FOL Axiomatization of Hurricane Domain

**Document:** `AXIOMS.md`

- Natural language FOL axioms using situation calculus
- Predicates: At, HasPeople, HasKit, Equipped, CanTraverse, Flooded
- Actions: traverse, equip, unequip
- Initial state, static facts, preconditions, effects
- Goal specification: AllPeopleRescued
- Example CNF conversion

### ✅ 3. CNF Formulations

**Example 1 - Simple Logical Proof:** `examples/example.cnf`

- Domain: Parent-Ancestor relationships
- 5 clauses demonstrating basic resolution
- Easily verifiable (2-step proof)

**Example 2 - Hurricane Evacuation:** `examples/hurricane.cnf`

- Full situation calculus formulation
- 4-vertex graph with flooded edge
- People at vertices 2 and 4, kit at vertex 1
- Demonstrates planning and action effects

**Example 3 - Quiz Scenario:** `examples/quiz.cnf`

- Simplified 3-vertex evacuation
- Alternative to HW1 example
- Demonstrates multiple solution paths

### ✅ 4. Proof Traces

**Trace 1:** `TRACE_EXAMPLE.txt`

- Detailed walkthrough of simple logical proof
- Shows unification, MGU, resolvent generation
- 2 resolution steps deriving empty clause
- Fully annotated with logical steps

**Trace 2:** `TRACE_HURRICANE.txt`

- Hurricane problem overview and solution strategy
- Situation calculus axioms explained
- Optimal action sequence outlined
- Resolution proof structure described

**Trace 3:** `TRACE_QUIZ.txt`

- Quiz scenario problem setup
- Two alternative solution strategies
- Resolution proof steps outlined
- Key insights and causal reasoning explained

### ✅ 5. Proof Scripts (Automated)

**Script 1:** `proofs/example.script`

- 2 resolution steps for simple proof
- Format: `i li j lj` per line

**Script 2:** `proofs/hurricane.script`

- Sequence of steps for hurricane evacuation
- Multi-step proof with action effects

**Script 3:** `proofs/quiz.script`

- Proof for quiz scenario
- Demonstrates alternative solution path

### ✅ 6. Documentation

**README.md**

- Complete usage guide
- Syntax explanation with examples
- Quick start instructions
- Project structure overview
- Implementation details (unification, resolution, proof by contradiction)
- Testing procedures
- Design decisions and limitations

**AXIOMS.md**

- Detailed axiomatization in situation calculus
- FOL syntax and predicates
- Action definitions and effects
- Initial state and static facts
- Closed-world assumptions
- Goal specification
- CNF conversion explanation

## Quick Verification

### Test 1: Simple Proof (2 steps)

```bash
python run_prover.py examples/example.cnf
# Commands: r 3 0 1 0; r 5 0 4 0
# Expected: Empty clause → Goal proved
```

### Test 2: Scripted Execution with Trace

```bash
python run_proof_script.py examples/example.cnf proofs/example.script
# Expected: Proof SUCCESS message
```

### Test 3: Interactive Hurricane Problem

```bash
python run_prover.py examples/hurricane.cnf
# Manually execute resolution steps from proofs/hurricane.script
```

## Summary of Work

| Component             | File(s)                             | Status                 |
| --------------------- | ----------------------------------- | ---------------------- |
| Unification           | unify.py                            | ✅ Implemented         |
| Resolution            | resolution.py                       | ✅ Implemented         |
| Parser                | parser.py                           | ✅ Implemented         |
| Data structures       | term.py                             | ✅ Implemented         |
| Interactive CLI       | run_prover.py                       | ✅ Implemented         |
| Script executor       | run_proof_script.py                 | ✅ Implemented         |
| Example 1 (logical)   | example.cnf                         | ✅ Complete with trace |
| Example 2 (hurricane) | hurricane.cnf + TRACE_HURRICANE.txt | ✅ Complete            |
| Example 3 (quiz)      | quiz.cnf + TRACE_QUIZ.txt           | ✅ Complete            |
| Axiomatization docs   | AXIOMS.md                           | ✅ Complete            |
| User guide            | README.md                           | ✅ Complete            |

## Key Features Implemented

1. **Robinson's Unification** - with occurs-check, handles variables/constants/functions
2. **Binary Resolution** - resolves complementary literals, applies MGU, removes tautologies
3. **CNF Parsing** - simple syntax (case-based variable/constant distinction)
4. **Semi-Manual Control** - user selects which clauses/literals to resolve
5. **Situation Calculus** - natural formulation for action planning domain
6. **Proof by Contradiction** - negates goal, derives empty clause

## Assignment Requirements Coverage

✅ **Constructing a partial resolution theorem proving program**

- Unification algorithm implemented
- Resolution operator implemented
- Semi-manual interface (user-guided)

✅ **Exercising program on Hurricane evacuation domain**

- Axioms written in situation calculus FOL
- Converted to CNF format
- Multiple examples provided (HW1, quiz)

✅ **Proof traces**

- Empty clause derivation shown for all examples
- Detailed walkthrough of resolution steps
- Contradiction demonstrated

✅ **Deliverables**

- Program code and executables
- FOL axioms (natural language + CNF)
- Example CNF files
- Proof traces (both document and script formats)
- Documentation and usage guide

---

**Status:** Ready for demonstration and grading  
**Date:** February 15, 2025  
**Submission location:** `resolution_prover/` folder
