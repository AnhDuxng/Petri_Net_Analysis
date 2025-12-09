"""
Reachable Optimization - Task 5

Optimizes a linear objective function over reachable markings.

Problem: maximize c^T * M, where M in Reach(M0)

Approach:
1. Get reachable markings from BDD
2. Find optimal marking by evaluating objective
"""

import time
from typing import Optional, Tuple, List
from petri_net import PetriNet
from symbolic_reachability import SymbolicReachabilityAnalyzer


class ReachableOptimizer:
    """
    Optimizes a linear objective function over reachable markings.
    """
    
    def __init__(self, petri_net: PetriNet, reachability_analyzer: SymbolicReachabilityAnalyzer):
        self.petri_net = petri_net
        self.reachability_analyzer = reachability_analyzer
        self.computation_time: float = 0.0
        self.optimal_marking: Optional[Tuple[int, ...]] = None
        self.optimal_value: Optional[float] = None
        
    def optimize(self, weights: List[float], maximize: bool = True) -> Optional[Tuple[int, ...]]:
        """
        Optimize a linear objective function over reachable markings.
        
        Args:
            weights: List of weights for each place (objective coefficients)
            maximize: If True, maximize; if False, minimize
            
        Returns:
            Optimal marking if found, None if problem is infeasible
        """
        start_time = time.time()
        
        if len(weights) != len(self.petri_net.places):
            raise ValueError(f"Weight vector length ({len(weights)}) must match "
                           f"number of places ({len(self.petri_net.places)})")
        
        # Get all reachable markings
        reachable_markings = self.reachability_analyzer.extract_markings_from_bdd()
        
        if not reachable_markings:
            self.computation_time = time.time() - start_time
            return None
        
        # Simple approach: evaluate objective for each marking
        best_marking = None
        best_value = float('-inf') if maximize else float('inf')
        
        for marking in reachable_markings:
            value = sum(w * m for w, m in zip(weights, marking))
            
            if maximize and value > best_value:
                best_value = value
                best_marking = marking
            elif not maximize and value < best_value:
                best_value = value
                best_marking = marking
        
        self.optimal_marking = best_marking
        self.optimal_value = best_value
        self.computation_time = time.time() - start_time
        
        return best_marking
    
    def get_statistics(self) -> dict:
        """Return statistics about the optimization."""
        return {
            'optimal_found': self.optimal_marking is not None,
            'optimal_marking': self.optimal_marking,
            'optimal_value': self.optimal_value,
            'time_seconds': self.computation_time
        }


def optimize_reachable(petri_net: PetriNet, 
                       reachability_analyzer: SymbolicReachabilityAnalyzer,
                       weights: List[float],
                       maximize: bool = True) -> Optional[Tuple[int, ...]]:
    """
    Convenience function to optimize over reachable markings.
    
    Args:
        petri_net: The Petri net to analyze
        reachability_analyzer: Pre-computed reachability analyzer with BDD
        weights: Objective coefficients for each place
        maximize: If True, maximize; if False, minimize
        
    Returns:
        Optimal marking if found, None otherwise
    """
    optimizer = ReachableOptimizer(petri_net, reachability_analyzer)
    return optimizer.optimize(weights, maximize)

