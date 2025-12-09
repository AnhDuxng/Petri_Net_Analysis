"""
Core Petri Net data structures.

A Petri net consists of:
- Places (P): Conditions or states
- Transitions (T): Events or actions
- Flow relations (F): Arcs connecting places to transitions and vice versa
- Initial marking (M0): Initial distribution of tokens

For 1-safe Petri nets, each place can hold at most 1 token.
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class Place:
    """Represents a place in a Petri net."""
    id: str
    name: str = ""
    initial_tokens: int = 0
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, Place) and self.id == other.id
    
    def __repr__(self):
        return f"Place({self.id}, tokens={self.initial_tokens})"


@dataclass
class Transition:
    """Represents a transition in a Petri net."""
    id: str
    name: str = ""
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, Transition) and self.id == other.id
    
    def __repr__(self):
        return f"Transition({self.id})"


@dataclass
class Arc:
    """Represents an arc (flow relation) in a Petri net."""
    source: str  # ID of source node (place or transition)
    target: str  # ID of target node (place or transition)
    weight: int = 1
    
    def __repr__(self):
        return f"Arc({self.source} -> {self.target}, weight={self.weight})"


class PetriNet:
    """
    Represents a Petri net with places, transitions, and arcs.
    Supports 1-safe Petri nets (places hold at most 1 token).
    """
    
    def __init__(self):
        self.places: Dict[str, Place] = {}
        self.transitions: Dict[str, Transition] = {}
        self.arcs: List[Arc] = []
        
        # Precomputed structures for efficient transition firing
        self._input_places: Dict[str, Set[str]] = {}  # transition_id -> set of input place IDs
        self._output_places: Dict[str, Set[str]] = {}  # transition_id -> set of output place IDs
        self._place_index: Dict[str, int] = {}  # place_id -> index in marking vector
        self._transition_index: Dict[str, int] = {}  # transition_id -> index
        
    def add_place(self, place: Place):
        """Add a place to the Petri net."""
        self.places[place.id] = place
        
    def add_transition(self, transition: Transition):
        """Add a transition to the Petri net."""
        self.transitions[transition.id] = transition
        self._input_places[transition.id] = set()
        self._output_places[transition.id] = set()
        
    def add_arc(self, arc: Arc):
        """Add an arc to the Petri net."""
        self.arcs.append(arc)
        
        # Update input/output place mappings
        if arc.source in self.places and arc.target in self.transitions:
            # Place -> Transition (input arc)
            self._input_places[arc.target].add(arc.source)
        elif arc.source in self.transitions and arc.target in self.places:
            # Transition -> Place (output arc)
            self._output_places[arc.source].add(arc.target)
            
    def build_indices(self):
        """Build index mappings for efficient operations."""
        self._place_index = {pid: idx for idx, pid in enumerate(sorted(self.places.keys()))}
        self._transition_index = {tid: idx for idx, tid in enumerate(sorted(self.transitions.keys()))}
        
    def get_initial_marking(self) -> Tuple[int, ...]:
        """
        Return the initial marking as a tuple of integers.
        The marking is ordered by place IDs (sorted).
        """
        if not self._place_index:
            self.build_indices()
        
        marking = [0] * len(self.places)
        for place_id, place in self.places.items():
            idx = self._place_index[place_id]
            marking[idx] = place.initial_tokens
        return tuple(marking)
    
    def get_place_id_by_index(self, index: int) -> str:
        """Get place ID by its index in the marking vector."""
        for pid, idx in self._place_index.items():
            if idx == index:
                return pid
        raise ValueError(f"No place with index {index}")
    
    def is_enabled(self, transition_id: str, marking: Tuple[int, ...]) -> bool:
        """
        Check if a transition is enabled in the given marking.
        A transition is enabled if all its input places have sufficient tokens.
        """
        for place_id in self._input_places[transition_id]:
            idx = self._place_index[place_id]
            if marking[idx] < 1:  # For 1-safe nets, we need exactly 1 token
                return False
        return True
    
    def fire_transition(self, transition_id: str, marking: Tuple[int, ...]) -> Tuple[int, ...]:
        """
        Fire a transition and return the new marking.
        Assumes the transition is enabled.
        """
        new_marking = list(marking)
        
        # Remove tokens from input places
        for place_id in self._input_places[transition_id]:
            idx = self._place_index[place_id]
            new_marking[idx] -= 1
            
        # Add tokens to output places
        for place_id in self._output_places[transition_id]:
            idx = self._place_index[place_id]
            new_marking[idx] += 1
            
        return tuple(new_marking)
    
    def get_enabled_transitions(self, marking: Tuple[int, ...]) -> List[str]:
        """Return list of enabled transition IDs for the given marking."""
        enabled = []
        for tid in self.transitions.keys():
            if self.is_enabled(tid, marking):
                enabled.append(tid)
        return enabled
    
    def __repr__(self):
        return (f"PetriNet(places={len(self.places)}, "
                f"transitions={len(self.transitions)}, "
                f"arcs={len(self.arcs)})")

