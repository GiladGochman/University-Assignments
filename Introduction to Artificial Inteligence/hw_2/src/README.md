### Heuristic Explanation

The heuristic estimates the value of a game state by combining  the number of people saved  and proximity to the remaining people(calculated using a Minimum Spanning Tree or MST).

1.  **Core Components**
    * **People Saved:** Counts how many people each agent has secured.
    * **MST Distance:** Uses Prim's algorithm to calculate the "cost" (distance) to reach all remaining people from an agent's current location.
        * *Optimistic Assumption:* It treats flooded edges as normal (weight 1) to ensure the heuristic remains optimistic (admissible).

2.  **Strategy-Specific Logic**
    The components are combined differently depending on the chosen tactic:

    * **Adversarial:**
        * **Formula:** `(My Saved - Opponent Saved) + (Opponent MST Cost - My MST Cost)`
        * **Goal:** Maximizes the winning gap. It rewards having a higher score than the opponent and being positioned closer to the remaining people than they are.

    * **Fully Cooperative:**
        * **Formula:** `(My Saved + Opponent Saved) - min(My MST Cost, Opponent MST Cost)`
        * **Goal:** Maximizes the *team* score. It penalizes the state only based on the *closest* agent to the people, encouraging efficient division of labor (one agent can be far away if the other is close).

    * **Semi-Cooperative:**
        * **Formula:** `(My Saved + Position Bonus, Opponent Saved)`
        * **Goal:** Prioritizes my own score (with a position bonus). If two moves yield the same personal score, it breaks the tie by choosing the one that results in a higher score for the opponent.