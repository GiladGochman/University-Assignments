import sys


class AIGameAgent:
    """AI agent that uses minimax/alpha-beta pruning for decision making."""

    def __init__(self, agent_id, game):
        self.agent_id = agent_id
        self.game = game

    def act(self, alpha_beta: bool) -> str:
        """Execute agent's turn and return action description."""
        if self.game.tactic == "Adversarial":
            best_state, action = self.alpha_beta_minmax_decision(alpha_beta)
        else:
            best_state, action = self.cooperative_decision()

        self.game.current_state = best_state
        return action

    def alpha_beta_minmax_decision(self, alpha_beta: bool = True):
        """Make decision using alpha-beta minimax algorithm."""
        current_state = self.game.current_state
        successors = current_state.get_successor_states(self.agent_id)

        if not successors:
            return current_state, "no-op"

        max_value = -sys.maxsize
        best_state = None
        best_action = None
        evaluated_any = False

        if alpha_beta:
            alpha = -sys.maxsize
            beta = sys.maxsize

        for successor, action in successors:
            if successor.time > self.game.deadline:
                continue

            if alpha_beta:
                current_value = self.min_value(successor, 1, alpha, beta)

                if current_value > max_value or not evaluated_any:
                    max_value = current_value
                    best_state = successor
                    best_action = action
                    evaluated_any = True

                if current_value >= beta:
                    return best_state, best_action

                alpha = max(alpha, current_value)
            else:
                current_value = self.min_value(successor, 1)

                if current_value > max_value or not evaluated_any:
                    max_value = current_value
                    best_state = successor
                    best_action = action
                    evaluated_any = True

        if not evaluated_any:
            if successors:
                best_state = successors[0][0]
                best_action = successors[0][1]
            else:
                return current_state, "no-op"

        return best_state, best_action

    def max_value(self, state, depth: int, alpha: int = None, beta: int = None) -> int:
        """Compute max value in minimax tree."""
        if state.cutoff_test(depth):
            return state.get_heuristic_value(self.agent_id)

        value = -sys.maxsize
        successors = state.get_successor_states(self.agent_id)

        if not successors:
            return state.get_heuristic_value(self.agent_id)

        evaluated_any = False

        for successor, _ in successors:
            if successor.time > self.game.deadline:
                continue

            evaluated_any = True

            if alpha is not None and beta is not None:
                value = max(value, self.min_value(successor, depth + 1, alpha, beta))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            else:
                value = max(value, self.min_value(successor, depth + 1))

        if not evaluated_any:
            return state.get_heuristic_value(self.agent_id)

        return value

    def min_value(self, state, depth: int, alpha: int = None, beta: int = None) -> int:
        """Compute min value in minimax tree."""
        other = self._get_opponent_id()

        if state.cutoff_test(depth):
            return state.get_heuristic_value(self.agent_id)

        value = sys.maxsize
        successors = state.get_successor_states(other)

        if not successors:
            return state.get_heuristic_value(self.agent_id)

        evaluated_any = False

        for successor, _ in successors:
            if successor.time > self.game.deadline:
                continue

            evaluated_any = True

            if alpha is not None and beta is not None:
                value = min(value, self.max_value(successor, depth + 1, alpha, beta))
                if value <= alpha:
                    return value
                beta = min(beta, value)
            else:
                value = min(value, self.max_value(successor, depth + 1))

        if not evaluated_any:
            return state.get_heuristic_value(self.agent_id)

        return value

 
    def _get_opponent_id(self) -> str:
        all_agents = list(self.game.agents.keys())
        for aid in all_agents:
            if aid != self.agent_id:
                return aid
        return self.agent_id

    @staticmethod
    def get_other_player(agent_id: str) -> str:
        return "A" if agent_id == "B" else "B"


    def cooperative_decision(self):
        """Make decision using cooperative strategy."""
        current_state = self.game.current_state
        successors = current_state.get_successor_states(self.agent_id)

        if not successors:
            return current_state, "no-op"

        if self.game.tactic == "Semi Cooperative":
            max_value = (-sys.maxsize, -sys.maxsize)
        else:
            max_value = -sys.maxsize

        best_state = None
        best_action = None
        evaluated_any = False

        for successor, action in successors:
            if successor.time > self.game.deadline:
                continue

            child_value = self.max_cooperative_value(successor, 1, self._get_opponent_id())

            if self.game.tactic == "Semi Cooperative" and isinstance(child_value, tuple):
                potential = (child_value[1], child_value[0])
            else:
                potential = child_value

            if not evaluated_any or potential > max_value:
                max_value = potential
                best_state = successor
                best_action = action
                evaluated_any = True

        if not evaluated_any:
            best_state = successors[0][0]
            best_action = successors[0][1]

        return best_state, best_action

    def max_cooperative_value(self, state, depth: int, current_agent_id: str):
        """Compute max cooperative value with perspective swapping for Semi-Cooperative."""
        
        if state.cutoff_test(depth):
            return state.get_heuristic_value(current_agent_id)  

        next_agent = (
            self._get_opponent_id()
            if current_agent_id == self.agent_id
            else self.agent_id
        )

        if self.game.tactic == "Semi Cooperative":
            value = (-sys.maxsize, -sys.maxsize)
        else:
            value = -sys.maxsize

        successors = state.get_successor_states(current_agent_id)

        if not successors:
            return state.get_heuristic_value(current_agent_id)  

        evaluated_any = False
        for successor, _ in successors:
            if successor.time > self.game.deadline:
                continue

            evaluated_any = True

            child_value = self.max_cooperative_value(successor, depth + 1, next_agent)

            if self.game.tactic == "Semi Cooperative" and isinstance(child_value, tuple):
                current_perspective = (child_value[1], child_value[0])
            else:
                current_perspective = child_value

            value = max(value, current_perspective)

        if not evaluated_any:
            return state.get_heuristic_value(current_agent_id) 

        return value