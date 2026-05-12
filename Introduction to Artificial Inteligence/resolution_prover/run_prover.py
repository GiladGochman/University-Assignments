import sys
from src import parser
from src import resolution

def interactive_loop(clauses):
    kb = list(clauses)
    step = 0
    while True:
        print('\nKnowledge base:')
        for i,c in enumerate(kb):
            print(f"[{i}] {c}")
        cmd = input('\nEnter: r i li j lj (resolve) | q (quit) | a (add clause) | s (save trace): ').strip()
        if not cmd:
            continue
        if cmd == 'q':
            break
        if cmd.startswith('a'):
            rest = cmd[1:].strip()
            if rest:
                c = parser.parse_clause(rest)
                if c:
                    kb.append(c)
            else:
                ln = input('clause> ')
                c = parser.parse_clause(ln)
                if c:
                    kb.append(c)
            continue
        if cmd.startswith('r'):
            parts = cmd.split()
            if len(parts) < 5:
                print('Usage: r i li j lj')
                continue
            _, i, li, j, lj = parts[:5]
            try:
                i = int(i); li = int(li); j = int(j); lj = int(lj)
            except:
                print('bad indices')
                continue
            if i<0 or j<0 or i>=len(kb) or j>=len(kb):
                print('index out of range')
                continue
            res = resolution.resolve(kb[i], li, kb[j], lj)
            step += 1
            if res is None:
                print('No resolvent (either not complementary, not unifiable, or tautology).')
            else:
                print(f'Resolvent [{step}]: {res}')
                kb.append(res)
                if not res.lits:
                    print('\nContradiction derived (empty clause)!')
                    break
            continue
        print('Unknown command')

def main():
    if len(sys.argv) < 2:
        print('Usage: python run_prover.py <cnf-file>')
        return
    path = sys.argv[1]
    clauses = parser.load_cnf(path)
    print(f'Loaded {len(clauses)} clauses from {path}')
    interactive_loop(clauses)

if __name__ == '__main__':
    main()
