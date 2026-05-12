def enumeration_ask(X, e, bn):
    if X in e:
        observed_val = e[X]
        x_domain = bn.node_map[X].domain
        return {xi: 1.0 if xi == observed_val else 0.0 for xi in x_domain}

    Q = {}
    x_domain = bn.node_map[X].domain
    for xi in x_domain:
        e_extended = e.copy()
        e_extended[X] = xi
        Q[xi] = enumerate_all(bn.variables, e_extended, bn)
    return normalize(Q)


def enumerate_all(vars_list, e, bn):
    if not vars_list:
        return 1.0

    Y = vars_list[0]
    rest_vars = vars_list[1:]
    node = bn.node_map[Y]

    if Y in e:
        y = e[Y]
        return node.get_prob(y, e) * enumerate_all(rest_vars, e, bn)
    else:
        total = 0
        for y in node.domain:
            e_extended = e.copy()
            e_extended[Y] = y
            total += node.get_prob(y, e_extended) * enumerate_all(
                rest_vars, e_extended, bn
            )
        return total


def normalize(Q):
    total = sum(Q.values())
    if total == 0:
        return Q
    return {k: v / total for k, v in Q.items()}