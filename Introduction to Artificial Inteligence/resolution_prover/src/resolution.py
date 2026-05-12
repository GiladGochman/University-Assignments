from typing import List, Tuple, Optional
from .term import Clause, Literal
from .unify import unify

def resolve(ci: Clause, li_index: int, cj: Clause, lj_index: int):
    # resolve clause ci on literal at index li_index with clause cj at lj_index
    lit_i = ci.lits[li_index]
    lit_j = cj.lits[lj_index]
    if lit_i.pred != lit_j.pred or lit_i.positive == lit_j.positive:
        return None  # not complementary
    s = unify_pair(lit_i, lit_j)
    if s is None:
        return None
    # build new literals
    new_lits = []
    for idx, l in enumerate(ci.lits):
        if idx != li_index:
            new_lits.append(l.substitute(s))
    for idx, l in enumerate(cj.lits):
        if idx != lj_index:
            new_lits.append(l.substitute(s))
    # remove duplicates
    unique = []
    for l in new_lits:
        if l not in unique:
            unique.append(l)
    resolvent = Clause(unique)
    if resolvent.is_tautology():
        return None
    return resolvent

def unify_pair(a: Literal, b: Literal):
    # a and b have same predicate name and opposite signs
    s = {}
    for ta, tb in zip(a.args, b.args):
        s = unify(ta.substitute(s), tb.substitute(s), s)
        if s is None:
            return None
    return s
