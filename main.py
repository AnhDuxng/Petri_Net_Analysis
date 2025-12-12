"""
Main entry point for Petri net analysis.

Runs all tasks on a given PNML file:
1. Parse PNML
2. Explicit reachability
3. BDD-based symbolic reachability
4. Deadlock detection
5. Optimization over reachable markings
"""

import argparse
import sys
from pathlib import Path

from pnml_parser import load_petri_net
from explicit_reachability import analyze_explicit_reachability
from symbolic_reachability import analyze_symbolic_reachability
from deadlock_detection import detect_deadlock, DeadlockDetector
from reachable_optimization import optimize_reachable, ReachableOptimizer


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_all_tasks(pnml_file: str, weights: list = None):
    """Run all analysis tasks on a Petri net."""
    
    print_header("PETRI NET ANALYSIS")
    print(f"Input file: {pnml_file}\n")
    
    # Task 1: Parse PNML
    print("[Task 1] Parsing PNML file...")
    try:
        petri_net = load_petri_net(pnml_file)
        print(f"✓ Successfully parsed Petri net")
        print(f"  - Places: {len(petri_net.places)}")
        print(f"  - Transitions: {len(petri_net.transitions)}")
        print(f"  - Arcs: {len(petri_net.arcs)}")
        print(f"  - Initial marking: {petri_net.get_initial_marking()}")
    except Exception as e:
        print(f"✗ Error parsing PNML: {e}")
        return
    
    # Task 2: Explicit reachability
    print_header("Task 2: Explicit Reachability Analysis")
    explicit_analyzer = None
    try:
        explicit_analyzer = analyze_explicit_reachability(petri_net, method='bfs')
        stats = explicit_analyzer.get_statistics()
        print(f"✓ Explicit reachability computed")
        print(f"  - Reachable markings: {stats['num_reachable']}")
        print(f"  - Computation time: {stats['time_seconds']:.4f} seconds")
        print(f"  - Memory usage: ~{stats['memory_bytes'] / 1024:.2f} KB")
        
        # Print first few markings
        if stats['num_reachable'] <= 50:
            explicit_analyzer.print_reachable_markings(limit=20)
    except RuntimeError as e:
        print(f"⚠ {e}")
        print(f"  Skipping explicit analysis for this unbounded net...")
    except Exception as e:
        print(f"✗ Error in explicit reachability: {e}")
        import traceback
        traceback.print_exc()
    
    # Task 3: BDD-based symbolic reachability
    print_header("Task 3: BDD-based Symbolic Reachability")
    symbolic_analyzer = None
    try:
        symbolic_analyzer = analyze_symbolic_reachability(petri_net)
        stats = symbolic_analyzer.get_statistics()
        print(f"✓ Symbolic reachability computed")
        print(f"  - Reachable markings: {stats['num_reachable']}")
        print(f"  - Computation time: {stats['time_seconds']:.4f} seconds")
        print(f"  - BDD representation size: {stats['bdd_nodes']} (approx)")
        
        # Compare with explicit
        if explicit_analyzer is not None:
            explicit_stats = explicit_analyzer.get_statistics()
            if stats['time_seconds'] > 0:
                speedup = explicit_stats['time_seconds'] / stats['time_seconds']
                print(f"\n  Comparison with explicit approach:")
                print(f"  - Speedup: {speedup:.2f}x")
            else:
                print(f"\n  Comparison with explicit approach:")
                print(f"  - Speedup: N/A (symbolic was too fast to measure)")
            print(f"  - Same number of markings: {stats['num_reachable'] == explicit_stats['num_reachable']}")
    except RuntimeError as e:
        print(f"⚠ {e}")
        print(f"  Skipping symbolic analysis for this unbounded net...")
        print_header("Analysis Complete (Partial - Unbounded Net)")
        return
    except Exception as e:
        print(f"✗ Error in symbolic reachability: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Task 4: Deadlock detection
    print_header("Task 4: Deadlock Detection (BDD-based)")
    try:
        detector = DeadlockDetector(petri_net, symbolic_analyzer)
        deadlock = detector.detect_deadlock_ilp_direct()
        stats = detector.get_statistics()
        
        if deadlock:
            print(f"✓ Deadlock found!")
            print(f"  - Deadlock marking: {deadlock}")
            
            # Show which places have tokens
            place_ids = sorted(petri_net.places.keys())
            print(f"  - Places with tokens: {[place_ids[i] for i, val in enumerate(deadlock) if val == 1]}")
        else:
            print(f"✓ No deadlock found (system is deadlock-free)")
        
        print(f"  - Computation time: {stats['time_seconds']:.4f} seconds")
    except Exception as e:
        print(f"✗ Error in deadlock detection: {e}")
        import traceback
        traceback.print_exc()
    
    # Task 5: Optimization
    if weights:
        print_header("Task 5: Optimization over Reachable Markings")
        try:
            if len(weights) != len(petri_net.places):
                print(f"✗ Weight vector length ({len(weights)}) doesn't match "
                      f"number of places ({len(petri_net.places)})")
            else:
                optimizer = ReachableOptimizer(petri_net, symbolic_analyzer)
                optimal = optimizer.optimize(weights, maximize=True)
                stats = optimizer.get_statistics()
                
                if optimal:
                    print(f"✓ Optimal marking found!")
                    print(f"  - Optimal marking: {optimal}")
                    print(f"  - Objective value: {stats['optimal_value']:.2f}")
                    
                    # Show breakdown
                    place_ids = sorted(petri_net.places.keys())
                    print(f"  - Breakdown:")
                    for i, (w, m) in enumerate(zip(weights, optimal)):
                        if m > 0:
                            print(f"    {place_ids[i]}: weight={w}, tokens={m}, contrib={w*m}")
                else:
                    print(f"✗ No optimal marking found")
                
                print(f"  - Computation time: {stats['time_seconds']:.4f} seconds")
        except Exception as e:
            print(f"✗ Error in optimization: {e}")
            import traceback
            traceback.print_exc()
    
    print_header("Analysis Complete")


def main():
    parser = argparse.ArgumentParser(
        description="Petri Net Analysis with BDD and ILP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py examples/simple.pnml
  python main.py examples/simple.pnml --task explicit
  python main.py examples/simple.pnml --task optimize --weights "1,2,1,0,1"
        """
    )
    
    parser.add_argument('pnml_file', type=str, 
                       help='Path to PNML file')
    parser.add_argument('--task', type=str, choices=['all', 'explicit', 'bdd', 'deadlock', 'optimize'],
                       default='all', help='Specific task to run (default: all)')
    parser.add_argument('--weights', type=str,
                       help='Comma-separated weights for optimization (e.g., "1,2,1,0,1")')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.pnml_file).exists():
        print(f"Error: File '{args.pnml_file}' not found")
        sys.exit(1)
    
    # Parse weights if provided
    weights = None
    if args.weights:
        try:
            weights = [float(w.strip()) for w in args.weights.split(',')]
        except ValueError:
            print(f"Error: Invalid weight format. Use comma-separated numbers.")
            sys.exit(1)
    
    # Run analysis
    if args.task == 'all':
        run_all_tasks(args.pnml_file, weights)
    else:
        # Run specific task
        petri_net = load_petri_net(args.pnml_file)
        
        if args.task == 'explicit':
            analyzer = analyze_explicit_reachability(petri_net)
            print(analyzer.get_statistics())
        elif args.task == 'bdd':
            analyzer = analyze_symbolic_reachability(petri_net)
            print(analyzer.get_statistics())
        elif args.task == 'deadlock':
            symbolic_analyzer = analyze_symbolic_reachability(petri_net)
            deadlock = detect_deadlock(petri_net, symbolic_analyzer)
            print(f"Deadlock: {deadlock}")
        elif args.task == 'optimize':
            if not weights:
                print("Error: --weights required for optimization task")
                sys.exit(1)
            symbolic_analyzer = analyze_symbolic_reachability(petri_net)
            optimal = optimize_reachable(petri_net, symbolic_analyzer, weights)
            print(f"Optimal marking: {optimal}")


if __name__ == '__main__':
    main()

