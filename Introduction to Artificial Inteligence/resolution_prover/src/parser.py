import re
from .term import Variable, Constant, Function, Literal, Clause

token_re = re.compile(r"\s*(~)?\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$")

def parse_term(s: str):
    s = s.strip()
    # function or variable/constant
    if '(' in s and s.endswith(')'):
        name, rest = s.split('(', 1)
        args = rest[:-1]
        parts = split_args(args)
        return Function(name.strip(), [parse_term(p) for p in parts])
    # variable: starts with uppercase
    if s and s[0].isupper():
        return Variable(s)
    return Constant(s)

def split_args(s: str):
    parts = []
    depth = 0
    cur = []
    for ch in s:
        if ch == ',' and depth == 0:
            parts.append(''.join(cur).strip())
            cur = []
            continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        cur.append(ch)
    if cur:
        parts.append(''.join(cur).strip())
    return [p for p in parts if p!='']

def parse_literal(token: str):
    token = token.strip()
    m = token_re.match(token)
    if not m:
        raise ValueError(f"Can't parse literal: {token}")
    neg, pred, args = m.groups()
    parts = split_args(args)
    args_t = [parse_term(p) for p in parts] if parts else []
    return Literal(pred, args_t, positive=(neg is None))

def parse_clause(line: str):
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    parts = [p.strip() for p in line.split('|')]
    lits = [parse_literal(p) for p in parts]
    return Clause(lits)

def load_cnf(path: str):
    clauses = []
    with open(path,'r', encoding='utf-8') as f:
        for ln in f:
            c = parse_clause(ln)
            if c:
                clauses.append(c)
    return clauses
