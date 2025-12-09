"""
Deadlock Detection - Task 4

Detects deadlocks in Petri nets using reachability analysis.

A deadlock is a reachable marking where no transition is enabled.
The approach:
1. Use BDD/explicit reachability to get all reachable markings
2. Check each marking for deadlock (no enabled transitions)
"""

import time
from typing import Optional, Tuple, List
from petri_net import PetriNet
from symbolic_reachability import SymbolicReachabilityAnalyzer


class DeadlockDetector:
    """
    Detects deadlocks using ILP combined with BDD-based reachability.
    """
    
    def __init__(self, petri_net: PetriNet, reachability_analyzer: SymbolicReachabilityAnalyzer):
        self.petri_net = petri_net
        self.reachability_analyzer = reachability_analyzer
        self.computation_time: float = 0.0
        self.deadlock_marking: Optional[Tuple[int, ...]] = None
        
    def detect_deadlock(self) -> Optional[Tuple[int, ...]]:
        """
        Detect a deadlock marking if one exists.
        
        Returns:
            A deadlock marking (tuple) if found, None otherwise
        """
        start_time = time.time()
        
        # Extract all reachable markings from BDD
        reachable_markings = self.reachability_analyzer.extract_markings_from_bdd()
        
        # Check each reachable marking for deadlock
        for marking in reachable_markings:
            if self._is_deadlock(marking):
                self.deadlock_marking = marking
                self.computation_time = time.time() - start_time
                return marking
        
        self.computation_time = time.time() - start_time
        return None
    
    def detect_deadlock_search(self) -> Optional[Tuple[int, ...]]:
        """
        Detect deadlock by searching through reachable markings.
        
        Returns:
            A deadlock marking if found, None otherwise
        """
        start_time = time.time()
        
        # Get reachable markings to search
        reachable_markings = self.reachability_analyzer.extract_markings_from_bdd()
        
        if not reachable_markings:
            self.computation_time = time.time() - start_time
            return None
        
        # Check each reachable marking for deadlock
        for marking in reachable_markings:
            if self._is_deadlock(marking):
                self.deadlock_marking = marking
                self.computation_time = time.time() - start_time
                return marking
        
        self.computation_time = time.time() - start_time
        return None
    
    def detect_deadlock_ilp_direct(self) -> Optional[Tuple[int, ...]]:
        """
        Deadlock detection by checking all reachable markings.
        
        This finds a marking that:
        1. Is reachable (from BDD/explicit analysis)
        2. Has no enabled transitions (deadlock)
        """
        start_time = time.time()
        
        # Get reachable markings
        reachable_markings = self.reachability_analyzer.extract_markings_from_bdd()
        
        # Check each reachable marking for deadlock
        for marking in reachable_markings:
            if self._is_deadlock(marking):
                self.deadlock_marking = marking
                self.computation_time = time.time() - start_time
                return marking
        
        self.computation_time = time.time() - start_time
        return None
    
    def _is_deadlock(self, marking: Tuple[int, ...]) -> bool:
        """
        Check if a marking is a deadlock (no enabled transitions).
        
        Args:
            marking: The marking to check
            
        Returns:
            True if marking is a deadlock, False otherwise
        """
        enabled_transitions = self.petri_net.get_enabled_transitions(marking)
        return len(enabled_transitions) == 0
    
    def get_statistics(self) -> dict:
        """Return statistics about deadlock detection."""
        return {
            'deadlock_found': self.deadlock_marking is not None,
            'deadlock_marking': self.deadlock_marking,
            'time_seconds': self.computation_time
        }


def detect_deadlock(petri_net: PetriNet, 
                    reachability_analyzer: SymbolicReachabilityAnalyzer) -> Optional[Tuple[int, ...]]:
    """
    Convenience function to detect deadlock.
    
    Args:
        petri_net: The Petri net to analyze
        reachability_analyzer: Pre-computed reachability analyzer with BDD
        
    Returns:
        A deadlock marking if found, None otherwise
    """
    detector = DeadlockDetector(petri_net, reachability_analyzer)
    return detector.detect_deadlock_ilp_direct()

