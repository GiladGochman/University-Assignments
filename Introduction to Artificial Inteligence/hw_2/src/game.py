"""Game class for Hurricane Evacuation simulation."""

from typing import Any, Dict

from graph import Graph
from state import State
from agents import AIGameAgent
from models import VertexLocation


class Game:
    """Main game controller for Hurricane Evacuation simulation."""

    def __init__(
        self,
        deadline: float,
        params: Dict[str, int],
        vertices_config: Dict[str, dict],
        edges_config: Dict[str, tuple],
        agents_config: Dict[Any, Any],
        tactic: str,
        cutoff: int = 10,
        alpha_beta: bool = True,
    ):

        self.deadline = deadline
        self.unequip_time = params.get("unequip_time", 1)
        self.equip_time = params.get("equip_time", 1)
        self.kit_penalty = params.get("flood_penalty", 1)

        self.graph = Graph.from_config(vertices_config, edges_config)

        for agent_id, v_id in agents_config.items():
            self.graph.get_vertices()[v_id].init += " Agent_" + str(agent_id)

        init_people = {
            v_id: v.n_people
            for v_id, v in self.graph.get_vertices().items()
            if v.n_people > 0
        }

        init_saved = {agent_id: 0 for agent_id in agents_config.keys()}

        for agent_id, v_id in agents_config.items():
            if v_id in init_people and init_people[v_id] > 0:
                init_saved[agent_id] += init_people[v_id]
                init_people[v_id] = 0

        init_kits_on_vertices = {
            v_id: frozenset(cfg["kits"])
            for v_id, cfg in vertices_config.items()
            if cfg["kits"]
        }

        init_kits_held = {agent_id: None for agent_id in agents_config.keys()}

        init_locations = {
            agent_id: VertexLocation(v_id) for agent_id, v_id in agents_config.items()
        }

        self.current_state = State(
            self,
            init_locations,
            init_saved,
            init_people,
            init_kits_on_vertices,
            init_kits_held,
            0,
        )

        self.agents = {
            agent_id: AIGameAgent(agent_id, self)
            for agent_id, _ in agents_config.items()
        }

        self.time = 0
        self.cutoff = cutoff
        self.tactic = tactic
        self.alpha_beta = alpha_beta
        self.visited_states = {self.current_state}

    def run_game(self):
        """Run the game simulation until completion."""
        while (
            self.time < self.deadline
            and self.current_state.any_people_left()
            and len(self.agents) > 0
        ):
            print("-" * 20 + f"t = {self.time} -> {self.time + 1}" + "-" * 20)

            agent_ids = sorted(self.agents.keys())
            current_agent = self.agents[agent_ids[self.time % len(agent_ids)]]

            print(f"Currently saved: {self.current_state.saved}")
            print(f"Current people: {self.current_state.people}")
            print(f"Kits at vertices: {self.current_state.kits_on_vertices}")
            print(f"Agents holding kits: {self.current_state.kits_held}")
            print(f"Agent {current_agent.agent_id} at {self.current_state.locations[current_agent.agent_id]}")

            action_taken = current_agent.act(self.alpha_beta)
            print(f"Action: {action_taken}")

            self.time += 1

            if self.current_state in self.visited_states:
                print("State revisited - game ends!")
                break
            self.visited_states.add(self.current_state)

        print("=" * 60)
        print(f"Final people situation: {self.current_state.people}")
        print(f"People saved: {self.current_state.saved}")

        if len(self.agents) == 2:
            agent_ids = sorted(self.agents.keys())
            a1, a2 = agent_ids[0], agent_ids[1]
            if self.current_state.saved[a1] > self.current_state.saved[a2]:
                print(f"\nThe winner is {a1}")
            elif self.current_state.saved[a2] > self.current_state.saved[a1]:
                print(f"\nThe winner is {a2}")
            else:
                print("\nThere is a tie")

        print(f"States created: {State.states_created}")
