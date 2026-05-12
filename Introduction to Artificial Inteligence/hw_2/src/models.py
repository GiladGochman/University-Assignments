"""Core data structures for Hurricane Evacuation problem."""


class AgentLocation:
    """Base class for agent location."""

    pass


class VertexLocation(AgentLocation):
    """Agent is at a vertex."""

    def __init__(self, v_id):
        self.v_id = v_id

    def __str__(self):
        return f"At vertex {self.v_id}"

    def __eq__(self, other):
        return isinstance(other, VertexLocation) and self.v_id == other.v_id

    def __hash__(self):
        return hash(("vertex", self.v_id))


class EdgeLocation(AgentLocation):
    """Agent is traversing an edge."""

    def __init__(self, e_id, origin_v_id, destination_v_id, units: int):
        self.e_id = e_id
        self.origin_v_id = origin_v_id
        self.destination_v_id = destination_v_id
        self.units = units

    def __str__(self):
        return f"Traversing {self.e_id} to {self.destination_v_id} ({self.units} units left)"

    def __eq__(self, other):
        return (
            isinstance(other, EdgeLocation)
            and self.e_id == other.e_id
            and self.destination_v_id == other.destination_v_id
            and self.units == other.units
        )

    def __hash__(self):
        return hash(("edge", self.e_id, self.destination_v_id, self.units))


class EquippingLocation(AgentLocation):
    """Agent is equipping an amphibian kit."""

    def __init__(self, v_id, units: int, kit_id: str):
        self.v_id = v_id
        self.units = units
        self.kit_id = kit_id

    def __str__(self):
        return f"Equipping kit {self.kit_id} at {self.v_id} ({self.units} units left)"

    def __eq__(self, other):
        return (
            isinstance(other, EquippingLocation)
            and self.v_id == other.v_id
            and self.units == other.units
            and self.kit_id == other.kit_id
        )

    def __hash__(self):
        return hash(("equipping", self.v_id, self.units, self.kit_id))


class UnequippingLocation(AgentLocation):
    """Agent is unequipping an amphibian kit."""

    def __init__(self, v_id, units: int, kit_id: str):
        self.v_id = v_id
        self.units = units
        self.kit_id = kit_id

    def __str__(self):
        return f"Unequipping kit {self.kit_id} at {self.v_id} ({self.units} units left)"

    def __eq__(self, other):
        return (
            isinstance(other, UnequippingLocation)
            and self.v_id == other.v_id
            and self.units == other.units
            and self.kit_id == other.kit_id
        )

    def __hash__(self):
        return hash(("unequipping", self.v_id, self.units, self.kit_id))
