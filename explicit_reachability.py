"""
Explicit Reachability Analysis - Task 2

Implements breadth-first search (BFS) and depth-first search (DFS) algorithms
to enumerate all reachable markings from the initial marking.

This serves as a baseline for comparison with the symbolic BDD-based approach.
"""

import time
from collections import deque
from typing import Set, Tuple, List
from petri_net import PetriNet


class ExplicitReachabilityAnalyzer:
    """
    Computes reachable markings using explicit state enumeration.
    Uses BFS by default for systematic exploration.
    """
    
    def __init__(self, petri_net: PetriNet):
        self.petri_net = petri_net
        self.reachable_markings: Set[Tuple[int, ...]] = set()
        self.computation_time: float = 0.0
        
    def compute_reachable_markings_bfs(self, max_states: int = 10000) -> Set[Tuple[int, ...]]:
        """
        Compute all reachable markings using BFS.
        
        Args:
            max_states: Maximum states to explore (prevents infinite loops on unbounded nets)
        
        Returns:
            Set of reachable markings (each marking is a tuple of integers)
        
        Raises:
            RuntimeError: If max_states exceeded (likely unbounded net)
        """
        start_time = time.time()
        
        initial_marking = self.petri_net.get_initial_marking()
        self.reachable_markings = {initial_marking}
        queue = deque([initial_marking])
        
        while queue:
            current_marking = queue.popleft()
            
            # Try to fire each transition
            for transition_id in self.petri_net.transitions.keys():
                if self.petri_net.is_enabled(transition_id, current_marking):
                    new_marking = self.petri_net.fire_transition(transition_id, current_marking)
                    
                    if new_marking not in self.reachable_markings:
                        self.reachable_markings.add(new_marking)
                        queue.append(new_marking)
                        
                        # Check limit to prevent infinite loops
                        if len(self.reachable_markings) > max_states:
                            self.computation_time = time.time() - start_time
                            raise RuntimeError(
                                f"State limit exceeded ({max_states}). "
                                f"Net appears unbounded (infinite state space)."
                            )
        
        self.computation_time = time.time() - start_time
        return self.reachable_markings
    
    def compute_reachable_markings_dfs(self) -> Set[Tuple[int, ...]]:
        """
        Compute all reachable markings using DFS.
        
        Returns:
            Set of reachable markings (each marking is a tuple of integers)
        """
        start_time = time.time()
        
        initial_marking = self.petri_net.get_initial_marking()
        self.reachable_markings = set()
        
        def dfs(marking: Tuple[int, ...]):
            if marking in self.reachable_markings:
                return
            
            self.reachable_markings.add(marking)
            
            # Try to fire each transition
            for transition_id in self.petri_net.transitions.keys():
                if self.petri_net.is_enabled(transition_id, marking):
                    new_marking = self.petri_net.fire_transition(transition_id, marking)
                    dfs(new_marking)
        
        dfs(initial_marking)
        self.computation_time = time.time() - start_time
        return self.reachable_markings
    
    def get_statistics(self) -> dict:
        """Return statistics about the reachability analysis."""
        return {
            'num_reachable': len(self.reachable_markings),
            'time_seconds': self.computation_time,
            'memory_bytes': len(self.reachable_markings) * len(self.petri_net.places) * 8  # Rough estimate
        }
    
    def print_reachable_markings(self, limit: int = 20):
        """Print reachable markings (up to limit)."""
        print(f"\nReachable markings ({len(self.reachable_markings)} total):")
        
        place_ids = sorted(self.petri_net.places.keys())
        print(f"  {'Marking':<8} | {' '.join(f'{pid:>5}' for pid in place_ids)}")
        print("  " + "-" * (10 + 6 * len(place_ids)))
        
        for i, marking in enumerate(sorted(self.reachable_markings)):
            if i >= limit:
                print(f"  ... ({len(self.reachable_markings) - limit} more)")
                break
            marking_str = ' '.join(f'{val:>5}' for val in marking)
            print(f"  M{i:<7} | {marking_str}")


def analyze_explicit_reachability(petri_net: PetriNet, method: str = 'bfs') -> ExplicitReachabilityAnalyzer:
    """
    Convenience function to perform explicit reachability analysis.
    
    Args:
        petri_net: The Petri net to analyze
        method: 'bfs' or 'dfs'
        
    Returns:
        ExplicitReachabilityAnalyzer with computed results
    """
    analyzer = ExplicitReachabilityAnalyzer(petri_net)
    
    if method.lower() == 'bfs':
        analyzer.compute_reachable_markings_bfs()
    elif method.lower() == 'dfs':
        analyzer.compute_reachable_markings_dfs()
    else:
        raise ValueError(f"Unknown method: {method}. Use 'bfs' or 'dfs'.")
    
    return analyzer

