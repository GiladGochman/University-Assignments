"""Main entry point for Hurricane Evacuation simulation."""

from config import parse_config_string, config_flooded
from game import Game


def run_simulation(config, tactics=None):
    if tactics is None:
        tactics = ["Adversarial"]

    num_vertices, deadline, params, vertices_config, edges_config = parse_config_string(
        config
    )

    alpha_beta = True
    cutoff = 5
    agents_config = {"A": "V1", "B": "V2"}

    for tactic in tactics:
        print("-" * 60)
        print(f"Running Tactic: {tactic}")
        print("-" * 60)

        game = Game(
            deadline,
            params,
            vertices_config,
            edges_config,
            agents_config,
            tactic,
            cutoff,
            alpha_beta,
        )
        game.graph.save_plot()
        game.run_game()
        print()


if __name__ == "__main__":
    run_simulation(config_flooded)
