"""Game state management for Hurricane Evacuation problem."""

import heapq
from typing import Any, Dict, List, Tuple

from models import (
    AgentLocation,
    VertexLocation,
    EdgeLocation,
    EquippingLocation,
    UnequippingLocation,
)
from graph import Edge


class State:
    """Represents a game state including agent locations, saved people, etc."""

    states_created = 0

    def __init__(
        self,
        game,
        locations: Dict[str, AgentLocation],
        saved: Dict[str, int],
        people: Dict[Any, int],
        kits_on_vertices: Dict[str, frozenset],
        kits_held: Dict[str, Any],
        time: int,
    ):
        self.game = game
        self.locations = locations
        self.saved = saved
        self.people = people
        self.kits_on_vertices = kits_on_vertices
        self.kits_held = kits_held
        self.time = time
        State.states_created += 1

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        agent_ids = sorted(self.game.agents.keys())
        current_turn = (
            agent_ids[self.time % len(agent_ids)] if len(agent_ids) > 0 else "A"
        )
        other_turn = (
            agent_ids[other.time % len(agent_ids)] if len(agent_ids) > 0 else "A"
        )

        return (
        self.locations == other.locations
        and self.people == other.people
        and self.saved == other.saved 
        and self.kits_on_vertices == other.kits_on_vertices
        and self.kits_held == other.kits_held
        and current_turn == other_turn
    )

    def __hash__(self):
        agent_ids = sorted(self.game.agents.keys())
        current_turn = (
            agent_ids[self.time % len(agent_ids)] if len(agent_ids) > 0 else "A"
        )

        loc_tuple = tuple(sorted((k, v) for k, v in self.locations.items()))
        people_tuple = tuple(sorted(self.people.items()))
        kits_v_tuple = tuple(
            sorted((k, tuple(sorted(v))) for k, v in self.kits_on_vertices.items())
        )
        kits_h_tuple = tuple(sorted(self.kits_held.items()))
        saved_tuple = tuple(sorted(self.saved.items()))
        return hash((loc_tuple, saved_tuple, people_tuple, kits_v_tuple, kits_h_tuple, current_turn))

    def get_heuristic_value(self, agent_id):
        """
        Heuristic: (saved[agent] - saved[opponent]) + (mst_diff).
        """
        all_agents = list(self.saved.keys())
        other = [aid for aid in all_agents if aid != agent_id][0]

        saved_diff = self.saved[agent_id] - self.saved[other]
        remaining_people_vertices = [v_id for v_id, n in self.people.items() if n > 0]

        mst_diff = 0
        mst_agent = 0
        mst_other = 0

        if len(remaining_people_vertices) > 0:
            mst_agent = self._calculate_agent_mst(
                self.locations[agent_id], remaining_people_vertices
            )
            mst_other = self._calculate_agent_mst(
                self.locations[other], remaining_people_vertices
            )

            mst_diff = mst_other - mst_agent
        min_mst = min(mst_agent, mst_other)
        weighted_mst_diff = mst_diff / 100.0
        weighted_min_mst = min_mst / 100.0

        if self.game.tactic == "Adversarial":
            return saved_diff + mst_diff
        elif self.game.tactic == "Fully Cooperative":
            total_saved = self.saved[agent_id] + self.saved[other]
            return total_saved - weighted_min_mst
        elif self.game.tactic == "Semi Cooperative":
            return (self.saved[agent_id] + weighted_mst_diff, self.saved[other])

        return self.saved[agent_id]

    def _calculate_agent_mst(
        self, location: AgentLocation, remaining_people: List[str]
    ) -> int:
        """
        Helper to calculate MST from a generic location (Vertex, Edge, or Action).
        If on an edge, assumes completion of current move + MST from destination.
        """
        start_node = None
        extra_cost = 0

        if isinstance(location, VertexLocation):
            start_node = location.v_id
        elif isinstance(location, EdgeLocation):
            start_node = location.destination_v_id
            extra_cost = location.units
        elif isinstance(location, (EquippingLocation, UnequippingLocation)):
            start_node = location.v_id
            extra_cost = location.units

        if start_node:
            targets = [start_node] + remaining_people
            return self._compute_mst_for_vertices(targets) + extra_cost
        return 0

    def _compute_mst_for_vertices(self, vertex_ids: List[str]) -> int:
        """
        Compute MST cost using a dense graph of shortest paths (Dijkstra).
        Optimistic heuristic: Ignores flood penalties and kit restrictions.
        """
        if len(vertex_ids) <= 1:
            return 0

        distances = {}

        for start_node in vertex_ids:
            pq = [(0, start_node)]
            local_dists = {start_node: 0}
            visited = set()

            while pq:
                d, u_id = heapq.heappop(pq)

                if u_id in visited:
                    continue
                visited.add(u_id)

                if u_id in vertex_ids and u_id != start_node:
                    distances[(start_node, u_id)] = d
                    distances[(u_id, start_node)] = d  

                u = self.game.graph.get_vertices()[u_id]
                for e in u.edges.values():
                    v_node = e.get_other_vertex(u)
                    new_dist = d + e.w 
                    if new_dist < local_dists.get(v_node.v_id, float("inf")):
                        local_dists[v_node.v_id] = new_dist
                        heapq.heappush(pq, (new_dist, v_node.v_id))

        mst_cost = 0
        in_tree = {vertex_ids[0]}
        available_edges = []

        start = vertex_ids[0]
        for other in vertex_ids[1:]:
            if (start, other) in distances:
                heapq.heappush(available_edges, (distances[(start, other)], other))

        while len(in_tree) < len(vertex_ids) and available_edges:
            w, u = heapq.heappop(available_edges)
            if u in in_tree:
                continue

            in_tree.add(u)
            mst_cost += w

            for v in vertex_ids:
                if v not in in_tree and (u, v) in distances:
                    heapq.heappush(available_edges, (distances[(u, v)], v))

        return mst_cost

    def get_successor_states(self, agent_id) -> List[Tuple["State", str]]:
        successors = []
        location = self.locations[agent_id]

        if isinstance(location, EdgeLocation):
            if location.units == 1:
                new_state = self.get_vertex_state(agent_id, location.destination_v_id)
                successors.append(
                    (new_state, f"finish_traverse to {location.destination_v_id}")
                )
            else:
                new_state = self.continue_action(agent_id)
                successors.append(
                    (new_state, f"continue_traverse ({location.units - 1} left)")
                )
            return successors

        if isinstance(location, EquippingLocation):
            if location.units == 1:
                new_state = self.finish_equipping(agent_id)
                successors.append(
                    (new_state, f"finish_equip {location.kit_id} at {location.v_id}")
                )
            else:
                new_state = self.continue_action(agent_id)
                successors.append(
                    (
                        new_state,
                        f"continue_equip {location.kit_id} ({location.units - 1} left)",
                    )
                )
            return successors

        if isinstance(location, UnequippingLocation):
            if location.units == 1:
                new_state = self.finish_unequipping(
                    agent_id, location.v_id, location.kit_id
                )
                successors.append(
                    (new_state, f"finish_unequip {location.kit_id} at {location.v_id}")
                )
            else:
                new_state = self.continue_action(agent_id)
                successors.append(
                    (
                        new_state,
                        f"continue_unequip {location.kit_id} ({location.units - 1} left)",
                    )
                )
            return successors

        if isinstance(location, VertexLocation):
            v_id = location.v_id
            v = self.game.graph.get_vertices()[v_id]
            has_kit = self.kits_held[agent_id] is not None

            for e in v.edges.values():
                u = e.get_other_vertex(v)
                if not e.flooded or has_kit:
                    time_multiplier = (
                        self.game.kit_penalty if (e.flooded and has_kit) else 1
                    )
                    actual_weight = e.w * time_multiplier

                    if actual_weight == 1:
                        new_state = self.get_vertex_state(agent_id, u.v_id, 1)
                        successors.append((new_state, f"traverse to {u.v_id}"))
                    else:
                        new_state = self.get_traverse_state(
                            e, agent_id, v_id, u.v_id, actual_weight
                        )
                        successors.append((new_state, f"start_traverse to {u.v_id}"))

            available_kits = self.kits_on_vertices.get(v_id, frozenset())
            if available_kits and not has_kit:
                target_kit = min(available_kits)
                time_needed = self.game.equip_time
                if time_needed == 1:
                    new_state = self.finish_equipping_from_vertex(
                        agent_id, v_id, target_kit
                    )
                    successors.append((new_state, f"equip {target_kit} at {v_id}"))
                else:
                    new_state = self.start_equipping(
                        agent_id, v_id, time_needed, target_kit
                    )
                    successors.append(
                        (new_state, f"start_equip {target_kit} at {v_id}")
                    )

            if has_kit:
                kit_to_drop = self.kits_held[agent_id]
                time_needed = self.game.unequip_time
                if time_needed == 1:
                    new_state = self.finish_unequipping(agent_id, v_id, kit_to_drop)
                    successors.append((new_state, f"unequip {kit_to_drop} at {v_id}"))
                else:
                    new_state = self.start_unequipping(
                        agent_id, v_id, time_needed, kit_to_drop
                    )
                    successors.append(
                        (new_state, f"start_unequip {kit_to_drop} at {v_id}")
                    )

            new_state = self.get_noop_state(agent_id)
            successors.append((new_state, "no-op"))

        return successors

    def get_vertex_state(self, agent_id, destination_v_id, w: int = 1):
        current_locations = self.locations.copy()
        current_locations[agent_id] = VertexLocation(destination_v_id)
        currently_saved = self.saved.copy()
        current_people = self.people.copy()
        if destination_v_id in current_people and current_people[destination_v_id] > 0:
            currently_saved[agent_id] += current_people[destination_v_id]
            current_people[destination_v_id] = 0
        return State(
            self.game,
            current_locations,
            currently_saved,
            current_people,
            self.kits_on_vertices,
            self.kits_held,
            self.time + w,
        )

    def get_traverse_state(
        self, e: Edge, agent_id, origin_v_id, destination_v_id, total_weight
    ):
        current_locations = self.locations.copy()
        current_locations[agent_id] = EdgeLocation(
            e.e_id, origin_v_id, destination_v_id, total_weight - 1
        )
        return State(
            self.game,
            current_locations,
            self.saved,
            self.people,
            self.kits_on_vertices,
            self.kits_held,
            self.time + 1,
        )

    def start_equipping(self, agent_id, v_id, equip_time, kit_id):
        current_locations = self.locations.copy()
        current_locations[agent_id] = EquippingLocation(v_id, equip_time - 1, kit_id)
        new_vertex_kits = self.kits_on_vertices.copy()
        current_set = set(new_vertex_kits.get(v_id, []))
        current_set.remove(kit_id)
        new_vertex_kits[v_id] = frozenset(current_set)
        return State(
            self.game,
            current_locations,
            self.saved,
            self.people,
            new_vertex_kits,
            self.kits_held,
            self.time + 1,
        )

    def finish_equipping(self, agent_id):
        location = self.locations[agent_id]
        current_locations = self.locations.copy()
        current_locations[agent_id] = VertexLocation(location.v_id)
        new_held = self.kits_held.copy()
        new_held[agent_id] = location.kit_id
        return State(
            self.game,
            current_locations,
            self.saved,
            self.people,
            self.kits_on_vertices,
            new_held,
            self.time + 1,
        )

    def finish_equipping_from_vertex(self, agent_id, v_id, kit_id):
        new_held = self.kits_held.copy()
        new_held[agent_id] = kit_id
        new_vertex_kits = self.kits_on_vertices.copy()
        current_set = set(new_vertex_kits.get(v_id, []))
        current_set.remove(kit_id)
        new_vertex_kits[v_id] = frozenset(current_set)
        return State(
            self.game,
            self.locations.copy(),
            self.saved,
            self.people,
            new_vertex_kits,
            new_held,
            self.time + 1,
        )

    def start_unequipping(self, agent_id, v_id, unequip_time, kit_id):
        current_locations = self.locations.copy()
        current_locations[agent_id] = UnequippingLocation(
            v_id, unequip_time - 1, kit_id
        )
        return State(
            self.game,
            current_locations,
            self.saved,
            self.people,
            self.kits_on_vertices,
            self.kits_held,
            self.time + 1,
        )

    def finish_unequipping(self, agent_id, v_id, kit_id):
        new_held = self.kits_held.copy()
        new_held[agent_id] = None
        new_vertex_kits = self.kits_on_vertices.copy()
        current_set = set(new_vertex_kits.get(v_id, []))
        current_set.add(kit_id)
        new_vertex_kits[v_id] = frozenset(current_set)

        current_locations = self.locations.copy()
        current_locations[agent_id] = VertexLocation(v_id)

        return State(
            self.game,
            current_locations,
            self.saved,
            self.people,
            new_vertex_kits,
            new_held,
            self.time + 1,
        )

    def continue_action(self, agent_id):
        location = self.locations[agent_id]
        current_locations = self.locations.copy()
        if isinstance(location, EdgeLocation):
            current_locations[agent_id] = EdgeLocation(
                location.e_id,
                location.origin_v_id,
                location.destination_v_id,
                location.units - 1,
            )
        elif isinstance(location, EquippingLocation):
            current_locations[agent_id] = EquippingLocation(
                location.v_id, location.units - 1, location.kit_id
            )
        elif isinstance(location, UnequippingLocation):
            current_locations[agent_id] = UnequippingLocation(
                location.v_id, location.units - 1, location.kit_id
            )

        return State(
            self.game,
            current_locations,
            self.saved,
            self.people,
            self.kits_on_vertices,
            self.kits_held,
            self.time + 1,
        )

    def get_noop_state(self, agent_id):
        return State(
            self.game,
            self.locations.copy(),
            self.saved,
            self.people,
            self.kits_on_vertices,
            self.kits_held,
            self.time + 1,
        )

    def cutoff_test(self, d):
        return d >= self.game.cutoff or not self.any_people_left()

    def any_people_left(self):
        return any(self.people.values())
