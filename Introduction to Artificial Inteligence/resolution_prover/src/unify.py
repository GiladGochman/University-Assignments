from typing import Dict, Optional
from .term import Variable, Constant, Function, Term

Subst = Dict[Variable, Term]

def occurs_check(var: Variable, term: Term, subs: Subst) -> bool:
    t = term
    if isinstance(t, Variable):
        t = subs.get(t, t)
        return t == var
    if isinstance(t, Function):
        for a in t.args:
            if occurs_check(var, a, subs):
                return True
    return False

def unify_var(var: Variable, x: Term, subs: Subst) -> Optional[Subst]:
    if var in subs:
        return unify(subs[var], x, subs)
    if isinstance(x, Variable) and x in subs:
        return unify(var, subs[x], subs)
    if occurs_check(var, x, subs):
        return None
    subs2 = dict(subs)
    subs2[var] = x
    return subs2

def unify(x: Term, y: Term, subs: Optional[Subst] = None) -> Optional[Subst]:
    if subs is None:
        subs = {}
    if x == y:
        return dict(subs)
    if isinstance(x, Variable):
        return unify_var(x, y, subs)
    if isinstance(y, Variable):
        return unify_var(y, x, subs)
    if isinstance(x, Function) and isinstance(y, Function) and x.name == y.name and len(x.args) == len(y.args):
        s = dict(subs)
        for a, b in zip(x.args, y.args):
            s = unify(a.substitute(s), b.substitute(s), s)
            if s is None:
                return None
        return s
    if isinstance(x, Constant) and isinstance(y, Constant) and x.name == y.name:
        return dict(subs)
    return None
