# Report Template for CO2011 Assignment

This template provides a structure for your report (Task 6: Report Quality - 10%)

---

# Symbolic and Algebraic Reasoning in Petri Nets
## Assignment Report

**Group Members:**
- Student ID 1 - Name 1
- Student ID 2 - Name 2
- Student ID 3 - Name 3
- ...

**Course:** CO2011 - Mathematical Modeling  
**Date:** December 2025

---

## Abstract

[Brief summary of what was implemented, key findings, and results. Max 200 words.]

Example:
> This report presents an implementation of Petri net analysis combining explicit state enumeration, Binary Decision Diagrams (BDDs), and Integer Linear Programming (ILP). We implemented a complete tool that parses PNML files, computes reachable markings both explicitly and symbolically, detects deadlocks, and optimizes linear objectives over reachable states. Our experiments on several example Petri nets demonstrate that...

---

## 1. Introduction

### 1.1 Background

[Introduce Petri nets, their importance, and the motivation for using symbolic methods]

Key points to cover:
- What are Petri nets and why are they important?
- The state space explosion problem
- Why use BDDs and ILP?

### 1.2 Problem Statement

[Clearly state the assignment objectives - the 5 tasks]

### 1.3 Our Approach

[High-level overview of your solution]

---

## 2. Theoretical Background

### 2.1 Petri Nets

#### 2.1.1 Formal Definition

A Petri net is a 4-tuple N = (P, T, F, M₀) where:
- P is a finite set of places
- T is a finite set of transitions
- F ⊆ (P × T) ∪ (T × P) is the flow relation
- M₀: P → ℕ is the initial marking

#### 2.1.2 1-Safe Petri Nets

[Define 1-safe property and its implications]

A Petri net is 1-safe if for all reachable markings M, M(p) ≤ 1 for all places p.

**Key property:** For 1-safe nets with n places, there are at most 2ⁿ reachable markings.

### 2.2 Binary Decision Diagrams (BDDs)

[Explain BDDs - what they are, why they're useful]

Key concepts:
- Reduced ordered BDDs (ROBDDs)
- Shannon expansion
- Canonical representation
- Operations: AND, OR, NOT, RESTRICT

### 2.3 Integer Linear Programming (ILP)

[Explain ILP formulation]

Standard form:
```
maximize    c^T x
subject to  Ax ≤ b
            x ∈ ℤⁿ
```

### 2.4 Reachability Analysis

#### 2.4.1 Explicit Methods

[Describe BFS/DFS algorithms]

#### 2.4.2 Symbolic Methods

[Describe symbolic reachability using BDDs]

Fixed-point computation:
```
R₀ = {M₀}
Rᵢ₊₁ = Rᵢ ∪ Image(Rᵢ, Trans)
```

### 2.5 Deadlock Detection

[Define deadlocks and detection methods]

**Definition:** A deadlock is a reachable marking M where no transition is enabled.

---

## 3. Implementation

### 3.1 System Architecture

[Diagram or description of module structure]

```
┌─────────────────┐
│   main.py       │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┬────────────┐
    │         │         │          │            │
┌───▼──┐  ┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌────▼────┐
│PNML  │  │Expl.│  │Symbol.│  │Dead.  │  │Optim.   │
│Parser│  │Reach│  │Reach  │  │Detect │  │         │
└──────┘  └─────┘  └───────┘  └───────┘  └─────────┘
     │
     ▼
┌─────────┐
│PetriNet │
└─────────┘
```

### 3.2 Task 1: PNML Parser

#### 3.2.1 Design Decisions

[Explain parsing approach, library choices (lxml), etc.]

#### 3.2.2 Implementation Details

**Key functions:**
- `parse_file()`: Main parsing function
- `_parse_place()`: Extract place information
- `_parse_transition()`: Extract transition information
- `_parse_arc()`: Extract flow relations

#### 3.2.3 Validation

[Describe validation checks implemented]
- Check for missing nodes
- Ensure arcs connect places to transitions or vice versa
- Validate arc weights

**Code snippet:**
```python
def _validate_petri_net(petri_net: PetriNet):
    place_ids = set(petri_net.places.keys())
    transition_ids = set(petri_net.transitions.keys())
    # ... validation logic ...
```

### 3.3 Task 2: Explicit Reachability

#### 3.3.1 Algorithm

[Describe BFS algorithm for explicit reachability]

**Pseudocode:**
```
Algorithm: ExplicitReachability(N, M₀)
  Input: Petri net N, initial marking M₀
  Output: Set R of reachable markings

  R ← {M₀}
  Q ← Queue containing M₀
  
  while Q is not empty:
    M ← Q.dequeue()
    for each transition t:
      if t is enabled in M:
        M' ← fire(t, M)
        if M' ∉ R:
          R ← R ∪ {M'}
          Q.enqueue(M')
  
  return R
```

#### 3.3.2 Data Structures

[Explain how markings are represented, how sets are maintained, etc.]

**Marking representation:** Tuples of integers, e.g., (1, 0, 1, 0)

**Why tuples?**
- Immutable (can be used in sets)
- Hashable (efficient lookup)
- Memory efficient

#### 3.3.3 Complexity Analysis

**Time complexity:** O(|R| × |T|)
- |R| = number of reachable markings
- |T| = number of transitions

**Space complexity:** O(|R| × |P|)
- |P| = number of places

### 3.4 Task 3: Symbolic Reachability with BDD

#### 3.4.1 BDD Encoding

[Explain how markings are encoded as boolean formulas]

**Encoding scheme:**
- For n places, use n boolean variables x₀, x₁, ..., xₙ₋₁
- Marking M = (m₀, m₁, ..., mₙ₋₁) is encoded as: x₀^m₀ ∧ x₁^m₁ ∧ ... ∧ xₙ₋₁^mₙ₋₁
- Where xᵢ^0 means ¬xᵢ and xᵢ^1 means xᵢ

**Example:**
- Marking (1, 0, 1) → x₀ ∧ ¬x₁ ∧ x₂

#### 3.4.2 BDD Construction

[Explain the approach used]

**Our approach:** Hybrid method
1. Use explicit BFS to enumerate reachable markings
2. Encode each marking as a BDD formula
3. Combine using BDD disjunction (OR)

**Alternative:** Pure symbolic (more complex)
- Would encode transition relation as BDD
- Use BDD image computation
- Iterate until fixed point

#### 3.4.3 BDD Library: PyEDA

[Justify library choice]

**Why PyEDA?**
- Pure Python implementation
- Easy to install and use
- Sufficient for academic purposes
- Good documentation

**Alternatives:**
- CUDD (faster, but C library)
- BuDDy (C++ library)

#### 3.4.4 Extracting Markings from BDD

[Explain the extraction process]

```python
def extract_markings_from_bdd(self) -> Set[Tuple[int, ...]]:
    markings = set()
    for solution in self.reachable_bdd.satisfy_all():
        marking = [solution.get(self.x[j], 0) for j in range(self.num_places)]
        markings.add(tuple(marking))
    return markings
```

### 3.5 Task 4: Deadlock Detection

#### 3.5.1 Approach

[Explain the combined BDD + checking approach]

**Algorithm:**
1. Extract all reachable markings from BDD (using Task 3)
2. For each marking M:
   - Check if any transition is enabled
   - If no transition enabled, M is a deadlock
3. Return first deadlock found (or None)

#### 3.5.2 ILP Integration

[Discuss how ILP could be used, and why we use explicit checking]

**ILP formulation (not fully implemented):**
- Variables: m[i] for each place
- Constraints: 
  - m must be reachable (complex to encode)
  - For each transition: at least one input place must be empty
  
**Our implementation:** Simpler explicit checking approach
- Sufficient for small/medium nets
- Easier to understand and verify
- Avoids complex ILP encoding

### 3.6 Task 5: Optimization over Reachable Markings

#### 3.6.1 Problem Formulation

Maximize c^T · M subject to M ∈ Reach(M₀)

Where:
- c = (c₁, c₂, ..., cₙ) is the weight vector
- M = (m₁, m₂, ..., mₙ) is a marking
- Reach(M₀) is the set of reachable markings

#### 3.6.2 Algorithm

**Simple enumeration approach:**
1. Extract all reachable markings from BDD
2. For each marking M, compute objective value: v = Σᵢ cᵢ × mᵢ
3. Track maximum value and corresponding marking
4. Return optimal marking

**Time complexity:** O(|R| × |P|)

#### 3.6.3 Alternative: ILP-Based

[Describe ILP formulation]

```
Variables:
  y[k] ∈ {0,1}  for k = 1..|R|  (select marking k)
  m[i] ∈ {0,1}  for i = 1..|P|  (place i value)

Constraints:
  Σₖ y[k] = 1              (select exactly one marking)
  m[i] = Σₖ y[k] × Mₖ[i]   (m values match selected marking)

Objective:
  maximize Σᵢ cᵢ × m[i]
```

### 3.7 Libraries and Tools

| Library | Version | Purpose |
|---------|---------|---------|
| PyEDA | 0.28.0+ | BDD operations |
| PuLP | 2.7.0+ | ILP solving |
| lxml | 4.9.0+ | XML parsing |
| NetworkX | 3.1+ | Graph utilities (optional) |

---

## 4. Experimental Results

### 4.1 Test Cases

[Describe the test Petri nets used]

#### 4.1.1 Simple Net
- **Description:** Linear 3-place net
- **Places:** 3
- **Transitions:** 2
- **Initial marking:** (1, 0, 0)

#### 4.1.2 Producer-Consumer
[Details...]

#### 4.1.3 Mutual Exclusion
[Details...]

#### 4.1.4 Deadlock Example
[Details...]

### 4.2 Performance Results

#### Table 1: Reachability Analysis

| Net | |P| | |T| | |R| | Explicit (ms) | BDD (ms) | Speedup |
|-----|-----|-----|-----|---------------|----------|---------|
| Simple | 3 | 2 | 3 | 0.05 | 0.10 | 0.5× |
| Prod-Cons | 5 | 4 | 8 | 0.12 | 0.15 | 0.8× |
| Mutex | 5 | 4 | 3 | 0.08 | 0.11 | 0.7× |
| Deadlock | 4 | 3 | 5 | 0.09 | 0.12 | 0.75× |

[Add your actual measurements]

**Observations:**
- For small nets, explicit method is faster (less overhead)
- BDD approach would scale better for larger nets
- Our hybrid BDD approach has overhead from enumeration

#### Table 2: Deadlock Detection

| Net | Deadlock Found? | Time (ms) | Deadlock Marking |
|-----|-----------------|-----------|------------------|
| Simple | Yes | 0.05 | (0, 0, 1) |
| Prod-Cons | No | 0.10 | - |
| Mutex | No | 0.08 | - |
| Deadlock | Yes | 0.09 | (0, 0, 0, 0) |

#### Table 3: Optimization Results

| Net | Weights | Optimal Marking | Objective Value | Time (ms) |
|-----|---------|----------------|-----------------|-----------|
| Simple | (3,2,1) | (1, 0, 0) | 3.0 | 0.05 |
| Mutex | (0,0,1,1,2) | (0, 0, 1, 1, 1) | 4.0 | 0.08 |

### 4.3 Analysis

[Discuss results]

**Key findings:**
1. Explicit method faster for small nets due to BDD overhead
2. BDD provides compact representation (good for memory)
3. Deadlock detection works correctly
4. Optimization finds correct optimal markings

---

## 5. Discussion

### 5.1 Strengths of Our Implementation

1. **Correctness:** All tasks produce correct results
2. **Modularity:** Clean separation of concerns
3. **Usability:** Easy-to-use command-line interface
4. **Documentation:** Well-commented code

### 5.2 Limitations

1. **Hybrid BDD Approach:** Uses explicit enumeration, not pure symbolic
   - Trade-off: Simpler to implement, easier to debug
   - Impact: Less scalable for very large nets
   
2. **ILP Integration:** Limited use of ILP
   - Could encode more constraints symbolically
   - Current approach enumerates then checks

3. **Performance:** Not optimized for speed
   - Sufficient for assignment requirements
   - Could use CUDD for faster BDDs

### 5.3 Comparison with State-of-the-Art

[Compare with methods from references [17], [12], etc.]

**Pastor et al. [17]:**
- Uses pure symbolic BDD approach
- Implements full transition relation encoding
- More complex but scales better

**Our approach:**
- Simpler hybrid method
- Correct for small/medium nets
- Educational value: easier to understand

### 5.4 Challenges Encountered

#### Challenge 1: BDD Extraction

**Problem:** PyEDA's `restrict()` method didn't work as expected

**Solution:** Used `satisfy_all()` method instead

**Learning:** Always check library documentation and test edge cases

#### Challenge 2: PNML Parsing with Namespaces

**Problem:** Some PNML files have namespaces, others don't

**Solution:** Implemented fallback parsing without namespaces

#### Challenge 3: [Your challenges]

[Add any challenges you faced]

---

## 6. Conclusions

### 6.1 Summary

[Summarize what was accomplished]

We successfully implemented all five required tasks:
✓ PNML parsing with validation
✓ Explicit reachability using BFS
✓ Symbolic reachability using BDDs
✓ Deadlock detection combining BDD and checking
✓ Optimization over reachable markings

### 6.2 Learning Outcomes

[What did you learn from this assignment?]

1. Understanding of Petri net semantics
2. Practical experience with BDDs
3. Integration of symbolic and explicit methods
4. Trade-offs between different approaches

### 6.3 Future Work

**Possible improvements:**
1. Implement pure symbolic BDD approach
2. Add more sophisticated ILP encoding
3. Support for general (not just 1-safe) Petri nets
4. Visualization of Petri nets and reachability graphs
5. Additional verification properties (liveness, boundedness)

---

## 7. References

[1] Blätke, M. A., Heiner, M., & Marwan, W. (2015). Biomodel engineering with Petri nets...

[2] Bryant, R. E. (1986). Graph-based algorithms for boolean function manipulation...

[3] Burch, J. R., et al. (1992). Symbolic model checking: 10²⁰ states and beyond...

[Continue with all references from assignment document...]

---

## Appendices

### Appendix A: Installation Instructions

```bash
# Clone/extract project
cd petri_net_analysis

# Install dependencies
pip install -r requirements.txt

# Run tests
python main.py examples/simple.pnml
```

### Appendix B: Code Structure

```
petri_net_analysis/
├── petri_net.py              # Core data structures
├── pnml_parser.py            # Task 1
├── explicit_reachability.py  # Task 2
├── symbolic_reachability.py  # Task 3
├── deadlock_detection.py     # Task 4
├── reachable_optimization.py # Task 5
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
├── README.md                 # User guide
├── IMPLEMENTATION_GUIDE.md   # Developer guide
└── examples/                 # Test PNML files
    ├── simple.pnml
    ├── producer_consumer.pnml
    ├── deadlock_example.pnml
    └── mutual_exclusion.pnml
```

### Appendix C: Example Output

[Include full output of running your tool on an example]

```
======================================================================
  PETRI NET ANALYSIS
======================================================================
Input file: examples/simple.pnml

[Task 1] Parsing PNML file...
✓ Successfully parsed Petri net
  - Places: 3
  - Transitions: 2
  - Arcs: 4
  - Initial marking: (1, 0, 0)
  
[... full output ...]
```

### Appendix D: Key Code Snippets

[Include important code snippets that demonstrate key concepts]

```python
def fire_transition(self, transition_id: str, marking: Tuple[int, ...]) -> Tuple[int, ...]:
    """Fire a transition and return the new marking."""
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
```

---

## Declaration

We declare that this report and the accompanying code represent our own work, completed as a group. We have properly cited all external sources and have not shared our implementation with other groups.

**Group Members:**
- Name 1 (ID 1): [Signature] - [Contribution %]
- Name 2 (ID 2): [Signature] - [Contribution %]
- Name 3 (ID 3): [Signature] - [Contribution %]

Date: [Date]

---

**Total Pages:** 15 (within limit)
**Word Count:** ~[count] words

