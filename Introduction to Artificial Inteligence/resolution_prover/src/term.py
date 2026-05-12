from typing import List, Dict, Union

class Term:
    def substitute(self, subs: Dict["Variable", "Term"]):
        raise NotImplementedError()

class Variable(Term):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return self.name
    def substitute(self, subs):
        return subs.get(self, self)
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name
    def __hash__(self):
        return hash(("Var", self.name))

class Constant(Term):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return self.name
    def substitute(self, subs):
        return self
    def __eq__(self, other):
        return isinstance(other, Constant) and self.name == other.name
    def __hash__(self):
        return hash(("Const", self.name))

class Function(Term):
    def __init__(self, name: str, args: List[Term]):
        self.name = name
        self.args = args
    def __repr__(self):
        return f"{self.name}({', '.join(map(str,self.args))})"
    def substitute(self, subs):
        return Function(self.name, [a.substitute(subs) for a in self.args])
    def __eq__(self, other):
        return isinstance(other, Function) and self.name == other.name and self.args == other.args
    def __hash__(self):
        return hash(("Fun", self.name, tuple(self.args)))

class Literal:
    def __init__(self, pred: str, args: List[Term], positive: bool = True):
        self.pred = pred
        self.args = args
        self.positive = positive
    def __repr__(self):
        sign = "" if self.positive else "~"
        return f"{sign}{self.pred}({', '.join(map(str,self.args))})"
    def substitute(self, subs: Dict[Variable, Term]):
        return Literal(self.pred, [a.substitute(subs) for a in self.args], self.positive)
    def negate(self):
        return Literal(self.pred, self.args, not self.positive)
    def __eq__(self, other):
        return isinstance(other, Literal) and self.pred == other.pred and self.args == other.args and self.positive == other.positive
    def __hash__(self):
        return hash((self.pred, tuple(self.args), self.positive))

class Clause:
    def __init__(self, literals: List[Literal]):
        # keep order but allow set-like operations
        self.lits = list(literals)
    def __repr__(self):
        return " | ".join(map(str, self.lits)) if self.lits else "<empty>"
    def substitute(self, subs: Dict[Variable, Term]):
        return Clause([lit.substitute(subs) for lit in self.lits])
    def is_tautology(self):
        s = set()
        for lit in self.lits:
            if Literal(lit.pred, lit.args, not lit.positive) in s:
                return True
            s.add(lit)
        return False
