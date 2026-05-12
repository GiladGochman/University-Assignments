import json
import argparse
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
import networkx as nx
from action import Action
from agents import AGENTS_FACTORY
from environment import Environment
from graph import Edge, Node
from pathlib import Path
import os
from collections import defaultdict

from main import GameSettings, Simulation


class VisualSimulation(Simulation):
    def __init__(self, config_dict):
        self.config_dict = config_dict
        self.description = self.config_dict.get("description", "N/A")
        self.load_game_settings(self.config_dict["general_settings"])
        self.environment = Environment()
        self.load_vertices(self.config_dict["vertices"])
        self.load_edges(self.config_dict["edges"])
        self.load_agents(self.config_dict["agents"])

        self.duration = 0

        # Visual tracking
        self.agent_paths = defaultdict(list)
        self.agent_actions = defaultdict(list)
        self.history = []

        # Capture initial state (Duration 0, index 0)
        self._record_current_state()

    def _create_networkx_graph(self):
        """Create a NetworkX graph for visualization"""
        G = nx.Graph()

        # Add nodes
        for node_id, node in self.environment.vertices.items():
            G.add_node(
                node_id,
                amphibian_kits=node.amphibian_kits,
                people=node.people_to_rescue,
            )

        # Add edges
        added_edges = set()
        for from_node in self.environment.edges:
            for to_node, edge in self.environment.edges[from_node].items():
                edge_tuple = tuple(sorted([from_node, to_node]))
                if edge_tuple not in added_edges:
                    G.add_edge(
                        from_node, to_node, weight=edge.weight, flooded=edge.is_flooded
                    )
                    added_edges.add(edge_tuple)

        return G

    def _record_current_state(self):
        """Records the current state for visualization history."""
        step_info = {"duration": self.duration, "agents": [], "vertices": {}}

        # Record vertex states
        for vertex_id, vertex in self.environment.vertices.items():
            step_info["vertices"][vertex_id] = {
                "people_to_rescue": vertex.people_to_rescue,
                "amphibian_kits": vertex.amphibian_kits,
            }

        for i, agent in enumerate(self.environment.agents):
            # Record agent state
            step_info["agents"].append(
                {
                    "id": i,
                    "vertex": agent.vertex_id,
                    "equipped": agent.is_equipped,
                    "terminated": agent.is_terminated,
                    "people_saved": agent.people_saved,
                    "time_taken": agent.time_taken,
                    "score": agent.score,
                }
            )

            # For Duration 0 only, ensure the path array starts with the initial vertex
            if self.duration == 0:
                self.agent_paths[i].append(agent.vertex_id)

        self.history.append(step_info)

    def step(self):
        """Execute one simulation step and record state"""

        for i, agent in enumerate(self.environment.agents):
            if not agent.is_terminated:
                prev_vertex = agent.vertex_id
                action, target = agent.decide_action()

                # Execute action
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

                # 1. Record action taken (before state recording)
                # FIX: action is a string constant (e.g., "traverse"), so remove .value
                action_str = f"{action}{f' V{target}' if action == Action.TRAVERSE and target is not None else ''}"
                self.agent_actions[i].append(action_str)

                # 2. Record vertex state for path length alignment
                self.agent_paths[i].append(agent.vertex_id)

        # 3. Record full final state for this step (Duration N+1)
        self.duration += 1
        self._record_current_state()


    def run_simulation(self, visualize=True, save_path=None):
        """Run the simulation with optional visualization"""
        print(f"\n=== STARTING SIMULATION: {self.description} ===\n")

        while not self.should_terminate_simulation():
            self.display()
            self.step()

        self.display()
        print("\n=== SIMULATION ENDED ===")
        print(
            f"Total people rescued: {sum(agent.people_saved for agent in self.environment.agents)}"
        )
        print(f"People remaining: {self.environment.total_people_remaining()}")

        self._print_path_summary()
        self._print_vertex_changes()

        if visualize:
            self.visualize_paths(save_path)

    def display(self):
        """Display current simulation state"""
        print("=" * 60)
        print(f"STEP {self.duration} | {self.description}")
        print(f"People remaining: {self.environment.total_people_remaining()}")
        for i, agent in enumerate(self.environment.agents):
            status = "✓" if agent.is_terminated else "→"
            equip = "🔧" if agent.is_equipped else "  "
            # Display score from the most recent agent state in history
            latest_score = (
                self.history[-1]["agents"][i]["score"] if self.history else agent.score
            )

            print(
                f"  {status} Agent {i+1} ({agent.__class__.__name__:15s}): "
                f"Node {agent.vertex_id:2d} {equip} | "
                f"Saved: {agent.people_saved:2d} | "
                f"Time: {agent.time_taken:6.1f} | "
                f"Score: {latest_score:6.0f}"
            )

    def _print_path_summary(self):
        """Print summary of paths taken by each agent"""
        print("\n" + "=" * 60)
        print("PATH SUMMARY")
        print("=" * 60)
        for i, agent in enumerate(self.environment.agents):
            path = self.agent_paths[i]
            print(f"\nAgent {i+1} ({agent.__class__.__name__}):")
            print(f"  Path: {' → '.join(map(str, path))}")
            print(f"  Length: {len(path)} nodes visited")
            print(f"  People saved: {agent.people_saved}")
            print(f"  Final score: {agent.score:.0f}")

    def _print_vertex_changes(self):
        """Print summary of vertex state changes during simulation"""
        print("\n" + "=" * 60)
        print("VERTEX CHANGES SUMMARY")
        print("=" * 60)

        # Get initial and final states
        initial_state = self.history[0]["vertices"]
        final_state = self.history[-1]["vertices"]

        print(
            "\nVertex ID | Initial People | Final People | People Rescued | Initial Kits | Final Kits | Kits Used"
        )
        print("-" * 95)

        for vertex_id in sorted(initial_state.keys()):
            initial = initial_state[vertex_id]
            final = final_state[vertex_id]

            people_rescued = initial["people_to_rescue"] - final["people_to_rescue"]
            kits_used = initial["amphibian_kits"] - final["amphibian_kits"]

            if people_rescued > 0 or kits_used > 0:
                print(
                    f"    {vertex_id:2d}    |      {initial['people_to_rescue']:2d}        |      {final['people_to_rescue']:2d}      |       {people_rescued:2d}       |      {initial['amphibian_kits']:2d}      |     {final['amphibian_kits']:2d}     |     {kits_used:2d}"
                )

    def visualize_paths(self, save_path=None):
        """Create a visualization of the graph and agent paths"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

        self.pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

        self._draw_graph_with_paths(ax1)
        self._draw_stats(ax2)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"\nVisualization saved to: {save_path}")

        plt.show()

    def _draw_graph_with_paths(self, ax):
        """Draw the graph with all agent paths"""
        ax.set_title(
            f"Agent Paths - {self.description}", fontsize=16, fontweight="bold"
        )
        ax.axis("off")

        for u, v, data in self.graph.edges(data=True):
            color = "blue" if data["flooded"] else "gray"
            style = "dashed" if data["flooded"] else "solid"
            width = 1 if data["flooded"] else 2
            nx.draw_networkx_edges(
                self.graph,
                self.pos,
                [(u, v)],
                edge_color=color,
                style=style,
                width=width,
                ax=ax,
            )

        node_colors = []
        node_sizes = []
        for node in self.graph.nodes():
            vertex = self.environment.vertices[node]
            if vertex.people_to_rescue > 0:
                node_colors.append("red")
                node_sizes.append(800)
            elif vertex.amphibian_kits > 0:
                node_colors.append("green")
                node_sizes.append(600)
            else:
                node_colors.append("lightgray")
                node_sizes.append(400)

        nx.draw_networkx_nodes(
            self.graph, self.pos, node_color=node_colors, node_size=node_sizes, ax=ax
        )
        nx.draw_networkx_labels(
            self.graph, self.pos, font_size=10, font_weight="bold", ax=ax
        )

        agent_colors = ["purple", "orange", "brown", "pink", "cyan"]
        for i, path in self.agent_paths.items():
            if len(path) > 1:
                color = agent_colors[i % len(agent_colors)]
                path_edges = [(path[j], path[j + 1]) for j in range(len(path) - 1)]

                for j, (u, v) in enumerate(path_edges):
                    alpha = 0.3 + 0.7 * (j / len(path_edges))
                    nx.draw_networkx_edges(
                        self.graph,
                        self.pos,
                        [(u, v)],
                        edge_color=color,
                        width=3,
                        alpha=alpha,
                        arrows=True,
                        arrowsize=20,
                        connectionstyle="arc3,rad=0.1",
                        ax=ax,
                    )

        legend_elements = [
            mpatches.Patch(color="red", label="People to rescue"),
            mpatches.Patch(color="green", label="Amphibian kits"),
            mpatches.Patch(color="blue", label="Flooded edge"),
            mpatches.Patch(color="gray", label="Normal edge"),
        ]
        for i in range(len(self.environment.agents)):
            color = agent_colors[i % len(agent_colors)]
            legend_elements.append(
                mpatches.Patch(color=color, label=f"Agent {i+1} path")
            )
        ax.legend(handles=legend_elements, loc="upper left", fontsize=10)

    def _draw_stats(self, ax):
        """Draw statistics panel"""
        ax.set_title("Simulation Statistics", fontsize=16, fontweight="bold")
        ax.axis("off")

        stats_text = f"""
SIMULATION: {self.description}

SETTINGS:
  • Nodes: {self.game_settings.number_of_vertices}
  • Equip time: {self.game_settings.equip_time_unit}
  • Unequip time: {self.game_settings.unequip_time_unit}
  • Amphibian penalty: {self.game_settings.amphibian_penalty_factor}x

RESULTS:
  • Duration: {self.duration} steps
  • Total agents: {len(self.environment.agents)}
  • People rescued: {sum(a.people_saved for a in self.environment.agents)}
  • People remaining: {self.environment.total_people_remaining()}

AGENT DETAILS:
"""

        for i, agent in enumerate(self.environment.agents):
            path_length = len(self.agent_paths[i])
            stats_text += f"""
Agent {i+1}: {agent.__class__.__name__}
  • Path length: {path_length} nodes
  • People saved: {agent.people_saved}
  • Time taken: {agent.time_taken:.1f}
  • Actions: {agent.actions_count}
  • Score: {agent.score:.0f}
"""

        ax.text(
            0.1,
            0.95,
            stats_text,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.3),
        )

    def create_animation(self, save_path=None):
        """Create an animated visualization of the simulation"""
        fig, ax = plt.subplots(figsize=(12, 10))

        self.pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

        def update(frame):
            ax.clear()
            ax.set_title(f"Step {frame} - {self.description}", fontsize=14)
            ax.axis("off")

            for u, v, data in self.graph.edges(data=True):
                color = "blue" if data["flooded"] else "gray"
                style = "dashed" if data["flooded"] else "solid"
                nx.draw_networkx_edges(
                    self.graph, self.pos, [(u, v)], edge_color=color, style=style, ax=ax
                )

            # Get vertex states for this frame
            if frame < len(self.history):
                vertex_states = self.history[frame]["vertices"]

                node_colors = []
                node_sizes = []
                for node in self.graph.nodes():
                    vertex_state = vertex_states[node]
                    if vertex_state["people_to_rescue"] > 0:
                        node_colors.append("red")
                        node_sizes.append(800)
                    elif vertex_state["amphibian_kits"] > 0:
                        node_colors.append("green")
                        node_sizes.append(600)
                    else:
                        node_colors.append("lightgray")
                        node_sizes.append(400)

                nx.draw_networkx_nodes(
                    self.graph,
                    self.pos,
                    node_color=node_colors,
                    node_size=node_sizes,
                    ax=ax,
                )
            else:
                nx.draw_networkx_nodes(
                    self.graph, self.pos, node_color="lightgray", node_size=500, ax=ax
                )

            nx.draw_networkx_labels(self.graph, self.pos, ax=ax)

            if frame < len(self.history):
                step_info = self.history[frame]
                agent_colors = ["purple", "orange", "brown", "pink", "cyan"]

                for agent_info in step_info["agents"]:
                    if not agent_info["terminated"]:
                        agent_id = agent_info["id"]
                        vertex = agent_info["vertex"]
                        color = agent_colors[agent_id % len(agent_colors)]

                        pos_x, pos_y = self.pos[vertex]
                        offset = 0.1 * (agent_id - len(step_info["agents"]) / 2)
                        ax.scatter(
                            pos_x + offset,
                            pos_y,
                            s=200,
                            c=color,
                            marker="o",
                            edgecolors="black",
                            linewidths=2,
                            zorder=10,
                        )

        anim = FuncAnimation(
            fig, update, frames=len(self.history), interval=500, repeat=True
        )

        if save_path:
            anim.save(save_path, writer="pillow", fps=2)
            print(f"\nAnimation saved to: {save_path}")

        plt.show()


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


def export_simulation_to_viewer_format(sim, output_file):
    """Export simulation data in the format expected by the HTML viewer"""

    edges_added = set()
    edges_list = []

    for from_node in sim.environment.edges:
        for to_node, edge in sim.environment.edges[from_node].items():
            edge_tuple = tuple(sorted([from_node, to_node]))
            if edge_tuple not in edges_added:
                edges_list.append(
                    {
                        "vertex_a": edge.from_node,
                        "vertex_b": edge.to_node,
                        "weight": edge.weight,
                        "is_flooded": edge.is_flooded,
                    }
                )
                edges_added.add(edge_tuple)

    agents_list = []
    for i, agent in enumerate(sim.environment.agents):
        # State arrays (length = len(path))
        people_saved_history = []
        equipped_history = []
        score_history = []

        # Extract state from history
        for step in sim.history:
            agent_state = step["agents"][i]
            people_saved_history.append(agent_state["people_saved"])
            equipped_history.append(agent_state["equipped"])
            score_history.append(agent_state["score"])

        actions_list = sim.agent_actions[i]

        agent_data = {
            "type": agent.__class__.__name__,
            "start_vertex": sim.agent_paths[i][0],
            "path": sim.agent_paths[i],
            "actions": actions_list,
            "people_saved": people_saved_history,
            "equipped": equipped_history,
            "score": score_history,
        }

        agents_list.append(agent_data)

    # Build vertex history
    vertices_with_history = []
    for vertex_id, vertex in sim.environment.vertices.items():
        # Extract history for this vertex
        people_history = []
        kits_history = []

        for step in sim.history:
            vertex_state = step["vertices"][vertex_id]
            people_history.append(vertex_state["people_to_rescue"])
            kits_history.append(vertex_state["amphibian_kits"])

        vertex_data = {
            "id": vertex_id,
            "amphibian_kits": vertex.amphibian_kits,
            "people_to_rescue": vertex.people_to_rescue,
            "people_history": people_history,
            "kits_history": kits_history,
        }
        vertices_with_history.append(vertex_data)

    viewer_data = {
        "description": sim.description,
        "vertices": vertices_with_history,
        "edges": edges_list,
        "agents": agents_list,
    }

    with open(output_file, "w") as f:
        json.dump(viewer_data, f, indent=2)

    print(f"✓ Simulation data exported to: {output_file}")
    print(f"  - {len(viewer_data['vertices'])} vertices")
    print(f"  - {len(viewer_data['edges'])} edges")
    print(f"  - {len(viewer_data['agents'])} agents")
    print(f"  - {len(sim.history)} steps")
    print(f"\nOpen index.html and load this file to view the simulation!")


if __name__ == "__main__":
    options = get_all_config_options()

    parser = argparse.ArgumentParser(
        description="Export simulation data for HTML viewer"
    )
    parser.add_argument(
        "config_name",
        choices=options.keys(),
        help="The configuration to simulate and export",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="simulation_export.json",
        help="Output JSON file (default: simulation_export.json)",
    )

    args = parser.parse_args()

    print(f"\n=== Running simulation: {args.config_name} ===\n")

    sim = VisualSimulation(options[args.config_name])
    sim.run_simulation(visualize=False)

    print(f"\n=== Exporting data ===\n")
    export_simulation_to_viewer_format(sim, args.output)
