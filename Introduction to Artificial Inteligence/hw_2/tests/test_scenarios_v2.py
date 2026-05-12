import unittest
import matplotlib

matplotlib.use("Agg")

from config import parse_config_string
from models import VertexLocation, EdgeLocation
from graph import Graph
from state import State
from game import Game


class TestConfigParser(unittest.TestCase):
    """Test configuration parsing functionality"""

    def test_parse_basic_config(self):
        """Test parsing a basic configuration"""
        config = """
#N 3
#D 40
#V1 P10
#V2
#V3 P1

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)

        self.assertEqual(N, 3)
        self.assertEqual(D, 40)
        self.assertEqual(len(vertices_config), 3)
        self.assertEqual(vertices_config["V1"]["people"], 10)
        self.assertEqual(vertices_config["V2"]["people"], 0)
        self.assertEqual(vertices_config["V3"]["people"], 1)
        self.assertEqual(len(edges_config), 2)

    def test_parse_flooded_config(self):
        """Test parsing configuration with flooded edges"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W2 F
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)

        # Check flooded edge
        edge_v1v2 = edges_config["V1V2"]
        self.assertTrue(edge_v1v2[3])  # flooded flag
        self.assertEqual(edge_v1v2[2], 2)  # weight

        # Check non-flooded edge
        edge_v2v3 = edges_config["V2V3"]
        self.assertFalse(edge_v2v3[3])

    def test_parse_kit_config(self):
        """Test parsing configuration with amphibian kits"""
        config = """
#N 4
#D 50
#V1 P5 K2
#V2 P3
#V3 K3
#V4 P1

#E1 1 2 W1
#E2 2 3 W1
#E3 3 4 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        print(list(vertices_config))
        print(list(vertices_config))
        print(list(vertices_config))
        print(list(vertices_config))
        print(list(vertices_config))
        print("==============================")
        self.assertEqual(vertices_config["V1"]["kit_equip_time"], 2)
        self.assertEqual(vertices_config["V2"]["kit_equip_time"], 0)
        self.assertEqual(vertices_config["V3"]["kit_equip_time"], 3)
        self.assertEqual(vertices_config["V1"]["people"], 5)


class TestGraphConstruction(unittest.TestCase):
    """Test graph construction and properties"""

    def test_graph_from_config(self):
        """Test creating a graph from configuration"""
        vertices_config = {
            "V1": {"people": 5, "kit_equip_time": 0},
            "V2": {"people": 3, "kit_equip_time": 2},
            "V3": {"people": 0, "kit_equip_time": 0},
        }
        edges_config = {"V1V2": ("V1", "V2", 1, False), "V2V3": ("V2", "V3", 2, True)}

        graph = Graph.from_config(vertices_config, edges_config)

        self.assertEqual(len(graph.get_vertices()), 3)
        self.assertEqual(len(graph.get_edges()), 2)

        # Check vertex properties
        v1 = graph.get_vertices()["V1"]
        self.assertEqual(v1.n_people, 5)
        self.assertEqual(v1.kit_equip_time, 0)

        # Check edge properties
        edge_v2v3 = graph.get_edges()["V2V3"]
        self.assertTrue(edge_v2v3.flooded)
        self.assertEqual(edge_v2v3.w, 2)

    def test_edges_added_to_vertices(self):
        """Test that edges are correctly added to vertices"""
        vertices_config = {
            "V1": {"people": 0, "kit_equip_time": 0},
            "V2": {"people": 0, "kit_equip_time": 0},
        }
        edges_config = {"V1V2": ("V1", "V2", 1, False)}

        graph = Graph.from_config(vertices_config, edges_config)
        v1 = graph.get_vertices()["V1"]
        v2 = graph.get_vertices()["V2"]

        self.assertIn("V1V2", v1.edges)
        self.assertIn("V1V2", v2.edges)


class TestStateManagement(unittest.TestCase):
    """Test state creation and manipulation"""

    def setUp(self):
        """Set up a basic game for state tests"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        self.game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

    def test_initial_state(self):
        """Test initial state setup"""
        state = self.game.current_state

        # Agents should be at their starting vertices
        self.assertIsInstance(state.locations["A"], VertexLocation)
        self.assertEqual(state.locations["A"].v_id, "V1")
        self.assertIsInstance(state.locations["B"], VertexLocation)
        self.assertEqual(state.locations["B"].v_id, "V2")

        # People at starting vertices should be saved
        self.assertEqual(state.saved["A"], 5)
        self.assertEqual(state.saved["B"], 3)
        self.assertEqual(state.people["V1"], 0)
        self.assertEqual(state.people["V2"], 0)
        self.assertEqual(state.people["V3"], 2)

    def test_state_equality(self):
        """Test state equality comparison"""
        state1 = self.game.current_state

        # Create identical state
        state2 = State(
            self.game,
            state1.locations.copy(),
            state1.saved.copy(),
            state1.people.copy(),
            state1.kits_equipped.copy(),
            state1.kits_available.copy(),
            state1.time,
        )

        self.assertEqual(state1, state2)

    def test_successor_states_basic(self):
        """Test generating successor states"""
        state = self.game.current_state
        successors = state.get_successor_states("A")

        # Should have at least traverse and no-op actions
        self.assertGreater(len(successors), 0)

        # Check that actions are strings
        for successor_state, action in successors:
            self.assertIsInstance(action, str)
            self.assertIsInstance(successor_state, State)


class TestTraversalMechanics(unittest.TestCase):
    """Test edge traversal mechanics"""

    def test_single_weight_traversal(self):
        """Test traversing a single-weight edge"""
        config = """
#N 3
#D 40
#V1 P5
#V2
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        successors = state.get_successor_states("A")

        # Find traverse action to V2
        traverse_actions = [s for s in successors if "traverse to V2" in s[1]]
        self.assertGreater(len(traverse_actions), 0)

        new_state = traverse_actions[0][0]
        # Should arrive immediately at V2
        self.assertEqual(new_state.locations["A"].v_id, "V2")

    def test_multi_weight_traversal(self):
        """Test traversing a multi-weight edge"""
        config = """
#N 3
#D 40
#V1 P5
#V2
#V3 P2

#E1 1 2 W3
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
            alpha_beta=True,
        )

        state = game.current_state
        successors = state.get_successor_states("A")

        # Find start traverse action
        traverse_actions = [s for s in successors if "start_traverse to V2" in s[1]]
        self.assertGreater(len(traverse_actions), 0)

        new_state = traverse_actions[0][0]
        # Should be in EdgeLocation
        self.assertIsInstance(new_state.locations["A"], EdgeLocation)
        self.assertEqual(new_state.locations["A"].units, 2)  # 3-1 = 2 units left


class TestFloodedEdgeMechanics(unittest.TestCase):
    """Test flooded edge mechanics and amphibian kits"""

    def test_flooded_edge_blocking(self):
        """Test that flooded edges block agents without kits"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1 F
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        successors = state.get_successor_states("A")

        # Should not be able to traverse flooded edge without kit
        traverse_to_v2 = [s for s in successors if "V2" in s[1] and "traverse" in s[1]]
        self.assertEqual(len(traverse_to_v2), 0)

    def test_kit_equipping(self):
        """Test equipping an amphibian kit"""
        config = """
#N 3
#D 40
#V1 P5 K2
#V2 P3
#V3 P2

#E1 1 2 W1 F
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
            alpha_beta=True,
        )

        state = game.current_state

        # Check kit is available at V1
        self.assertTrue(state.kits_available["V1"])
        self.assertFalse(state.kits_equipped["A"])

        successors = state.get_successor_states("A")

        # Should have equip action
        equip_actions = [s for s in successors if "equip" in s[1]]
        self.assertGreater(len(equip_actions), 0)

    def test_kit_enables_flooded_traversal(self):
        """Test that equipped kit allows traversing flooded edges"""
        config = """
#N 3
#D 40
#V1 K1
#V2 P3
#V3 P2

#E1 1 2 W1 F
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
            alpha_beta=True,
        )

        # Manually equip kit
        state = game.current_state
        state.kits_equipped["A"] = True
        state.kits_available["V1"] = False

        successors = state.get_successor_states("A")

        # Should now be able to traverse flooded edge
        traverse_to_v2 = [s for s in successors if "V2" in s[1] and "traverse" in s[1]]
        self.assertGreater(len(traverse_to_v2), 0)

    def test_flooded_edge_time_multiplier(self):
        """Test that flooded edges with kit take P times longer"""
        config = """
#N 3
#D 40
#V1 K1
#V2 P3
#V3 P2

#E1 1 2 W2 F
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        P = 3  # Time multiplier
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            P=P,
            cutoff=5,
            alpha_beta=True,
        )

        # Equip kit
        state = game.current_state
        state.kits_equipped["A"] = True
        state.kits_available["V1"] = False

        successors = state.get_successor_states("A")

        # Find traverse action
        traverse_to_v2 = [s for s in successors if "start_traverse to V2" in s[1]]
        self.assertGreater(len(traverse_to_v2), 0)

        new_state = traverse_to_v2[0][0]
        # Weight should be 2 * 3 = 6, so units should be 5
        self.assertIsInstance(new_state.locations["A"], EdgeLocation)
        self.assertEqual(new_state.locations["A"].units, 5)  # 6-1 = 5

    def test_kit_unequipping(self):
        """Test unequipping a kit"""
        config = """
#N 2
#D 40
#V1 K1
#V2 P5

#E1 1 2 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        # Equip kit first
        state = game.current_state
        state.kits_equipped["A"] = True
        state.kits_available["V1"] = False

        successors = state.get_successor_states("A")

        # Should have unequip action
        unequip_actions = [s for s in successors if "unequip" in s[1]]
        self.assertGreater(len(unequip_actions), 0)

        new_state = unequip_actions[0][0]
        # Kit should be unequipped and available at V1
        self.assertFalse(new_state.kits_equipped["A"])
        self.assertTrue(new_state.kits_available["V1"])


class TestGameTactics(unittest.TestCase):
    """Test different game tactics (Adversarial, Cooperative)"""

    def test_adversarial_scoring(self):
        """Test adversarial heuristic scoring"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        h_value = state.get_heuristic_value("A")

        # A has 5 saved, B has 3 saved, so difference should be positive
        self.assertGreater(h_value, 0)

    def test_fully_cooperative_scoring(self):
        """Test fully cooperative heuristic scoring"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Fully Cooperative",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        h_value = state.get_heuristic_value("A")

        # Should be sum of both agents' scores
        self.assertEqual(h_value, 5 + 3)

    def test_semi_cooperative_scoring(self):
        """Test semi-cooperative heuristic scoring"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Semi Cooperative",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        h_value = state.get_heuristic_value("A")

        # Should return tuple for lexicographic comparison
        self.assertIsInstance(h_value, tuple)
        self.assertEqual(len(h_value), 2)


class TestAlphaBetaPruning(unittest.TestCase):
    """Test alpha-beta pruning functionality"""

    def test_alpha_beta_vs_minimax(self):
        """Compare alpha-beta pruning with regular minimax"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}

        # Test with alpha-beta
        game_ab = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        # Test without alpha-beta
        State.states_created = 0  # Reset counter
        game_no_ab = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=False,
        )

        # Both should find valid moves (we're just checking they work)
        agent_ab = game_ab.agents["A"]
        agent_no_ab = game_no_ab.agents["A"]

        best_state_ab, action_ab = agent_ab.alpha_beta_minmax_decision(True)
        best_state_no_ab, action_no_ab = agent_no_ab.alpha_beta_minmax_decision(False)

        # Both should return valid states and actions
        self.assertIsNotNone(best_state_ab)
        self.assertIsNotNone(action_ab)
        self.assertIsNotNone(best_state_no_ab)
        self.assertIsNotNone(action_no_ab)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_no_people_left(self):
        """Test game ends when no people left"""
        config = """
#N 2
#D 40
#V1
#V2

#E1 1 2 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        self.assertFalse(state.any_people_left())

    def test_deadline_reached(self):
        """Test cutoff at deadline"""
        config = """
#N 3
#D 5
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        self.assertFalse(state.cutoff_test(0))
        self.assertTrue(state.cutoff_test(3))

    def test_agent_at_vertex_with_people(self):
        """Test agent saves people when arriving at vertex"""
        config = """
#N 3
#D 40
#V1
#V2 P5
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        # Agent A should be able to traverse to V2
        successors = state.get_successor_states("A")
        traverse_to_v2 = [s for s in successors if "V2" in s[1] and "traverse" in s[1]]

        if len(traverse_to_v2) > 0:
            new_state = traverse_to_v2[0][0]
            # People at V2 should be saved by A
            self.assertEqual(new_state.saved["A"], 5)
            self.assertEqual(new_state.people["V2"], 0)

    def test_no_op_action(self):
        """Test no-op action"""
        config = """
#N 2
#D 40
#V1 P5
#V2 P3

#E1 1 2 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        state = game.current_state
        successors = state.get_successor_states("A")

        # Should have no-op action
        noop_actions = [s for s in successors if s[1] == "no-op"]
        self.assertGreater(len(noop_actions), 0)

        new_state = noop_actions[0][0]
        # State should be essentially the same except time
        self.assertEqual(new_state.time, state.time + 1)
        self.assertEqual(new_state.locations, state.locations)


class TestComplexScenarios(unittest.TestCase):
    """Test complex multi-step scenarios"""

    def test_multi_agent_coordination(self):
        """Test coordination between two agents"""
        config = """
#N 4
#D 40
#V1
#V2 P5
#V3 P3
#V4 P2

#E1 1 2 W1
#E2 2 3 W1
#E3 3 4 W1
#E4 1 4 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V4"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Fully Cooperative",
            cutoff=3,
            alpha_beta=True,
        )

        # Just verify the game initializes correctly with this scenario
        self.assertEqual(len(game.agents), 2)
        self.assertTrue(game.current_state.any_people_left())

    def test_flooded_network_with_multiple_kits(self):
        """Test complex scenario with multiple flooded edges and kits"""
        config = """
#N 5
#D 40
#V1 K2
#V2 P5
#V3 K1
#V4 P3
#V5 P2

#E1 1 2 W1 F
#E2 2 3 W2 F
#E3 3 4 W1
#E4 4 5 W1 F
#E5 1 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V5"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            P=2,
            cutoff=5,
            alpha_beta=True,
        )

        # Verify kits are available where expected
        self.assertTrue(game.current_state.kits_available["V1"])
        self.assertTrue(game.current_state.kits_available["V3"])
        self.assertFalse(game.current_state.kits_available["V2"])

    def test_state_revisit_detection(self):
        """Test that revisited states are detected"""
        config = """
#N 3
#D 40
#V1 P1
#V2
#V3

#E1 1 2 W1
#E2 2 3 W1
#E3 3 1 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
            alpha_beta=True,
        )

        initial_state = game.current_state
        self.assertIn(initial_state, game.visited_states)


class TestPerformance(unittest.TestCase):
    """Test performance and state space exploration"""

    def test_state_creation_count(self):
        """Test that state creation is tracked"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}

        State.states_created = 0
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=2,
            alpha_beta=True,
        )

        initial_count = State.states_created

        # Generate successors
        state = game.current_state
        successors = state.get_successor_states("A")

        # More states should have been created
        self.assertGreater(State.states_created, initial_count)

    def test_cutoff_limits_exploration(self):
        """Test that cutoff properly limits search depth"""
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}

        # Low cutoff
        State.states_created = 0
        game_low = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=2,
            alpha_beta=True,
        )

        agent = game_low.agents["A"]
        agent.alpha_beta_minmax_decision(True)
        states_low = State.states_created

        # Higher cutoff
        State.states_created = 0
        game_high = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=4,
            alpha_beta=True,
        )

        agent = game_high.agents["A"]
        agent.alpha_beta_minmax_decision(True)
        states_high = State.states_created

        # Higher cutoff should explore more states
        self.assertGreater(states_high, states_low)


class TestDetailedMechanics(unittest.TestCase):
    """Test precise game mechanics and state updates"""

    def test_traversal_units_decrement(self):
        """Test that edge traversal decrements units correctly over time"""
        config = """
#N 2
#D 10
#V1
#V2

#E1 1 2 W3
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
            alpha_beta=True,
        )

        # Turn 0: Start Traverse
        state_0 = game.current_state
        successors = state_0.get_successor_states("A")
        # Find start traverse action
        start_action = next(s for s in successors if "start_traverse" in s[1])
        state_1 = start_action[0]

        # Check T=1: Should be on Edge with W-1 units
        self.assertIsInstance(state_1.locations["A"], EdgeLocation)
        # Weight 3, so after 1 step, remaining units should be 2
        self.assertEqual(state_1.locations["A"].units, 2)

        # Turn 1: Continue (usually no-op or specific continue action depending on implementation)
        # Assuming the standard implementation allows 'no-op' or automatically decrements
        # if the agent is stuck on an edge in the next generator call
        successors_1 = state_1.get_successor_states("A")

        # In many implementations, being on an edge limits actions to just "continue"
        # or the next state naturally decrements. Let's pick the resulting state.
        state_2 = successors_1[0][0]

        # Check T=2: Should be on Edge with units=1
        self.assertIsInstance(state_2.locations["A"], EdgeLocation)
        self.assertEqual(state_2.locations["A"].units, 1)

        # Turn 2: Finish Traversal
        successors_2 = state_2.get_successor_states("A")
        state_3 = successors_2[0][0]

        # Check T=3: Should be at V2
        self.assertIsInstance(state_3.locations["A"], VertexLocation)
        self.assertEqual(state_3.locations["A"].v_id, "V2")

    def test_kit_consumption(self):
        """Test that when one agent takes a kit, it is removed for others"""
        config = """
#N 2
#D 10
#V1 K1
#V2

#E1 1 2 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        # Both agents at V1
        agents_config = {"A": "V1", "B": "V1"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
            alpha_beta=True,
        )

        state = game.current_state

        # 1. Verify kit is there
        self.assertTrue(state.kits_available["V1"])

        # 2. Agent A equips the kit
        successors_A = state.get_successor_states("A")
        equip_action = next(s for s in successors_A if "equip" in s[1])
        state_after_A_equip = equip_action[0]

        # 3. Verify kit is gone in the new state
        self.assertFalse(state_after_A_equip.kits_available["V1"])
        self.assertTrue(state_after_A_equip.kits_equipped["A"])

        # 4. In this new state, Agent B should NOT be able to equip
        # Note: We must ask for B's successors based on the state where A has already acted
        # (or if turns are simultaneous, this checks the logic of the state object itself)
        successors_B = state_after_A_equip.get_successor_states("B")
        equip_actions_B = [s for s in successors_B if "equip" in s[1]]

        self.assertEqual(
            len(equip_actions_B), 0, "Agent B should not be able to equip a taken kit"
        )


class TestHeuristicLogic(unittest.TestCase):
    """Test that heuristics favor the correct outcomes"""

    def setUp(self):
        config = """
#N 3
#D 10
#V1 P10
#V2
#V3

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        # FIX: We MUST include 'B' here so the game engine initializes data for Agent B.
        # We place B at V3 to keep it out of the way.
        agents_config = {"A": "V2", "B": "V3"}
        self.game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
            alpha_beta=True,
        )

    def test_preference_for_saving_people(self):
        """Heuristic should be higher for states where people are saved"""
        state_zero_saved = self.game.current_state

        # Manually create a state where A has saved people.
        # We must explicitly include 'B' in the saved dictionary to prevent KeyError.
        state_ten_saved = State(
            self.game,
            state_zero_saved.locations,
            {"A": 10, "B": 0},  # <--- FIX: B is included here
            state_zero_saved.people,
            state_zero_saved.kits_equipped,
            state_zero_saved.kits_available,
            state_zero_saved.time,
        )

        h_zero = state_zero_saved.get_heuristic_value("A")
        h_ten = state_ten_saved.get_heuristic_value("A")

        self.assertGreater(h_ten, h_zero, "Heuristic should value saving people")

    def test_preference_for_proximity(self):
        """Heuristic should arguably favor being closer to people"""
        state_near = self.game.current_state

        # Create a state where Agent A is further away (V3)
        locs = state_near.locations.copy()
        locs["A"] = VertexLocation("V3")

        state_far = State(
            self.game,
            locs,
            state_near.saved,  # This already includes 'B' from setUp
            state_near.people,
            state_near.kits_equipped,
            state_near.kits_available,
            state_near.time,
        )

        h_near = state_near.get_heuristic_value("B")
        h_far = state_far.get_heuristic_value("B")

        self.assertGreater(
            h_near, h_far, "Heuristic should not penalize being closer to people"
        )


class TestChainTopology(unittest.TestCase):
    """Test behaviors on linear 'chain' graph topologies: V1 - V2 - V3 - V4..."""

    def test_long_chain_traversal(self):
        """
        Test traversing a long chain to reach people at the very end.
        Topology: V1 --(1)--> V2 --(1)--> V3 --(1)--> V4 --(1)--> V5 (People here)
        """
        config = """
#N 5
#D 20
#V1
#V2
#V3
#V4
#V5 P10

#E1 1 2 W1
#E2 2 3 W1
#E3 3 4 W1
#E4 4 5 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1"}

        # Cutoff must be high enough to see the end of the chain
        # Depth needed is 4 steps.
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=6,
            alpha_beta=True,
        )

        current_state = game.current_state

        # Simulate the chain traversal step-by-step
        expected_path = ["V1", "V2", "V3", "V4", "V5"]

        for i in range(len(expected_path) - 1):
            curr_node = expected_path[i]
            next_node = expected_path[i + 1]

            # Verify we are at the current node
            self.assertEqual(current_state.locations["A"].v_id, curr_node)

            # Find move to next node
            successors = current_state.get_successor_states("A")

            # Look for the specific action that goes to the next node
            # Action string format might vary, looking for destination in string
            next_step = None
            for state, action in successors:
                if (
                    f"traverse to {next_node}" in action
                    or f"start_traverse to {next_node}" in action
                ):
                    next_step = state
                    break

            self.assertIsNotNone(
                next_step, f"Agent at {curr_node} could not find path to {next_node}"
            )
            current_state = next_step

        # Final check: Arrived at V5 and saved people
        self.assertEqual(current_state.locations["A"].v_id, "V5")
        self.assertEqual(current_state.saved["A"], 10)

    def test_broken_chain_with_kit(self):
        """
        Test a chain where the middle link is flooded, requiring a kit from the start.
        Topology: V1(Kit) --(Flooded)--> V2 --(Normal)--> V3(People)
        """
        config = """
    #N 3
    #D 20
    #V1 K1
    #V2
    #V3 P5

    #E1 1 2 W1 F
    #E2 2 3 W1
    """
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1"}
        # Explicitly set P=1 to keep math simple, though the loop below handles P>1 too
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            P=1,
            cutoff=10,
            alpha_beta=True,
        )

        state = game.current_state

        # 1. Agent must equip kit first
        successors = state.get_successor_states("A")
        equip_state = next((s for s, act in successors if "equip" in act), None)
        self.assertIsNotNone(equip_state, "Agent should be able to equip kit at V1")

        # 2. Agent starts traversal V1 -> V2 (Flooded)
        successors_2 = equip_state.get_successor_states("A")
        # This might be 'traverse' (immediate) or 'start_traverse' (takes time)
        move_v2_action = next(
            ((s, act) for s, act in successors_2 if "traverse to V2" in act), None
        )
        self.assertIsNotNone(
            move_v2_action, "Should traverse flooded edge after equipping"
        )

        state = move_v2_action[0]

        # === FIX: ROBUST TRAVERSAL LOOP ===
        # If the agent is on an EdgeLocation, keep stepping forward until they reach the vertex
        while isinstance(state.locations["A"], EdgeLocation):
            successors_step = state.get_successor_states("A")
            # Usually only one valid action while on edge (continue/no-op)
            state = successors_step[0][0]

        # Verify we actually arrived at V2
        self.assertEqual(
            state.locations["A"].v_id, "V2", "Agent got stuck and never reached V2"
        )

        # 3. Now agent traverses V2 -> V3
        successors_3 = state.get_successor_states("A")
        move_v3_state = next(
            (s for s, act in successors_3 if "traverse to V3" in act), None
        )

        # Handle case where specific rules force unequipping before walking on normal ground
        if move_v3_state is None:
            unequip_state = next(
                (s for s, act in successors_3 if "unequip" in act), None
            )
            if unequip_state:
                # If we must unequip, do so, then try moving again
                successors_4 = unequip_state.get_successor_states("A")
                move_v3_state = next(
                    (s for s, act in successors_4 if "traverse to V3" in act), None
                )

        self.assertIsNotNone(move_v3_state, "Should reach final node (V3)")

        # Verify people saved
        self.assertEqual(move_v3_state.saved["A"], 5)


class TestParserRobustness(unittest.TestCase):
    """Test parser resilience to weird formatting"""

    def test_extra_whitespace(self):
        config = """
#N    2
#D 10
#V1      P10
#V2

#E1   1    2    W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        self.assertEqual(N, 2)
        self.assertEqual(vertices_config["V1"]["people"], 10)
        self.assertEqual(edges_config["V1V2"][2], 1)


class TestTreeTopology(unittest.TestCase):
    """
    Test behaviors on branching 'tree' graph topologies.
    Structure:
           V1 (Root)
          /  \
        V2    V3
       /      \
     V4       V5 (Goal: People here)
    """

    def _ensure_arrival(self, game, agent_id, target_v_id):
        """
        Helper: Advances the state until the agent actually arrives at the target vertex.
        Handles cases where the agent is 'walking' on an edge (EdgeLocation).
        """
        state = game.current_state

        # 1. Find the move command (start_traverse or traverse)
        successors = state.get_successor_states(agent_id)

        # Look for explicit traverse command
        action_pair = next(
            ((s, a) for s, a in successors if f"traverse to {target_v_id}" in a), None
        )

        if not action_pair:
            # If not found, check if we are already on the edge heading there?
            # Or maybe we need to 'no-op' if we are already walking.
            # For this test helper, we assume we are at a vertex looking to move.
            self.fail(
                f"Agent at {state.locations[agent_id]} has no action to traverse to {target_v_id}"
            )

        new_state = action_pair[0]

        # 2. Loop until agent is at a VertexLocation
        # (Simulates time passing while walking on the edge)
        steps = 0
        while isinstance(new_state.locations[agent_id], EdgeLocation) and steps < 10:
            # While walking, get the next state (usually forced continue or no-op)
            succs = new_state.get_successor_states(agent_id)
            if not succs:
                self.fail("Agent got stuck on edge (no successors)")
            new_state = succs[0][0]
            steps += 1

        game.current_state = new_state
        self.assertIsInstance(new_state.locations[agent_id], VertexLocation)
        self.assertEqual(new_state.locations[agent_id].v_id, target_v_id)

    def test_binary_tree_traversal(self):
        """Test navigating the correct branch of a tree to find people"""
        config = """
#N 5
#D 20
#V1
#V2
#V3
#V4
#V5 P10

#E1 1 2 W1
#E2 1 3 W1
#E3 2 4 W1
#E4 3 5 W1
"""
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=6,
            alpha_beta=True,
        )

        # Path should be V1 -> V3 -> V5

        # Step 1: Move Root to Right Child (V3)
        self._ensure_arrival(game, "A", "V3")

        # Step 2: Move Right Child to Right Leaf (V5)
        self._ensure_arrival(game, "A", "V5")

        # Verify people are saved
        self.assertEqual(game.current_state.saved["A"], 10)

    def test_heuristic_branch_choice(self):
        """
        Test that the AI *decides* to go the right way.
        This checks the alpha_beta_minmax_decision result directly.
        """
        config = """
#N 3
#D 20
#V1
#V2
#V3 P10

#E1 1 2 W1
#E2 1 3 W1
"""
        # V1 connects to V2 (empty) and V3 (10 people).
        # A smart agent should choose V3.
        N, D, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=4,
            alpha_beta=True,
        )

        agent = game.agents["A"]

        # Ask the AI for its best move
        best_state, action = agent.alpha_beta_minmax_decision(True)

        self.assertIsNotNone(action)
        # We expect the action to be related to V3
        self.assertIn(
            "V3",
            action,
            f"AI chose '{action}' but should have chosen V3 to save people",
        )


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigParser))
    suite.addTests(loader.loadTestsFromTestCase(TestGraphConstruction))
    suite.addTests(loader.loadTestsFromTestCase(TestStateManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestTraversalMechanics))
    suite.addTests(loader.loadTestsFromTestCase(TestFloodedEdgeMechanics))
    suite.addTests(loader.loadTestsFromTestCase(TestGameTactics))
    suite.addTests(loader.loadTestsFromTestCase(TestAlphaBetaPruning))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))

    # Add NEW test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDetailedMechanics))
    suite.addTests(loader.loadTestsFromTestCase(TestHeuristicLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestParserRobustness))
    suite.addTests(
        loader.loadTestsFromTestCase(TestChainTopology)
    )  # <--- Added this line
    suite.addTests(loader.loadTestsFromTestCase(TestTreeTopology))  # <--- Added this
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    # Suppress matplotlib plotting during tests
    import matplotlib.pyplot as plt

    plt.ioff()

    run_tests()
