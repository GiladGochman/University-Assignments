import unittest
import matplotlib

matplotlib.use("Agg")

from config import parse_config_string
from models import VertexLocation, EdgeLocation, UnequippingLocation
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
        # Unpack 5 values now
        N, D, params, vertices_config, edges_config = parse_config_string(config)

        self.assertEqual(N, 3)
        self.assertEqual(D, 80)
        self.assertEqual(len(vertices_config), 3)
        self.assertEqual(vertices_config["V1"]["people"], 10)
        self.assertEqual(vertices_config["V2"]["people"], 0)
        self.assertEqual(vertices_config["V3"]["people"], 1)
        self.assertEqual(len(edges_config), 2)
        # Check default params
        self.assertEqual(params["equip_time"], 1)

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
        N, D, params, vertices_config, edges_config = parse_config_string(config)

        # Check flooded edge
        edge_v1v2 = edges_config[
            "#E1"
        ]  # Key uses full tag in new parser if not careful,
        # actually looking at config.py provided previously: edges_data[tag] = ...
        # The tag is "#E1". Let's check the values.

        # Helper to find edge by connectivity since keys might be tags
        edge_data = next(
            e for k, e in edges_config.items() if e[0] == "V1" and e[1] == "V2"
        )
        self.assertTrue(edge_data[3])  # flooded flag
        self.assertEqual(edge_data[2], 2)  # weight

    def test_parse_kit_config(self):
        """Test parsing configuration with amphibian kits"""
        config = """
#N 4
#D 50
#Q 2
#V1 P5 K
#V2 P3
#V3 K
#V4 P1

#E1 1 2 W1
#E2 2 3 W1
#E3 3 4 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)

        # Check Global Equip Time
        self.assertEqual(params["equip_time"], 2)

        # Check Kits exist (list of IDs)
        self.assertGreater(len(vertices_config["V1"]["kits"]), 0)
        self.assertEqual(len(vertices_config["V2"]["kits"]), 0)
        self.assertGreater(len(vertices_config["V3"]["kits"]), 0)

        self.assertEqual(vertices_config["V1"]["people"], 5)


class TestGraphConstruction(unittest.TestCase):
    """Test graph construction and properties"""

    def test_graph_from_config(self):
        """Test creating a graph from configuration"""
        # Config structure must match what parse_config_string produces
        vertices_config = {
            "V1": {"people": 5, "kits": []},
            "V2": {"people": 3, "kits": ["K0", "K1"]},
            "V3": {"people": 0, "kits": []},
        }
        edges_config = {"V1V2": ("V1", "V2", 1, False), "V2V3": ("V2", "V3", 2, True)}

        graph = Graph.from_config(vertices_config, edges_config)

        self.assertEqual(len(graph.get_vertices()), 3)
        self.assertEqual(len(graph.get_edges()), 2)

        # Check vertex properties
        v1 = graph.get_vertices()["V1"]
        self.assertEqual(v1.n_people, 5)
        self.assertEqual(len(v1.initial_kits), 0)

        v2 = graph.get_vertices()["V2"]
        self.assertEqual(len(v2.initial_kits), 2)

        # Check edge properties
        edge_v2v3 = graph.get_edges()["V2V3"]
        self.assertTrue(edge_v2v3.flooded)
        self.assertEqual(edge_v2v3.w, 2)

    def test_edges_added_to_vertices(self):
        """Test that edges are correctly added to vertices"""
        vertices_config = {
            "V1": {"people": 0, "kits": []},
            "V2": {"people": 0, "kits": []},
        }
        edges_config = {"E1": ("V1", "V2", 1, False)}

        graph = Graph.from_config(vertices_config, edges_config)
        v1 = graph.get_vertices()["V1"]
        v2 = graph.get_vertices()["V2"]

        self.assertIn("E1", v1.edges)
        self.assertIn("E1", v2.edges)


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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        self.game = Game(
            D,
            params,  # Pass params
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

        # Kits held should be None
        self.assertIsNone(state.kits_held["A"])

        # People at starting vertices should be saved
        self.assertEqual(state.saved["A"], 5)
        self.assertEqual(state.saved["B"], 3)
        self.assertEqual(state.people["V1"], 0)

    def test_state_equality(self):
        """Test state equality comparison"""
        state1 = self.game.current_state

        # Create identical state using new signature
        state2 = State(
            self.game,
            state1.locations.copy(),
            state1.saved.copy(),
            state1.people.copy(),
            state1.kits_on_vertices.copy(),  # Changed from kits_available
            state1.kits_held.copy(),  # Changed from kits_equipped
            state1.time,
        )

        self.assertEqual(state1, state2)

    def test_successor_states_basic(self):
        """Test generating successor states"""
        state = self.game.current_state
        successors = state.get_successor_states("A")

        self.assertGreater(len(successors), 0)
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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D,
            params,
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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
            alpha_beta=True,
        )

        state = game.current_state
        successors = state.get_successor_states("A")

        traverse_actions = [s for s in successors if "start_traverse to V2" in s[1]]
        self.assertGreater(len(traverse_actions), 0)

        new_state = traverse_actions[0][0]
        self.assertIsInstance(new_state.locations["A"], EdgeLocation)
        self.assertEqual(new_state.locations["A"].units, 2)


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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        state = game.current_state
        successors = state.get_successor_states("A")

        traverse_to_v2 = [s for s in successors if "V2" in s[1] and "traverse" in s[1]]
        self.assertEqual(len(traverse_to_v2), 0)

    def test_kit_equipping(self):
        """Test equipping an amphibian kit"""
        config = """
#N 3
#D 40
#V1 P5 K
#V2 P3
#V3 P2

#E1 1 2 W1 F
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        state = game.current_state

        # Check kit is on V1 (Set should not be empty)
        self.assertTrue(state.kits_on_vertices.get("V1"))
        self.assertIsNone(state.kits_held["A"])

        successors = state.get_successor_states("A")
        equip_actions = [s for s in successors if "equip" in s[1]]
        self.assertGreater(len(equip_actions), 0)

    def test_kit_enables_flooded_traversal(self):
        """Test that equipped kit allows traversing flooded edges"""
        config = """
#N 3
#D 40
#V1 K
#V2 P3
#V3 P2

#E1 1 2 W1 F
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        # Manually equip kit
        state = game.current_state
        state.kits_held["A"] = "K0"  # Assign an ID
        state.kits_on_vertices["V1"] = frozenset()  # Empty the vertex

        successors = state.get_successor_states("A")

        traverse_to_v2 = [s for s in successors if "V2" in s[1] and "traverse" in s[1]]
        self.assertGreater(len(traverse_to_v2), 0)

    def test_flooded_edge_time_multiplier(self):
        """Test that flooded edges with kit take P times longer"""
        config = """
#N 3
#D 40
#P 3
#V1 K
#V2 P3
#V3 P2

#E1 1 2 W2 F
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}

        # Params should have P=3 from config
        self.assertEqual(params["flood_penalty"], 3)

        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        state = game.current_state
        state.kits_held["A"] = "K0"
        state.kits_on_vertices["V1"] = frozenset()

        successors = state.get_successor_states("A")
        traverse_to_v2 = [s for s in successors if "start_traverse to V2" in s[1]]
        self.assertGreater(len(traverse_to_v2), 0)

        new_state = traverse_to_v2[0][0]
        # Weight 2 * P(3) = 6. Remaining units 5.
        self.assertIsInstance(new_state.locations["A"], EdgeLocation)
        self.assertEqual(new_state.locations["A"].units, 5)

    def test_kit_unequipping(self):
        """Test unequipping a kit"""
        config = """
#N 2
#D 40
#V1 K
#V2 P5

#E1 1 2 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        state = game.current_state
        state.kits_held["A"] = "K0"
        state.kits_on_vertices["V1"] = frozenset()

        successors = state.get_successor_states("A")
        unequip_actions = [s for s in successors if "unequip" in s[1]]
        self.assertGreater(len(unequip_actions), 0)

        new_state = unequip_actions[0][0]
        # Kit should be unequipped (None) and available at V1 (in set)
        self.assertIsNone(new_state.kits_held["A"])
        self.assertTrue("K0" in new_state.kits_on_vertices["V1"])


class TestGameTactics(unittest.TestCase):
    """Test different game tactics (Adversarial, Cooperative)"""

    def test_adversarial_scoring(self):
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        state = game.current_state
        h_value = state.get_heuristic_value("A")
        self.assertGreater(h_value, 0)

    def test_fully_cooperative_scoring(self):
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Fully Cooperative"
        )

        state = game.current_state
        h_value = state.get_heuristic_value("A")
        print(h_value)
        self.assertEqual(h_value, 7.99)

    def test_semi_cooperative_scoring(self):
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Semi Cooperative"
        )

        state = game.current_state
        h_value = state.get_heuristic_value("A")
        self.assertIsInstance(h_value, tuple)


class TestAlphaBetaPruning(unittest.TestCase):
    """Test alpha-beta pruning functionality"""

    def test_alpha_beta_vs_minimax(self):
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}

        game_ab = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            alpha_beta=True,
        )

        State.states_created = 0
        game_no_ab = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            alpha_beta=False,
        )

        agent_ab = game_ab.agents["A"]
        agent_no_ab = game_no_ab.agents["A"]

        best_state_ab, action_ab = agent_ab.alpha_beta_minmax_decision(True)
        best_state_no_ab, action_no_ab = agent_no_ab.alpha_beta_minmax_decision(False)

        self.assertIsNotNone(best_state_ab)
        self.assertIsNotNone(action_ab)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_no_people_left(self):
        config = """
#N 2
#D 40
#V1
#V2

#E1 1 2 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        state = game.current_state
        self.assertFalse(state.any_people_left())

    def test_deadline_reached(self):
        config = """
#N 3
#D 5
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
        )
        state = game.current_state
        self.assertFalse(state.cutoff_test(4))
        self.assertTrue(state.cutoff_test(5))

    def test_agent_at_vertex_with_people(self):
        config = """
#N 3
#D 40
#V1
#V2 P5
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V3"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        state = game.current_state
        successors = state.get_successor_states("A")
        traverse_to_v2 = [s for s in successors if "V2" in s[1] and "traverse" in s[1]]

        if len(traverse_to_v2) > 0:
            new_state = traverse_to_v2[0][0]
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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=3,
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

    def test_multi_agent_coordination(self):
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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V4"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Fully Cooperative"
        )
        self.assertEqual(len(game.agents), 2)

    def test_flooded_network_with_multiple_kits(self):
        config = """
#N 5
#D 40
#P 2
#V1 K
#V2 P5
#V3 K
#V4 P3
#V5 P2

#E1 1 2 W1 F
#E2 2 3 W2 F
#E3 3 4 W1
#E4 4 5 W1 F
#E5 1 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V5"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        # Check for kits (non-empty set)
        self.assertTrue(game.current_state.kits_on_vertices.get("V1"))
        self.assertTrue(game.current_state.kits_on_vertices.get("V3"))
        # V2 should be empty or None
        self.assertFalse(game.current_state.kits_on_vertices.get("V2"))

    def test_state_revisit_detection(self):
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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        initial_state = game.current_state
        self.assertIn(initial_state, game.visited_states)


class TestPerformance(unittest.TestCase):

    def test_state_creation_count(self):
        config = """
#N 3
#D 40
#V1 P5
#V2 P3
#V3 P2

#E1 1 2 W1
#E2 2 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}

        State.states_created = 0
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=2,
        )
        initial_count = State.states_created

        state = game.current_state
        successors = state.get_successor_states("A")
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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}

        # Low cutoff
        State.states_created = 0
        game_low = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=2,
        )

        agent = game_low.agents["A"]
        agent.alpha_beta_minmax_decision(True)
        states_low = State.states_created

        # Higher cutoff
        State.states_created = 0
        game_high = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=4,
        )

        agent = game_high.agents["A"]
        agent.alpha_beta_minmax_decision(True)
        states_high = State.states_created

        # Higher cutoff should explore more states
        self.assertGreater(states_high, states_low)


class TestDetailedMechanics(unittest.TestCase):

    def test_traversal_units_decrement(self):
        config = """
#N 2
#D 10
#V1
#V2

#E1 1 2 W3
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1"}
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=5,
        )

        state_0 = game.current_state
        successors = state_0.get_successor_states("A")
        start_action = next(s for s in successors if "start_traverse" in s[1])
        state_1 = start_action[0]

        # W3 -> 2 units left after 1st step
        self.assertEqual(state_1.locations["A"].units, 2)

    def test_kit_consumption(self):
        config = """
#N 2
#D 10
#V1 K
#V2

#E1 1 2 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V1"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

        state = game.current_state

        # 1. Verify kit is there
        self.assertTrue(state.kits_on_vertices.get("V1"))

        # 2. Agent A equips
        successors_A = state.get_successor_states("A")
        equip_action = next(s for s in successors_A if "equip" in s[1])
        state_after_A_equip = equip_action[0]

        # 3. Verify kit is gone
        self.assertFalse(state_after_A_equip.kits_on_vertices.get("V1"))
        self.assertTrue(state_after_A_equip.kits_held["A"])

        # 4. Agent B cannot equip
        successors_B = state_after_A_equip.get_successor_states("B")
        equip_actions_B = [s for s in successors_B if "equip" in s[1]]
        self.assertEqual(len(equip_actions_B), 0)


class TestHeuristicLogic(unittest.TestCase):

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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V2", "B": "V3"}
        self.game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )

    def test_preference_for_saving_people(self):
        state_zero_saved = self.game.current_state
        state_ten_saved = State(
            self.game,
            state_zero_saved.locations,
            {"A": 10, "B": 0},
            state_zero_saved.people,
            state_zero_saved.kits_on_vertices,
            state_zero_saved.kits_held,
            state_zero_saved.time,
        )

        h_zero = state_zero_saved.get_heuristic_value("A")
        h_ten = state_ten_saved.get_heuristic_value("A")
        self.assertGreater(h_ten, h_zero)

    def test_preference_for_proximity(self):
        state_near = self.game.current_state
        locs = state_near.locations.copy()
        locs["A"] = VertexLocation("V3")

        state_far = State(
            self.game,
            locs,
            state_near.saved,
            state_near.people,
            state_near.kits_on_vertices,
            state_near.kits_held,
            state_near.time,
        )

        # B is at V3. People at V1.
        # This test logic seems to assume V3 is further from V1 than V2?
        # V1-V2 (W1), V2-V3 (W1).
        # Distance V2->V1 is 1. Distance V3->V1 is 2.
        # So "state_near" (A at V2) is closer to V1 than "state_far" (A at V3).
        # We check heuristic for A? The original test checked for B.
        # "h_near = state_near.get_heuristic_value('B')"
        # In setup, B is at V3. People at V1.
        # B is 2 hops away.
        # In state_far, B is still at V3.
        # The logic in original test modified A's location but checked B's heuristic?
        # Let's fix this to check A's heuristic where A moves.

        # Original test intent: A is player.
        # State Near: A at V2 (Dist 1).
        # State Far: A at V3 (Dist 2).
        h_near = state_near.get_heuristic_value("A")
        h_far = state_far.get_heuristic_value("A")

        self.assertGreater(h_near, h_far)

    def test_preference_for_saving_people(self):
        """Heuristic should be higher for states where people are saved"""
        state_zero_saved = self.game.current_state

        state_ten_saved = State(
            self.game,
            state_zero_saved.locations,
            {"A": 10, "B": 0},
            state_zero_saved.people,
            state_zero_saved.kits_on_vertices,
            state_zero_saved.kits_held,
            state_zero_saved.time,
        )

        h_zero = state_zero_saved.get_heuristic_value("A")
        h_ten = state_ten_saved.get_heuristic_value("A")

        self.assertGreater(h_ten, h_zero, "Heuristic should value saving people")


class TestChainTopology(unittest.TestCase):

    def test_long_chain_traversal(self):
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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1"}
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=6,
        )

        current_state = game.current_state
        expected_path = ["V1", "V2", "V3", "V4", "V5"]

        for i in range(len(expected_path) - 1):
            curr_node = expected_path[i]
            next_node = expected_path[i + 1]

            self.assertEqual(current_state.locations["A"].v_id, curr_node)
            successors = current_state.get_successor_states("A")
            next_step = None
            for state, action in successors:
                if f"to {next_node}" in action:
                    next_step = state
                    break
            self.assertIsNotNone(next_step)
            current_state = next_step

        self.assertEqual(current_state.locations["A"].v_id, "V5")
        self.assertEqual(current_state.saved["A"], 10)

    def test_broken_chain_with_kit(self):
        config = """
    #N 3
    #D 20
    #P 1
    #V1 K
    #V2
    #V3 P5

    #E1 1 2 W1 F
    #E2 2 3 W1
    """
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1"}
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=10,
        )

        state = game.current_state

        # 1. Equip
        successors = state.get_successor_states("A")
        equip_state = next((s for s, act in successors if "equip" in act), None)
        self.assertIsNotNone(equip_state)

        # 2. Traverse V1->V2 (Flooded)
        successors_2 = equip_state.get_successor_states("A")
        move_v2_action = next(
            ((s, act) for s, act in successors_2 if "to V2" in act), None
        )
        self.assertIsNotNone(move_v2_action)
        state = move_v2_action[0]

        while isinstance(state.locations["A"], EdgeLocation):
            successors_step = state.get_successor_states("A")
            state = successors_step[0][0]

        self.assertEqual(state.locations["A"].v_id, "V2")

        # 3. Traverse V2->V3
        successors_3 = state.get_successor_states("A")
        move_v3_state = next((s for s, act in successors_3 if "to V3" in act), None)

        # If forced unequip logic exists, handle it (depends on state.py implementation)
        # In current logic, you don't *have* to unequip to walk on normal ground,
        # so traverse should be available.
        self.assertIsNotNone(move_v3_state)
        self.assertEqual(move_v3_state.saved["A"], 5)


class TestTreeTopology(unittest.TestCase):

    def _ensure_arrival(self, game, agent_id, target_v_id):
        state = game.current_state
        successors = state.get_successor_states(agent_id)
        action_pair = next(
            ((s, a) for s, a in successors if f"to {target_v_id}" in a), None
        )
        if not action_pair:
            self.fail(f"No action to {target_v_id}")

        new_state = action_pair[0]
        steps = 0
        while isinstance(new_state.locations[agent_id], EdgeLocation) and steps < 10:
            succs = new_state.get_successor_states(agent_id)
            new_state = succs[0][0]
            steps += 1

        game.current_state = new_state
        self.assertEqual(new_state.locations[agent_id].v_id, target_v_id)

    def test_binary_tree_traversal(self):
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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1"}
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=6,
        )

        self._ensure_arrival(game, "A", "V3")
        self._ensure_arrival(game, "A", "V5")
        self.assertEqual(game.current_state.saved["A"], 10)

    def test_heuristic_branch_choice(self):
        config = """
#N 3
#D 20
#V1
#V2
#V3 P10

#E1 1 2 W1
#E2 1 3 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=4,
        )

        agent = game.agents["A"]
        best_state, action = agent.alpha_beta_minmax_decision(True)

        self.assertIsNotNone(action)
        self.assertIn("V3", action)


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
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        self.assertEqual(N, 2)
        self.assertEqual(vertices_config["V1"]["people"], 10)

        # Helper to find edge since key might be full tag string
        edge_data = list(edges_config.values())[0]
        self.assertEqual(edge_data[2], 1)


class TestAdvancedFeatures(unittest.TestCase):
    """Test advanced logic features like tie-breaking and generic IDs"""

    def test_semi_cooperative_tie_breaker(self):
        """
        Test that in Semi-Cooperative mode, if two moves give the Agent the SAME score,
        it picks the one that results in a higher score for the Opponent.
        """
        # Scenario:
        # Agent A is at V1.
        # Choice 1: Go to V2 (P1). B is stuck. (A=1, B=0)
        # Choice 2: Go to V3 (P1). This unblocks V4 for B (P1). (A=1, B=1)
        # Agent A should choose V3.
        config = """
#N 4
#D 10
#V1
#V2 P1
#V3 P1
#V4 P1

#E1 1 2 W1
#E2 1 3 W1
#E3 3 4 W1
"""
        # Note: We simulate the "Unblocking" logic abstractly here by saying
        # checking which state yields the higher heuristic tuple.
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V4"}

        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Semi Cooperative"
        )
        state = game.current_state

        # Manually construct the two potential future outcomes to check heuristic comparison

        # Outcome 1: A saves V2 (1 point), B saves nothing (0 points)
        state_selfish = State(
            game,
            state.locations,
            {"A": 1, "B": 0},
            state.people,
            state.kits_on_vertices,
            state.kits_held,
            state.time,
        )

        # Outcome 2: A saves V3 (1 point), B saves V4 (1 point)
        state_altruistic = State(
            game,
            state.locations,
            {"A": 1, "B": 1},
            state.people,
            state.kits_on_vertices,
            state.kits_held,
            state.time,
        )

        h_selfish = state_selfish.get_heuristic_value("A")  # Should be roughly (1, 0)
        h_altruistic = state_altruistic.get_heuristic_value(
            "A"
        )  # Should be roughly (1, 1)

        # Tuple comparison: (1, 1) > (1, 0)
        self.assertGreater(
            h_altruistic,
            h_selfish,
            "Should prefer helping opponent if my score is tied",
        )

    def test_multiple_kits_distribution(self):
        """Test that multiple kits at one vertex can be picked up by different agents"""
        config = """
#N 2
#D 10
#V1 K K
#V2

#E1 1 2 W1
"""
        # V1 has 2 kits (K K)
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V1"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )
        state = game.current_state

        # 1. Verify 2 kits exist
        self.assertEqual(len(state.kits_on_vertices["V1"]), 2)

        # 2. Agent A equips one
        succ_a = state.get_successor_states("A")
        equip_a = next(s for s in succ_a if "equip" in s[1])[0]

        # 3. Agent B equips the other (from the state where A already took one)
        succ_b = equip_a.get_successor_states("B")
        equip_b = next(s for s in succ_b if "equip" in s[1])[0]

        # 4. Verify both have kits and IDs are different
        self.assertIsNotNone(equip_b.kits_held["A"])
        self.assertIsNotNone(equip_b.kits_held["B"])
        self.assertNotEqual(equip_b.kits_held["A"], equip_b.kits_held["B"])

        # 5. Verify V1 is now empty
        self.assertEqual(len(equip_b.kits_on_vertices["V1"]), 0)

    def test_custom_agent_ids(self):
        """Test that the game works with non-standard agent IDs"""
        config = """
#N 2
#D 10
#V1 P1
#V2

#E1 1 2 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        # Use "Red" and "Blue" instead of "A" and "B"
        agents_config = {"Red": "V1", "Blue": "V2"}

        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )
        state = game.current_state

        # Check initialization
        self.assertIn("Red", state.locations)
        self.assertIn("Blue", state.locations)

        # Check heuristic calculation doesn't crash
        h_val = state.get_heuristic_value("Red")
        self.assertIsInstance(h_val, int)


class TestReadmeScenarios(unittest.TestCase):
    def test_scenario_1_greedy_split(self):
        """
        Scenario 1: Agent A chooses between 10 people (selfish) or 1 person (cooperative).
        """
        config = """
    #N 4
    #D 12
    #V1
    #V2
    #V3 P1
    #V4 P10
    #E1 1 3 W1
    #E2 2 4 W4
    #E3 1 4 W2
    """
        # EXPLANATION OF FIX:
        # 1. Increased Deadline to 12 to ensure B has plenty of time.
        # 2. Changed E2 (B's path) to W4.
        #    - A (W2) is still faster than B (W4), so A *could* be greedy.
        #    - But B is fast enough to arrive before D=12.

        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}

        # 1. Test Adversarial (Greedy)
        # Agent A takes V4 (10 pts) because it's worth more than V3 (1 pt).
        game_adv = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=6,
        )
        action_adv = game_adv.agents["A"].act(alpha_beta=True)
        self.assertIn("V4", action_adv, "Adversarial Agent A should greedily target V4")

        # 2. Test Fully Cooperative (Teamwork)
        # Agent A takes V3 (1 pt) so Agent B can take V4 (10 pts). Total = 11.
        # (If A took V4, B would get 0, Total = 10).
        game_coop = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Fully Cooperative",
            cutoff=12,
        )
        action_coop = game_coop.agents["A"].act(alpha_beta=True)
        self.assertIn(
            "V3", action_coop, "Cooperative Agent A should target V3 so B can take V4"
        )

    def test_scenario_2_spite(self):
        """
        Scenario 2: Spiteful behavior check.
        """
        config = """
#N 5
#D 1
#V1
#V2
#V3 P5
#V4 P5
#V5 P5
#E1 1 3 W1
#E2 1 4 W1
#E3 2 3 W2
#E4 2 4 W10
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V2"}
        # 1. Test Adversarial (Spiteful)
        game_adv = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=6,
        )
        action_adv = game_adv.agents["A"].act(alpha_beta=True)
        self.assertTrue("V3" in action_adv, "Adversarial A should block B by taking V3")

        # 2. Test Semi-Cooperative (Benevolent tie-breaker)
        game_semi = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Semi Cooperative",
            cutoff=6,
        )
        action_semi = game_semi.agents["A"].act(alpha_beta=True)
        # With state.py fix, A picks V4 because (5, 5) > (5, 0)
        self.assertTrue(
            "V4" in action_semi, "Semi-Coop A should take V4 to allow B to score at V3"
        )

    def test_scenario_3_spite(self):
        """
        Scenario 3: Test Agent B's spiteful vs cooperative behavior.
        B chooses between V3 and V4 while A can only reach one of them.
        """
        config = """
    #N 6
    #D 2
    #V1
    #V2
    #V3 P5
    #V4 P5
    #V5
    #V6 P5
    #E1 1 2 W1
    #E2 2 3 W1
    #E3 3 5 W1
    #E4 4 5 W1
    #E5 4 2 W1
    #E6 3 4 W1
    #E7 4 6 W1
    """
        # D=3: A moves t=0, B moves t=1, A moves t=2
        # A: V1 -> V2 (t=0) -> V3 or V4 (t=2)
        # B: V5 -> V3 or V4 (t=1)
        # B moves BEFORE A's second move, so B picks first!
        
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V5"}
        
        # 1. Test Adversarial (Spiteful)
        # B should block A by taking whichever A is heading toward
        # Since A is closer to V3 (via V2), B takes V3 to block
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Adversarial",
            cutoff=6,
        )
        # Let A move first
        self.assertTrue("V2" in game.agents["A"].act(alpha_beta=True), "Adversarial A advance to v2")
        self.assertTrue("V4" in game.agents["B"].act(alpha_beta=True), "Adversarial B advance to v2")
        game.agents["A"].act(alpha_beta=True)
        self.assertTrue("V6" in game.agents["B"].act(alpha_beta=True), "Adversarial B advance to v2")
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
            "Fully Cooperative",
            cutoff=12,
        )

        self.assertTrue("V2" in game.agents["A"].act(alpha_beta=True), "Adversarial A advance to v2")
        self.assertTrue("V4" in game.agents["B"].act(alpha_beta=True), "Adversarial B advance to 4")
        game.agents["A"].act(alpha_beta=True)
        self.assertTrue("V6" in game.agents["B"].act(alpha_beta=True), "Adversarial B advance to 5")
        game = Game(
            D,
            params,
            vertices_config,
            edges_config,
            agents_config,
           "Semi Cooperative",
            cutoff=12,
        )

        self.assertTrue("V2" in game.agents["A"].act(alpha_beta=True), "Adversarial A advance to v2")
        self.assertTrue("V4" in game.agents["B"].act(alpha_beta=True), "Adversarial B advance to v2")
        game.agents["A"].act(alpha_beta=True)
        self.assertTrue("V6" in game.agents["B"].act(alpha_beta=True), "Adversarial B advance to v2")



class TestBugFixes(unittest.TestCase):
    def test_dropped_kit_retrieval(self):
        config = """
#N 2
#D 20
#U 1
#Q 1
#V1 K
#V2

#E1 1 2 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V1"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )
        state = game.current_state

        # 1. Agent A equips the kit
        succ = state.get_successor_states("A")

        # FIX: Removed [0]. 'next' returns the State object directly from the generator.
        equip_state = next(s for s, a in succ if "equip" in a)

        # 2. Agent A moves to V2
        succ = equip_state.get_successor_states("A")
        move_state = next(s for s, a in succ if "traverse" in a)

        # 3. Agent A Unequips at V2
        succ = move_state.get_successor_states("A")
        drop_state = next(s for s, a in succ if "unequip" in a)

        self.assertTrue(len(drop_state.kits_on_vertices["V2"]) > 0)

        # 4. Verify Agent B can Equip at V2
        locs = drop_state.locations.copy()
        locs["B"] = VertexLocation("V2")
        state_b_at_v2 = State(
            game,
            locs,
            drop_state.saved,
            drop_state.people,
            drop_state.kits_on_vertices,
            drop_state.kits_held,
            drop_state.time,
        )

        succ_b = state_b_at_v2.get_successor_states("B")
        can_equip = any("equip" in a for s, a in succ_b)
        self.assertTrue(can_equip)


class TestBugFixes(unittest.TestCase):
    """Tests for specific bugs that were fixed (Dropped Kits, etc.)"""

    def test_dropped_kit_retrieval(self):
        """
        Test that an agent can drop a kit at a node (even if it had no kit initially)
        and another agent can pick it up.
        """
        config = """
#N 2
#D 20
#U 1
#Q 1
#V1 K
#V2

#E1 1 2 W1
"""
        N, D, params, vertices_config, edges_config = parse_config_string(config)
        agents_config = {"A": "V1", "B": "V1"}
        game = Game(
            D, params, vertices_config, edges_config, agents_config, "Adversarial"
        )
        state = game.current_state

        # 1. Agent A equips the kit
        succ = state.get_successor_states("A")
        equip_state = next(s for s, a in succ if "equip" in a)

        # 2. Agent A moves to V2 (carrying kit)
        succ = equip_state.get_successor_states("A")
        move_state = next(s for s, a in succ if "traverse" in a)

        # 3. Agent A Unequips at V2 (Drops kit)
        # Note: V2 config had NO kit initially. This tests the dynamic update.
        succ = move_state.get_successor_states("A")
        drop_state = next(s for s, a in succ if "unequip" in a)

        # Verify kit is now at V2 in the state
        self.assertTrue(
            len(drop_state.kits_on_vertices["V2"]) > 0,
            "Kit should be available at V2 after drop",
        )

        # 4. Verify Agent B (who walked there) can now Equip at V2
        # (Assuming B followed A to V2)
        # Move B to V2 in the state
        locs = drop_state.locations.copy()
        locs["B"] = VertexLocation("V2")
        state_b_at_v2 = State(
            game,
            locs,
            drop_state.saved,
            drop_state.people,
            drop_state.kits_on_vertices,
            drop_state.kits_held,
            drop_state.time,
        )

        succ_b = state_b_at_v2.get_successor_states("B")
        can_equip = any("equip" in a for s, a in succ_b)
        self.assertTrue(
            can_equip, "Agent B should be able to pick up the dropped kit at V2"
        )


def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestConfigParser,
        TestGraphConstruction,
        TestStateManagement,
        TestTraversalMechanics,
        TestFloodedEdgeMechanics,
        TestGameTactics,
        TestAlphaBetaPruning,
        TestEdgeCases,
        TestComplexScenarios,
        TestPerformance,
        TestDetailedMechanics,
        TestHeuristicLogic,
        TestChainTopology,
        TestTreeTopology,
        TestParserRobustness,
        TestAdvancedFeatures,
        TestReadmeScenarios,  # <--- Add this
        TestBugFixes,  # <--- Add this
    ]

    for tc in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(tc))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    plt.ioff()
    run_tests()
