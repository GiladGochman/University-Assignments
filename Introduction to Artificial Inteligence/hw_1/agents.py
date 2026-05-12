import heapq
from action import Action
from abc import ABC, abstractmethod

LIMIT = 10000


class Agent(ABC):
    def __init__(self,agent_id, vertex_id, environment, game_settings, **kwargs):
        self.agent_id=agent_id
        self.vertex_id = vertex_id
        self.is_equipped = False
        self.time_taken = 0.0
        self.actions_count = 0
        self.people_saved = 0
        self.is_terminated = False
        self.environment = environment
        self.game_settings = game_settings
        self.time_passed = 0

    @property
    def score(self):
        return (self.people_saved * 1000) - (self.time_taken + self.time_passed)

    def _shortest_path(self, start_id):
        distances = {}
        predecessors = {}

        for v_id in self.environment.vertices:
            distances[v_id] = float("inf")

        distances[start_id] = 0.0

        heap = [(0.0, start_id)]

        while heap:
            current_time, current_id = heapq.heappop(heap)
            current_state = current_id

            if current_time > distances[current_state]:
                continue

            if current_id in self.environment.edges:
                for neighbor_id in self.environment.edges[current_id]:
                    cost = self.get_traverse_cost(
                        current_id, neighbor_id, self.is_equipped
                    )

                    if cost is not None and cost != float("inf"):
                        new_time = current_time + cost
                        neighbor_state = neighbor_id

                        if new_time < distances[neighbor_state]:
                            distances[neighbor_state] = new_time
                            predecessors[neighbor_state] = (
                                current_id,
                                f"traverse_{neighbor_id}",
                            )
                            heapq.heappush(heap, (new_time, neighbor_id))

        return distances, predecessors

    def decide_action(self):
        raise NotImplementedError

    def pickup_people_at_current_vertex(self):
        if self.environment.vertices[self.vertex_id].people_to_rescue > 0:
            self.people_saved += self.environment.vertices[
                self.vertex_id
            ].people_to_rescue
            self.environment.vertices[self.vertex_id].people_to_rescue = 0

    def traverse(self, target_id):
        self.pickup_people_at_current_vertex()

        if target_id not in self.environment.edges.get(self.vertex_id, {}):
            self.noop()
            return

        edge = self.environment.edges[self.vertex_id][target_id]

        if self.is_equipped:
            self.time_taken += edge.weight * self.game_settings.amphibian_penalty_factor
            self.vertex_id = target_id
            self.actions_count += 1
        elif not edge.is_flooded:
            self.time_taken += edge.weight
            self.vertex_id = target_id
            self.actions_count += 1
        else:
            self.noop()
            return

        self.pickup_people_at_current_vertex()

    def equip(self):
        self.pickup_people_at_current_vertex()

        if self.environment.vertices[self.vertex_id].amphibian_kits > 0:
            self.is_equipped = True
            self.environment.vertices[self.vertex_id].amphibian_kits -= 1
        self.actions_count += 1
        self.time_taken += self.game_settings.equip_time_unit

    def unequip(self):
        self.pickup_people_at_current_vertex()

        if self.is_equipped:
            self.is_equipped = False
            self.environment.vertices[self.vertex_id].amphibian_kits += 1
        self.actions_count += 1
        self.time_taken += self.game_settings.unequip_time_unit

    def noop(self):
        self.pickup_people_at_current_vertex()

        self.actions_count += 1
        self.time_taken += 1

    def terminate(self):
        self.pickup_people_at_current_vertex()

        self.is_terminated = True
        self.actions_count += 1

    def get_traverse_cost(self, u_id, v_id, is_equipped):
        edge = self.environment.edges.get(u_id, {}).get(v_id)

        if not edge:
            return None

        if is_equipped:
            return edge.weight * self.game_settings.amphibian_penalty_factor
        elif not edge.is_flooded:
            return edge.weight
        else:
            return float("inf")

    def _get_next_traverse_node(self, predecessors, start_id, target_id):
        current = target_id

        if current not in predecessors and current != start_id:
            return None

        while current != start_id:
            parent_id, _ = predecessors[current]

            if parent_id == start_id:
                return current

            current = parent_id

        return None


class HumanAgent(Agent):
    def decide_action(self):
        while True:
            input_action_id = input(
                "Enter action ID:\n"
                "0: TRAVERSE (requires target vertex ID)\n"
                "1: EQUIP\n"
                "2: UNEQUIP\n"
                "3: NO_OP\n"
                "4: TERMINATE\n"
                ">>> "
            ).strip()
            if len(input_action_id) > 0 and input_action_id.isdigit():
                input_action_id = int(input_action_id)
                break

        if input_action_id == 0:
            target_id = int(input("Enter target vertex id: ").strip())
            return (Action.TRAVERSE, target_id)
        elif input_action_id == 1:
            return (Action.EQUIP, None)
        elif input_action_id == 2:
            return (Action.UNEQUIP, None)
        elif input_action_id == 3:
            return (Action.NO_OP, None)
        elif input_action_id == 4:
            return (Action.TERMINATE, None)
        else:
            return (Action.NO_OP, None)


class ThiefAgent(Agent):
    def pickup_people_at_current_vertex(self):
        pass

    def get_list_of_other_agent_ids(self):
        return [
            a.vertex_id
            for a in self.environment.agents
            if a != self and not a.is_terminated
        ]

    def _shortest_path_for_location_of_kit(self,start_id = None,vertex_masking={}):
        if start_id is None:
            start_id = self.vertex_id
        distances, predecessors = self._shortest_path(start_id)

        min_time = float("inf")
        best_target_id = None

        for v_id, vertex in self.environment.vertices.items():
            amphibian_kits=vertex_masking.get(v_id,vertex.amphibian_kits)
            if amphibian_kits > 0:
                time_to_target = distances.get(v_id, float("inf"))

                if time_to_target < min_time:
                    min_time = time_to_target
                    best_target_id = v_id

                elif (
                    best_target_id is not None
                    and time_to_target == min_time
                    and v_id < best_target_id
                ):
                    min_time = time_to_target
                    best_target_id = v_id

        return best_target_id, predecessors

    def _find_next_action_to_kit(self,start_id=None,vertex_masking={}):
        if start_id is None:
            start_id = self.vertex_id


        best_target_id, predecessors = self._shortest_path_for_location_of_kit(start_id,vertex_masking)

        if best_target_id is not None:
            if best_target_id != start_id:
                next_node = self._get_next_traverse_node(
                    predecessors, start_id, best_target_id
                )
                if next_node is not None:
                    return (Action.TRAVERSE, next_node)

        return (Action.NO_OP, None)

    def _find_next_action_to_run_away(self):
        other_agent_locs = self.get_list_of_other_agent_ids()

        if not other_agent_locs:
            return (Action.NO_OP, None)

        best_score = (-float("inf"), -float("inf"), -float("inf"))
        best_neighbor = None

        neighbors = self.environment.edges.get(self.vertex_id, {})

        for neighbor_id in neighbors:
            move_cost = self.get_traverse_cost(
                self.vertex_id, neighbor_id, self.is_equipped
            )
            if move_cost is None or move_cost == float("inf"):
                continue

            dists_from_neighbor, _ = self._shortest_path(neighbor_id)

            min_time_to_any_agent = float("inf")
            for agent_loc in other_agent_locs:
                dist = dists_from_neighbor.get(agent_loc, float("inf"))
                if dist < min_time_to_any_agent:
                    min_time_to_any_agent = dist

            current_score = (min_time_to_any_agent, -move_cost, -neighbor_id)

            if current_score > best_score:
                best_score = current_score
                best_neighbor = neighbor_id

        if best_neighbor is not None:
            return (Action.TRAVERSE, best_neighbor)

        return (Action.NO_OP, None)

    def decide_action(self, **kwargs):
        if not self.is_equipped:
            if self.environment.vertices[self.vertex_id].amphibian_kits > 0:
                return (Action.EQUIP, None)

            return self._find_next_action_to_kit()
        else:
            return self._find_next_action_to_run_away()

    def get_path_to_kit(self, start_id=None, vertex_masking={}):
        if start_id is None:
            start_id = self.vertex_id

        target_id, predecessors = self._shortest_path_for_location_of_kit(start_id, vertex_masking)

        if target_id is None:
            return []

        action_path = []

        if target_id != start_id:
            node_path = []
            curr = target_id
            while curr != start_id:
                node_path.append(curr)
                curr = predecessors.get(curr)
                if curr is None:
                    return []
            
            node_path.reverse()
            for node_id in node_path:
                action_path.append((Action.TRAVERSE, node_id))

        action_path.append((Action.EQUIP, None))

        return action_path
class StupidGreedyAgent(Agent):
    def _shortest_path_for_location_of_people_to_be_rescued(self):
        start_id = self.vertex_id
        distances, predecessors = self._shortest_path(start_id)

        min_time = float("inf")
        best_target_id = None

        for v_id, vertex in self.environment.vertices.items():
            if vertex.people_to_rescue > 0:

                time_to_target = distances.get(v_id, float("inf"))

                if time_to_target < min_time:
                    min_time = time_to_target
                    best_target_id = v_id

                elif (
                    best_target_id is not None
                    and time_to_target == min_time
                    and v_id < best_target_id
                ):
                    min_time = time_to_target
                    best_target_id = v_id

        return best_target_id, predecessors

    def decide_action(self, **kwargs):
        start_id = self.vertex_id

        best_target_id, predecessors = (
            self._shortest_path_for_location_of_people_to_be_rescued()
        )

        if best_target_id is not None:
            next_node = self._get_next_traverse_node(
                predecessors, start_id, best_target_id
            )

            if next_node is not None:
                return (Action.TRAVERSE, next_node)

        return (Action.TERMINATE, None)


class AIAgent(Agent):
    def __init__(
        self,
        agent_id,
        vertex_id,
        environment,
        game_settings,
        expansion_limit,
        priority_func=None,
        **kwargs,
    ):
        super().__init__(agent_id,vertex_id, environment, game_settings, **kwargs)
        self.num_of_expansions = 0
        self.planned_actions = []
        self.priority_func = priority_func
        self.expansion_limit = expansion_limit
        self.expansion_time = game_settings.expansion_time
        self.goal_reached = False
        self.bonus_enabled=game_settings.bonus_enabled


    def decide_action(self):
        if self.planned_actions:
            return self.planned_actions.pop(0)

        self.planned_actions = self._run_search()
        if self.planned_actions:
            return self.planned_actions.pop(0)
        else:
            return (Action.TERMINATE, None)
    def _get_initial_people_location(self):
        return frozenset(
            [
                vertex_id
                for vertex_id, vertex in self.environment.vertices.items()
                if vertex.people_to_rescue > 0 and vertex_id != self.vertex_id
            ]
        )
    def _run_search(self):
        initial_people_locs =self._get_initial_people_location()
        if self.bonus_enabled:
            for agent in self.environment.agents:
                if type(agent)==ThiefAgent:
                    self.thief_agent=agent

        
        amphibian_kits_locations={v_id: vertex.amphibian_kits for v_id, vertex in self.environment.vertices.items()}
        if self.bonus_enabled:
            thief_agent_loc=self.thief_agent.vertex_id
            thief_agent_done=sum(list(amphibian_kits_locations.values()))<=0
            thief_agent_path_to_kit=self.thief_agent.get_path_to_kit(self.thief_agent.vertex_id,amphibian_kits_locations)
            if len(thief_agent_path_to_kit)==1:
                thief_agent_target=self.thief_agent.vertex_id
            elif len(thief_agent_path_to_kit)>1:
                thief_agent_target=thief_agent_path_to_kit[:2][1]
            else:
                thief_agent_target=-1
                
        else:
            thief_agent_path_to_kit=[]
            thief_agent_done=True
            thief_agent_target=-1
            thief_agent_loc=-1
                
        start_node = self._create_search_node(
            self.vertex_id, self.is_equipped, initial_people_locs, [],thief_agent_path_to_kit,amphibian_kits_locations
            ,thief_agent_loc,thief_agent_done,thief_agent_target
        )

        counter = 0
        front = [self._create_front_entry(start_node, counter)]
        visited = set()

        while front:
            current, g_score = self._extract_from_front(front)

            if self._is_goal_state(current):
                return self._handle_goal_reached(current)

            if not self._should_continue_search(current):
                return self._handle_search_limit(current)

            state_signature = self._get_state_signature(current)
            if state_signature in visited:
                continue
            visited.add(state_signature)

            for successor, action_cost in self._generate_successors(current):
                counter += 1
                new_g = g_score + action_cost
                self._add_to_front(front, successor, counter, new_g)

        return None

    def _create_search_node(
        self, vertex_id, is_equipped, remaining_people, actions,
        thief_agent_path_to_kit=[],
        amphibian_kits_locations={},thief_agent_location=-1,thief_agent_done=True,thief_agent_target=-1
    ):
        return {
            "vertex_id": vertex_id,
            "is_equipped": is_equipped,
            "remaining_people": remaining_people,
            "actions": actions,
            "thief_agent_path_to_kit":thief_agent_path_to_kit,
            "amphibian_kits_locations":amphibian_kits_locations,
            "thief_agent_location":thief_agent_location,
            "thief_agent_done":thief_agent_done,
            "thief_agent_target":thief_agent_target
        }

    def _get_state_signature(self, node):
        if self.bonus_enabled:
            kits_signature = frozenset(node["amphibian_kits_locations"].items())
            thief_loc = node["thief_agent_location"]
            return (node["vertex_id"], node["is_equipped"], node["remaining_people"], kits_signature, thief_loc)
        
        return (node["vertex_id"], node["is_equipped"], node["remaining_people"])

    def _is_goal_state(self, node):
        return not node["remaining_people"]

    def _handle_goal_reached(self, node):
        self.goal_reached = True
        return node["actions"]

    def _handle_search_limit(self, node):
        return node["actions"] + [(Action.TERMINATE, None)]

    def _should_continue_search(self, node):
        return self.num_of_expansions < self.game_settings.expansion_limit
    def _generate_successors(self, current):
        successors = []
        curr_vertex = current["vertex_id"]
        curr_is_equipped = current["is_equipped"]
        curr_remaining_people = current["remaining_people"]
        
        amphibian_kits_locations = current["amphibian_kits_locations"]
        thief_agent_path_to_kit = current["thief_agent_path_to_kit"]
        thief_agent_location = current["thief_agent_location"]
        thief_agent_done = current["thief_agent_done"]
        thief_agent_target = current["thief_agent_target"]
        curr_actions = current["actions"]
        def simulate_thief_step(current_kits_locs, current_path, current_loc, current_done, current_tgt):
            new_kits = current_kits_locs.copy()
            new_path = list(current_path)
            new_loc = current_loc
            new_done = current_done
            new_tgt = current_tgt
            if self.bonus_enabled and not new_done and new_path:
                action_type, action_node = new_path[0]
                if action_type == Action.TRAVERSE:
                    new_loc = action_node
                    new_path.pop(0)
                
                elif action_type == Action.EQUIP:
                    if new_kits.get(new_loc, 0) > 0:
                        new_kits[new_loc] -= 1
                        new_done = True
                        new_path = []
                        new_tgt = -1
                    else:
                        new_path = self.thief_agent.get_path_to_kit(new_loc, new_kits)
                        if new_path:
                            if len(new_path) == 1:
                                new_tgt = new_loc
                            else:
                                new_tgt = new_path[-2][1] if new_path[-1][0] == Action.EQUIP else -1
                        else:
                            new_tgt = -1
            
            return new_kits, new_path, new_loc, new_done, new_tgt

        if not curr_is_equipped and amphibian_kits_locations.get(curr_vertex, 0) > 0:
            
            
            if thief_agent_done:
                amphibian_kits_locations_new = amphibian_kits_locations.copy()
                amphibian_kits_locations_new[curr_vertex] = max(0, amphibian_kits_locations_new[curr_vertex] - 1)
                
                new_node = self._create_search_node(
                    curr_vertex, True, curr_remaining_people, curr_actions + [(Action.EQUIP, None)],
                    thief_agent_path_to_kit,
                    amphibian_kits_locations_new, thief_agent_location, thief_agent_done, thief_agent_target
                )
                successors.append((new_node, self.game_settings.equip_time_unit))

            elif thief_agent_target != curr_vertex: 
                amphibian_kits_locations_new = amphibian_kits_locations.copy()
                amphibian_kits_locations_new[curr_vertex] = max(0, amphibian_kits_locations_new[curr_vertex] - 1)
                n_kits, n_path, n_loc, n_done, n_tgt = simulate_thief_step(
                    amphibian_kits_locations_new, thief_agent_path_to_kit, thief_agent_location, thief_agent_done, thief_agent_target
                )

                new_node = self._create_search_node(
                    curr_vertex, True, curr_remaining_people, curr_actions + [(Action.EQUIP, None)],
                    n_path, n_kits, n_loc, n_done, n_tgt
                )
                successors.append((new_node, self.game_settings.equip_time_unit))

            elif thief_agent_target == curr_vertex:
                
                if thief_agent_location == thief_agent_target and thief_agent_path_to_kit and thief_agent_path_to_kit[0][0] == Action.EQUIP:
                    if self.thief_agent.agent_id < self.agent_id:
                        pass 
                    else:
                        amphibian_kits_locations_new = amphibian_kits_locations.copy()
                        amphibian_kits_locations_new[curr_vertex] = max(0, amphibian_kits_locations_new[curr_vertex] - 1)

                        new_thief_path = self.thief_agent.get_path_to_kit(thief_agent_location, amphibian_kits_locations_new)
                        
                        new_tgt = -1
                        if new_thief_path:
                            if len(new_thief_path) == 1:
                                new_tgt = thief_agent_location
                            else:
                                if new_thief_path[-1][0] == Action.EQUIP:
                                    new_tgt = new_thief_path[-2][1]
                                else:
                                    new_tgt = -1

                        new_node = self._create_search_node(
                            curr_vertex, True, curr_remaining_people, curr_actions + [(Action.EQUIP, None)],
                            new_thief_path, amphibian_kits_locations_new, thief_agent_location, thief_agent_done, new_tgt
                        )
                        successors.append((new_node, self.game_settings.equip_time_unit))

                else:
                    amphibian_kits_locations_new = amphibian_kits_locations.copy()
                    amphibian_kits_locations_new[curr_vertex] = max(0, amphibian_kits_locations_new[curr_vertex] - 1)

                    n_kits, n_path, n_loc, n_done, n_tgt = simulate_thief_step(
                        amphibian_kits_locations_new, thief_agent_path_to_kit, thief_agent_location, thief_agent_done, thief_agent_target
                    )
                    
                    if amphibian_kits_locations_new[curr_vertex] == 0:
                        n_path = self.thief_agent.get_path_to_kit(n_loc, n_kits)
                        if n_path:
                             if len(n_path) == 1: 
                                 n_tgt = n_loc
                             else: 
                                if n_path[-1][0] == Action.EQUIP :
                                    n_tgt = n_path[-2][1]
                                else:
                                    n_tgt = -1
                        else:
                            n_tgt = -1

                    new_node = self._create_search_node(
                        curr_vertex, True, curr_remaining_people, curr_actions + [(Action.EQUIP, None)],
                        n_path, n_kits, n_loc, n_done, n_tgt
                    )
                    successors.append((new_node, self.game_settings.equip_time_unit))

        if curr_is_equipped:
            amphibian_kits_locations_new = amphibian_kits_locations.copy()
            amphibian_kits_locations_new[curr_vertex] = amphibian_kits_locations_new.get(curr_vertex, 0) + 1

            n_kits, n_path, n_loc, n_done, n_tgt = simulate_thief_step(
                amphibian_kits_locations_new, thief_agent_path_to_kit, thief_agent_location, thief_agent_done, thief_agent_target
            )

            new_node = self._create_search_node(
                curr_vertex, False, curr_remaining_people, curr_actions + [(Action.UNEQUIP, None)],
                n_path, n_kits, n_loc, n_done, n_tgt
            )
            successors.append((new_node, self.game_settings.unequip_time_unit))

        neighbors = self.environment.edges.get(curr_vertex, {})
        for neighbor_id, _ in neighbors.items():
            cost = self.get_traverse_cost(curr_vertex, neighbor_id, curr_is_equipped)

            if cost in [float("inf"), None]:
                continue
            
            if neighbor_id in curr_remaining_people:
                new_remaining_people = curr_remaining_people - {neighbor_id}
            else:
                new_remaining_people = curr_remaining_people

            n_kits, n_path, n_loc, n_done, n_tgt = simulate_thief_step(
                amphibian_kits_locations, thief_agent_path_to_kit, thief_agent_location, thief_agent_done, thief_agent_target
            )
            

            new_node = self._create_search_node(
                neighbor_id,
                curr_is_equipped,
                new_remaining_people,
                curr_actions + [(Action.TRAVERSE, neighbor_id)],
                n_path, n_kits, n_loc, n_done, n_tgt
            )
            successors.append((new_node, cost))

        return successors

    def _add_to_front(self, front, node, counter, g_score):
        if self.num_of_expansions >= self.game_settings.expansion_limit:
            return

        priority = self._calculate_priority(node, g_score)
        entry = self._create_front_entry(node, counter, priority, g_score)
        heapq.heappush(front, entry)
        self.num_of_expansions += 1
        self.time_passed += self.expansion_time

    def _calculate_priority(self, node, g_score):
        raise NotImplementedError

    def _create_front_entry(self, node, counter, priority=None, g_score=0):
        raise NotImplementedError

    def _extract_from_front(self, front):
        raise NotImplementedError

    def _heuristic(self, current_pos, is_equipped, remaining_people_locs):
        if not remaining_people_locs:
            return 0
        people_list = list(remaining_people_locs)
        return self._calculate_mst_cost(current_pos, people_list, is_equipped)

    def _calculate_mst_cost(self, current_pos, remaining_people_locs, is_equipped):
        nodes_to_cover = [current_pos] + remaining_people_locs
        if not remaining_people_locs:
            return 0.0

        dist_matrix = self._calculate_pairwise_distances(nodes_to_cover, is_equipped)
        mst_cost = 0.0
        visited = set()
        heap = [(0.0, current_pos)]

        while heap and len(visited) < len(nodes_to_cover):
            cost, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            mst_cost += cost

            for v in nodes_to_cover:
                if v not in visited:
                    weight = dist_matrix[u].get(v, float("inf"))
                    if weight != float("inf"):
                        heapq.heappush(heap, (weight, v))

        if len(visited) != len(nodes_to_cover):
            return float("inf")
        else:
            return mst_cost

    def _calculate_pairwise_distances(self, nodes_of_interest, is_equipped):
        pairwise_dists = {u: {} for u in nodes_of_interest}

        for start_node in nodes_of_interest:
            distances = {v: float("inf") for v in self.environment.vertices}
            distances[start_node] = 0
            heap = [(0, start_node)]

            while heap:
                d, u = heapq.heappop(heap)
                if d > distances[u]:
                    continue

                if u in self.environment.edges:
                    for v in self.environment.edges[u]:
                        weight = self._get_edge_weight(u, v, is_equipped)
                        if weight != float("inf"):
                            if distances[u] + weight < distances[v]:
                                distances[v] = distances[u] + weight
                                heapq.heappush(heap, (distances[v], v))

            for target_node in nodes_of_interest:
                pairwise_dists[start_node][target_node] = distances[target_node]

        return pairwise_dists

    def _get_edge_weight(self, vertex_u, vertex_v, is_equipped):
        if vertex_u == vertex_v:
            return 0.0
        edge = self.environment.edges.get(vertex_u, {}).get(vertex_v)
        if not edge:
            return float("inf")

        w = edge.weight
        p = self.game_settings.amphibian_penalty_factor
        equip_time = self.game_settings.equip_time_unit
        unequip_time = self.game_settings.unequip_time_unit

        if edge.is_flooded:
            if not is_equipped:
                return (w * p) + equip_time
            else:
                return w * p
        else:
            if not is_equipped:
                return w
            
            return min(w * p, w + unequip_time)


class GreedySearchAgent(AIAgent):
    def __init__(self,agent_id,vertex_id, environment, game_settings, **kwargs):
        super().__init__(
            agent_id=agent_id,
            vertex_id=vertex_id,
            environment=environment,
            game_settings=game_settings,
            expansion_limit=1,
            **kwargs,
        )

    def _calculate_priority(self, node, g_score):
        return self._heuristic(
            node["vertex_id"], node["is_equipped"], node["remaining_people"]
        )

    def _create_front_entry(self, node, counter, priority=None, g_score=0):
        if priority is None:
            priority = self._calculate_priority(node, g_score)
        return (priority, counter, node, g_score)

    def _extract_from_front(self, front):
        _, _, node, g = heapq.heappop(front)
        return node, g


class AStarAgent(AIAgent):
    def __init__(self, agent_id,vertex_id, environment, game_settings, **kwargs):
        super().__init__(
            agent_id=agent_id,
            vertex_id=vertex_id,
            environment=environment,
            game_settings=game_settings,
            expansion_limit=LIMIT,
            **kwargs,
        )

    def _calculate_priority(self, node, g_score):
        h = self._heuristic(
            node["vertex_id"], node["is_equipped"], node["remaining_people"]
        )
        return g_score + h

    def _create_front_entry(self, node, counter, priority=None, g_score=0):
        if priority is None:
            priority = self._calculate_priority(node, g_score)
        h = priority - g_score
        return (priority, h, g_score, counter, node, g_score)

    def _extract_from_front(self, front):
        _, _, _, _, node, g = heapq.heappop(front)
        return node, g


class AStarRealTimeAgent(AIAgent):
    def __init__(self,agent_id, vertex_id, environment, game_settings, **kwargs):
        super().__init__(
            agent_id=agent_id,
            
            vertex_id=vertex_id,
            environment=environment,
            game_settings=game_settings,
            expansion_limit=game_settings.expansion_limit,
            **kwargs,
        )

    def decide_action(self):
        if self.goal_reached and self.planned_actions:
            return self.planned_actions.pop(0)
        if self.goal_reached:
            return (Action.TERMINATE, None)

        self.num_of_expansions = 0
        self.planned_actions = self._run_search()

        if self.planned_actions:
            return self.planned_actions.pop(0)
        return (Action.TERMINATE, None)

    def _should_continue_search(self, node):
        return self.num_of_expansions < self.expansion_limit

    def _handle_search_limit(self, node):
        return node["actions"]

    def _calculate_priority(self, node, g_score):
        h = self._heuristic(
            node["vertex_id"], node["is_equipped"], node["remaining_people"]
        )
        return g_score + h

    def _create_front_entry(self, node, counter, priority=None, g_score=0):
        if priority is None:
            priority = self._calculate_priority(node, g_score)
        h = priority - g_score
        return (priority, h, g_score, counter, node, g_score)

    def _extract_from_front(self, front):
        _, _, _, _, node, g = heapq.heappop(front)
        return node, g


AGENTS_FACTORY = {
    "human": HumanAgent,
    "thief": ThiefAgent,
    "stupidgreedy": StupidGreedyAgent,
    "greedysearch": GreedySearchAgent,
    "astar": AStarAgent,
    "astar_rt": AStarRealTimeAgent,
}
