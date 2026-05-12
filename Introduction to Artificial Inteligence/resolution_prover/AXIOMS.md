# Hurricane Evacuation Domain - First-Order Logic Axioms

## Situation Calculus Formulation

### Domain Constants

- **agent**: the evacuation vehicle (agent)
- **s0**: initial situation
- **loc1, loc2, loc3, loc4, ..**: vertices in the graph
- **kit**: amphibian kit

### Predicates

- `At(agent, loc, s)`: agent is at location `loc` in situation `s`
- `HasPeople(loc, s)`: location `loc` has people to rescue in situation `s`
- `HasKit(loc, s)`: location `loc` contains an amphibian kit in situation `s`
- `Equipped(agent, s)`: agent has equipped the amphibian kit in situation `s`
- `CanTraverse(from, to, s)`: agent can traverse edge from `from` to `to` in situation `s`
- `Flooded(from, to)`: edge from `from` to `to` is flooded (static fact)
- `AllPeopleRescued(s)`: all people have been rescued in situation `s`

### Actions

- `traverse(a, from, to, s)`: agent `a` moves from vertex `from` to `to`
- `equip(a, loc, s)`: agent `a` equips the amphibian kit at location `loc`
- `unequip(a, loc, s)`: agent `a` unequips the amphibian kit at location `loc`

---

## FOL Axioms (Natural Language)

### Initial State

1. `At(agent, loc1, s0)` — agent starts at location 1
2. `HasPeople(loc2, s0)` — location 2 has people needing rescue
3. `HasPeople(loc4, s0)` — location 4 has people needing rescue
4. `HasKit(loc1, s0)` — amphibian kit is at location 1 initially
5. `~Equipped(agent, s0)` — agent has not equipped the kit initially

### Static Facts (Flooded Edges)

6. `Flooded(loc1, loc2)` — edge 1-2 is flooded
7. `~Flooded(loc1, loc3)` — edge 1-3 is not flooded
8. `~Flooded(loc2, loc3)` — edge 2-3 is not flooded
9. `~Flooded(loc3, loc4)` — edge 3-4 is not flooded
10. `~Flooded(loc2, loc4)` — edge 2-4 is not flooded

### Traversal Preconditions

11. For all s: `CanTraverse(from, to, s)` if `~Flooded(from, to)` OR `Equipped(agent, s)`
    - If an edge is not flooded, traversal is allowed
    - If an edge is flooded, traversal requires the amphibian kit

### Traversal Effects (Effects axioms)

12. `At(agent, from, s) ∧ CanTraverse(from, to, s) → At(agent, to, Result(traverse(agent, from, to), s))`
13. `At(agent, loc, s) ∧ HasPeople(loc, s) → ~HasPeople(loc, Result(traverse(agent, _, loc), s))`
    - When agent arrives at a location with people, they are rescued

### Equip/Unequip Effects

14. `At(agent, loc, s) ∧ HasKit(loc, s) → Equipped(agent, Result(equip(agent, loc), s))`
15. `At(agent, loc, s) ∧ Equipped(agent, s) → ~Equipped(agent, Result(unequip(agent, loc), s))`
16. `At(agent, loc, s) ∧ Equipped(agent, s) → HasKit(loc, Result(unequip(agent, loc), s))`

### Closed-World Axiom

17. `AllPeopleRescued(s)` iff for all locations L: `~HasPeople(L, s)`

### Goal

18. `AllPeopleRescued(Result(seq_of_actions, s0))` — prove that there exists a sequence of actions that rescues all people

---

## CNF Conversion Example

To prove the evacuation is possible, we negate the goal:
**Negated Goal:** `~AllPeopleRescued(final_situation)`

This becomes:

```
∃ L: HasPeople(L, final_situation)
```

Which in CNF (with Skolemization) becomes:

```
HasPeople(loc_unsaved, final_situation)
```

Combined with axioms, the resolution prover derives a contradiction, proving the goal.

---

## Simplified Example for Assignment

We use a 4-vertex graph with:

- **Edges (undirected):**
  - 1-2 (flooded)
  - 1-3 (not flooded)
  - 2-3 (not flooded)
  - 3-4 (not flooded)
  - 2-4 (not flooded)

- **Initial State:**
  - Agent at vertex 1
  - People at vertices 2 and 4
  - Amphibian kit at vertex 1

- **Goal:** Rescue all people (prove `AllPeopleRescued`)

**Proof Strategy:**

1. Equip kit at location 1
2. Traverse 1 → 2 (flooded but equipped)
3. Rescue people at 2
4. Traverse 2 → 4 (not flooded)
5. Rescue people at 4
6. All people rescued ✓
