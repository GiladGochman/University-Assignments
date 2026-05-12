class BayesianNode:
    def __init__(self, name, domain, parents=None, cpt=None):
        self.name = name
        self.domain = domain
        self.parents = parents if parents else []
        self.cpt = cpt if cpt else {}

    def get_prob(self, value, evidence):
        if not self.parents:
            return self.cpt[value]

        parent_vals = tuple(evidence[p] for p in self.parents)
        distribution = self.cpt.get(parent_vals)

        if distribution is None:
            raise ValueError(
                f"CPT missing entry for parents {parent_vals} in node {self.name}"
            )

        return distribution[value]
