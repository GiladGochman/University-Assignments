import json
from action import Action
from agents import AGENTS_FACTORY
from environment import Environment
from graph import Edge, Node
import argparse
from pathlib import Path
import os

BENCHMARK_CASES = [
    "test_astar_rt_t0_000001",
    "test_astar_rt_t0",
    "test_astar_t0_01",
    "test_greedy_t0_000001",
    "test_greedy_t0",
    "test_astar_rt_t0_01",
    "test_astar_t0_000001",
    "test_astar_t0",
    "test_greedy_t0_01",
]


class GameSettings:

    def __init__(
        self,
        number_of_vertices,
        unequip_time_unit,
        equip_time_unit,
        amphibian_penalty_factor,
        expansion_time=0,
        expansion_limit=10000,
        limited_search_limit=10,
        maximum_duration=1000,
        bonus_enabled=False,
    ):
        self.number_of_vertices = number_of_vertices
        self.unequip_time_unit = unequip_time_unit
        self.equip_time_unit = equip_time_unit
        self.amphibian_penalty_factor = amphibian_penalty_factor
        self.expansion_time = expansion_time
        self.expansion_limit = expansion_limit
        self.limited_search_limit = limited_search_limit
        self.maximum_duration = maximum_duration
        self.bonus_enabled = bonus_enabled
    @staticmethod
    def from_dict(d):
        return GameSettings(**d)

class Simulation:
    def __init__(self, config_name, config_dict):
        self.config_name = config_name
        self.config_dict = config_dict
        self.description = self.config_dict.get("description", "N/A")
        self.load_game_settings(self.config_dict["general_settings"])
        self.environment = Environment()
        self.load_vertices(self.config_dict["vertices"])
        self.load_edges(self.config_dict["edges"])
        self.load_agents(self.config_dict["agents"])

        self.duration = 0

    def load_game_settings(self, settings_config):
        number_of_vertices = settings_config["number_of_vertices"]
        unequip_time_unit = settings_config["unequip_time_unit"]
        equip_time_unit = settings_config["equip_time_unit"]
        amphibian_penalty_factor = settings_config["amphibian_penalty_factor"]
        expansion_time = settings_config.get("expansion_time")
        expansion_limit = settings_config.get("expansion_limit")
        self.game_settings = GameSettings.from_dict(settings_config
        )

    def load_agents(self, agent_configs):
        for agent_id,agent in enumerate(agent_configs):
            agent_type = agent["type"]
            vertex_id = agent["vertex"]
            agent_obj = AGENTS_FACTORY[agent_type](agent_id,
                vertex_id, self.environment, self.game_settings
            )
            self.environment.agents.append(agent_obj)

    def load_vertices(self, vertex_configs):
        for vertex in vertex_configs:
            node_id = vertex["id"]
            amphibian_kits = vertex.get("amphibian_kits", 0)
            people_to_rescue = vertex.get("people_to_rescue", 0)
            self.environment.vertices[node_id] = Node(
                node_id, amphibian_kits, people_to_rescue
            )

    def load_edges(self, edge_configs):
        for edge in edge_configs:
            edge_id = edge["id"]
            vertex_a = int(edge["vertex_a"])
            vertex_b = int(edge["vertex_b"])
            weight = edge["weight"]
            is_flooded = edge["is_flooded"]

            self.environment.edges[vertex_a] = self.environment.edges.get(vertex_a, {})
            self.environment.edges[vertex_a][vertex_b] = Edge(
                edge_id, vertex_a, vertex_b, weight, is_flooded
            )

            self.environment.edges[vertex_b] = self.environment.edges.get(vertex_b, {})
            self.environment.edges[vertex_b][vertex_a] = Edge(
                edge_id, vertex_b, vertex_a, weight, is_flooded
            )

    def step(self):
        for agent in self.environment.agents:
            if not agent.is_terminated:
                action, target = agent.decide_action()
                if action == Action.TRAVERSE:
                    agent.traverse(target)
                elif action == Action.EQUIP:
                    agent.equip()
                elif action == Action.UNEQUIP:
                    agent.unequip()
                elif action == Action.NO_OP:
                    agent.noop()
                elif action == Action.TERMINATE:
                    agent.terminate()
                else:
                    raise ValueError(f"Unknown action: {action}")

    def should_terminate_simulation(self):
        """Check if simulation should end"""
        all_terminated = all(agent.is_terminated for agent in self.environment.agents)

        all_rescued = self.environment.total_people_remaining() == 0
        duration_upper_limit = (
            self.duration >= self.game_settings.maximum_duration
        )
        return all_terminated or all_rescued or duration_upper_limit

    def run_simulation(self):
        while not self.should_terminate_simulation():
            self.display()
            self.step()
            self.duration += 1

        self.display()
        print("\n=== SIMULATION ENDED ===")
        print(
            f"Total people rescued: {sum(agent.people_saved for agent in self.environment.agents)}"
        )
        print(f"People remaining: {self.environment.total_people_remaining()}")
        print("\n=== AGENT PERFORMANCE ===")
        print(f"[stats] Case name:{self.config_name}")
        for i, agent in enumerate(self.environment.agents):
            print(f"[stats]  Agent {i+1} ({agent.__class__.__name__}):")
            print(f"[stats]  People saved: {agent.people_saved}")
            print(f"[stats]  Real world  taken: {agent.time_passed}")
            print(f"[stats]  Time taken: {agent.time_taken}")
            print(f"[stats]  Score: {agent.score}")

    def display(self):
        print("############################################################")
        print("###  GLOBAL SIMULATION STATS:")
        print(f"###  Running: {self.description}")
        print(f"Number of nodes: {self.game_settings.number_of_vertices}")
        print(
            f"Unequip time unit: {self.game_settings.unequip_time_unit}"
        )  # Fixed typo
        print(f"Equip time unit: {self.game_settings.equip_time_unit}")  # Fixed typo
        print(
            f"Amphibian penalty factor: {self.game_settings.amphibian_penalty_factor}"
        )  # Fixed typo
        print(f"Duration: {self.duration}")
        print(f"Total agents: {len(self.environment.agents)}")
        print(
            f"People remaining to rescue: {self.environment.total_people_remaining()}"
        )
        print("###  AGENTS STATS:")
        for i, agent in enumerate(self.environment.agents):
            print(f"--- Agent {i+1} ---")
            print(f"Type: {agent.__class__.__name__}")
            print(f"Current vertex: {agent.vertex_id}")
            print(f"Equipped: {agent.is_equipped}")
            print(f"Terminated: {agent.is_terminated}")
            print(f"People saved: {agent.people_saved}")
            print(f"Time taken: {agent.time_taken}")
            print(f"Actions count: {agent.actions_count}")
            print(f"Final Score: {agent.score}")


def load_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


def get_all_config_options():
    options = {}
    for f in os.listdir("configs"):
        name = f.replace(".json", "")
        options[name] = load_json(f"configs/{f}")
    return options


if __name__ == "__main__":
    options = get_all_config_options()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all available configuration options and exit",
    )
    parser.add_argument(
        "-b",
        "--benchmark",
        action="store_true",
        help="Evaluate diffrent configs for T",
    )
    parser.add_argument(
        "config_name",
        nargs="?",
        default="default",
        # choices=options.keys(),
        help="The configuration file to run (default: default)",
    )
    # parser.add_argument("path")
    args = parser.parse_args()
    largest_name = max([len(name) for name in options])
    if args.benchmark:
        for benchmark_case in BENCHMARK_CASES:
            sim = Simulation(benchmark_case, options[benchmark_case])
            sim.run_simulation()
    elif args.list:
        print("")
        for option_name, option_content in options.items():
            option_description = option_content.get("description", "N/A")
            pad_size = largest_name - len(option_name)
            option_name = option_name + " " * pad_size
            print(f"{option_name}   # {option_description}")
    elif args.config_name not in list(options):
        raise Exception("Invalid option was provided.Run -l to see options next time")
    else:
        sim = Simulation(args.config_name, options[args.config_name])
        sim.run_simulation()
