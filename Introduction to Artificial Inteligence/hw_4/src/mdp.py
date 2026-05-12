from collections import deque
import itertools

EPSILON = 1e-9


class BeliefState:
    def __init__(self, v_id, has_kit, E_prob, graph, params):
        self.v_id = v_id
        self.has_kit = has_kit
        self.E_prob = E_prob
        self.graph = graph
        self.params = params
        self.v = self.graph.vertices[self.v_id]

        sorted_probs = sorted(self.E_prob.items())
        self.id = f"{v_id}|K:{has_kit}|{tuple(sorted_probs)}"

        self.utility_value = -float("inf")
        self.optimal_action = None

    def Bellman_equation(self, belief_states_map):
        best_val = -float("inf")
        best_act = None

        if self.v.has_kit and not self.has_kit:
            cost = self.params["EC"]
            next_bs_id = BeliefState.make_id(self.v_id, True, self.E_prob)
            if next_bs_id in belief_states_map:
                val = -cost + belief_states_map[next_bs_id].utility_value
                if val > best_val:
                    best_val = val
                    best_act = "Equip"

        if self.has_kit:
            cost = self.params["UC"]
            next_bs_id = BeliefState.make_id(self.v_id, False, self.E_prob)
            if next_bs_id in belief_states_map:
                val = -cost + belief_states_map[next_bs_id].utility_value
                if val > best_val:
                    best_val = val
                    best_act = "Unequip"

        for e_id, edge in self.v.edges.items():
            neighbor = edge.get_other_vertex(self.v)
            status = self.E_prob.get(e_id)

            if status == 1 and not self.has_kit:
                continue

            move_cost = edge.w * (self.params["FF"] if self.has_kit else 1)

            expected_future = 0

            uncertain_at_next = [
                e for e in neighbor.edges.values() if self.E_prob.get(e.id) == -1
            ]

            if not uncertain_at_next:
                next_id = BeliefState.make_id(neighbor.id, self.has_kit, self.E_prob)
                expected_future = belief_states_map[next_id].utility_value
            else:
                outcomes = list(
                    itertools.product([0, 1], repeat=len(uncertain_at_next))
                )

                for outcome in outcomes:
                    prob = 1.0
                    temp_prob = self.E_prob.copy()

                    for i, u_edge in enumerate(uncertain_at_next):
                        is_flooded = outcome[i]
                        temp_prob[u_edge.id] = is_flooded
                        prob *= u_edge.prob if is_flooded else (1.0 - u_edge.prob)

                    next_id = BeliefState.make_id(neighbor.id, self.has_kit, temp_prob)
                    expected_future += (
                        prob * belief_states_map[next_id].utility_value
                    )

            val = -move_cost + expected_future
            if val > best_val:
                best_val = val
                best_act = neighbor.id

        return best_val, best_act

    @staticmethod
    def make_id(v_id, has_kit, E_prob):
        sorted_probs = sorted(E_prob.items())
        return f"{v_id}|K:{has_kit}|{tuple(sorted_probs)}"


class MDPSolver:
    def __init__(self, graph, start, target, params):
        self.graph = graph
        self.start = start
        self.target = target
        self.params = params
        self.belief_states = {}

    def check_legal_scenario(self):
        queue = [self.start]
        visited = {self.start}
        reached_target = False
        reached_kit = False

        while queue:
            curr = queue.pop(0)
            if curr == self.target:
                reached_target = True
            if self.graph.vertices[curr].has_kit:
                reached_kit = True

            for e in self.graph.vertices[curr].edges.values():
                if e.prob < EPSILON:
                    neighbor = e.get_other_vertex(self.graph.vertices[curr])
                    if neighbor.id not in visited:
                        visited.add(neighbor.id)
                        queue.append(neighbor.id)

        if reached_target or reached_kit:
            return True
        return False
    def get_edge_inital_status(self,edge):
        if edge.prob < EPSILON:
            return 0
        elif edge.prob > (1.0 - EPSILON):
            return 1
        else:
            return -1
        
    def build_reachable_states(self):
        init_prob = {
            e.id: self.get_edge_inital_status(e)
            for e in self.graph.edges.values()
        }

        start_v = self.graph.vertices[self.start]
        start_uncertain = [e for e in start_v.edges.values() if init_prob[e.id] == -1]

        queue = deque()

        if not start_uncertain:
            belief_state = BeliefState(self.start, False, init_prob, self.graph, self.params)
            self.belief_states[belief_state.id] = belief_state
            queue.append(belief_state)
        else:
            for outcome in itertools.product([0, 1], repeat=len(start_uncertain)):
                temp = init_prob.copy()
                for i, e in enumerate(start_uncertain):
                    temp[e.id] = outcome[i]
                belief_state = BeliefState(self.start, False, temp, self.graph, self.params)
                self.belief_states[belief_state.id] = belief_state
                queue.append(belief_state)

        processed = set(self.belief_states.keys())
        while queue:
            belief_state = queue.popleft()
            if belief_state.v_id == self.target:
                continue
            def add_next_state(next_vertex_id, next_has_kit, next_edge_beliefs):
                next_state_id = BeliefState.make_id(next_vertex_id, next_has_kit, next_edge_beliefs)
                
                if next_state_id not in processed:
                    next_belief_state = BeliefState(
                        next_vertex_id, next_has_kit, next_edge_beliefs, self.graph, self.params
                    )
                    self.belief_states[next_state_id] = next_belief_state
                    processed.add(next_state_id)
                    queue.append(next_belief_state)


            if belief_state.v.has_kit and not belief_state.has_kit:
                add_next_state(belief_state.v_id, True, belief_state.E_prob)
            if belief_state.has_kit:
                add_next_state(belief_state.v_id, False, belief_state.E_prob)

            for edge in belief_state.v.edges.values():
                edge_prob = belief_state.E_prob.get(edge.id)
                if edge_prob == 1 and not belief_state.has_kit:
                    continue

                neighbor = edge.get_other_vertex(belief_state.v)
                n_uncertain = [
                    e for e in neighbor.edges.values() if belief_state.E_prob.get(e.id) == -1
                ]

                if not n_uncertain:
                    add_next_state(neighbor.id, belief_state.has_kit, belief_state.E_prob)
                else:
                    for outcome in itertools.product([0, 1], repeat=len(n_uncertain)):
                        temp = belief_state.E_prob.copy()
                        for i, e in enumerate(n_uncertain):
                            temp[e.id] = outcome[i]
                        add_next_state(neighbor.id, belief_state.has_kit, temp)

    def value_iteration(self, epsilon=1e-4):
        for bs in self.belief_states.values():
            bs.utility_value = 0.0 if bs.v_id == self.target else -10000.0

        iter_count = 0
        while True:
            max_delta = 0
            iter_count += 1
            for bs in self.belief_states.values():
                if bs.v_id == self.target:
                    continue
                val, act = bs.Bellman_equation(self.belief_states)
                diff = abs(bs.utility_value - val)
                if diff > max_delta:
                    max_delta = diff
                bs.utility_value = val
                bs.optimal_action = act

            if max_delta < epsilon or iter_count > 1000:
                break
        return iter_count
