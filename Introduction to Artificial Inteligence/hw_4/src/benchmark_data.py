example_1 = """
#V 5    ; number of vertices n in graph (from 1 to n)

#E1 1 2 W3       ; Edge from vertex 1 to vertex 2, weight 3
#E2 2 3 W2 F 0.2 ; Edge from vertex 2 to vertex 3, weight 2, probability of flooding 0.2
#E3 3 4 W3 F 0.3 ; Edge from vertex 3 to vertex 4, weight 3, probability of flooding 0.3
#E4 4 5 W1       ; Edge from vertex 4 to vertex 5, weight 1
#E5 2 4 W4       ; Edge from vertex 2 to vertex 4, weight 4
                 ; Can assume that if not given, flooding not possible on that edge
				 
#K1 1            ; Amphibian kit at vertex 1
#EC 2            ; Takes 2 units of time to equip an amphibian kit
#UC 1            ; and 1 unit of time to unequip
#FF 3            ' Movement with amphibian kit is 3 times as slow as without

#Start 1
#Target 5
"""

example_2 = """
#V 6    ; number of vertices n in graph (from 1 to n)

; A more complex graph with multiple paths and higher flood risks
#E1 1 2 W2           ; Edge from vertex 1 to vertex 2, weight 2
#E2 1 3 W4           ; Edge from vertex 1 to vertex 3, weight 4
#E3 2 3 W1 F 0.4     ; Edge from vertex 2 to vertex 3, weight 1, probability of flooding 0.4
#E4 2 4 W3 F 0.5     ; Edge from vertex 2 to vertex 4, weight 3, probability of flooding 0.5
#E5 3 5 W2 F 0.3     ; Edge from vertex 3 to vertex 5, weight 2, probability of flooding 0.3
#E6 4 5 W2           ; Edge from vertex 4 to vertex 5, weight 2
#E7 4 6 W3 F 0.2     ; Edge from vertex 4 to vertex 6, weight 3, probability of flooding 0.2
#E8 5 6 W1           ; Edge from vertex 5 to vertex 6, weight 1

#K1 3                ; Amphibian kit at vertex 3
#EC 3                ; Takes 3 units of time to equip an amphibian kit
#UC 2                ; and 2 units of time to unequip
#FF 2                ; Movement with amphibian kit is 2 times as slow as without

#Start 1
#Target 6
"""

example_3 = """
#V 4    ; Small graph with critical flood decision

#E1 1 2 W1           ; Safe path start
#E2 2 3 W2 F 0.6     ; Risky shortcut with high flood probability
#E3 2 4 W5           ; Safe but long path
#E4 3 4 W1           ; Short path from 3 to target

#K1 1                ; Amphibian kit at start
#EC 2                ; Takes 2 units of time to equip
#UC 1                ; and 1 unit to unequip
#FF 3                ; Movement with kit is 3 times slower

#Start 1
#Target 4
"""

BUILTIN_SCENARIOS = {
    1: {
        "name": "Simple Path",
        "description": "Basic 5-vertex graph with moderate flood risks",
        "config": example_1,
    },
    2: {
        "name": "Complex Network",
        "description": "6-vertex graph with multiple paths and varied flood probabilities",
        "config": example_2,
    },
    3: {
        "name": "Risk vs Safety",
        "description": "Small graph testing risk/reward decisions with kit usage",
        "config": example_3,
    },
}
