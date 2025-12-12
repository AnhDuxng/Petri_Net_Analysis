# Petri Net Analysis with BDD and ILP

This project implements symbolic and algebraic reasoning for analyzing 1-safe Petri nets using Binary Decision Diagrams (BDDs) and Integer Linear Programming (ILP).

## Requirements

- Python 3.8 or higher
- See `requirements.txt` for dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Project Structure

```
.
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── petri_net.py            # Core Petri net data structures
├── pnml_parser.py          # PNML file parser (Task 1)
├── explicit_reachability.py # BFS/DFS reachability (Task 2)
├── symbolic_reachability.py # BDD-based reachability (Task 3)
├── deadlock_detection.py    # ILP+BDD deadlock detection (Task 4)
├── reachable_optimization.py # ILP optimization (Task 5)
├── main.py                  # Main entry point
└── examples/                # Example PNML files
    ├── simple.pnml
    ├── producer_consumer.pnml
    └── dining_philosophers.pnml
```

## Usage

Run all analysis on a Petri net:

```bash
python main.py examples/simple.pnml
```

Run specific tasks:

```bash
# Task 2: Explicit reachability only
python main.py examples/simple.pnml --task explicit

# Task 3: BDD-based reachability only
python main.py examples/simple.pnml --task bdd

# Task 4: Deadlock detection
python main.py examples/simple.pnml --task deadlock

# Task 5: Optimization (requires weights)
python main.py examples/simple.pnml --task optimize --weights "1,2,1,0,1"
```

## Example Output

```
=== Petri Net Analysis ===
Places: 5
Transitions: 4

[Task 2] Explicit Reachability:
- Reachable markings: 12
- Time: 0.003s

[Task 3] BDD-based Reachability:
- Reachable markings: 12
- BDD nodes: 45
- Time: 0.001s

[Task 4] Deadlock Detection:
- Deadlock found: [1, 0, 1, 0, 0]
- Time: 0.005s

[Task 5] Optimization:
- Optimal marking: [0, 1, 1, 0, 1]
- Objective value: 5
- Time: 0.008s
```


