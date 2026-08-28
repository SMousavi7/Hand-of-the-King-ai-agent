# Hand of the King — Minimax AI Agent with Genetic Optimization

An AI agent for the **Hand of the King** board game, built using **Minimax search with Alpha-Beta Pruning** and a heuristic evaluation function whose weights were optimized using a **Genetic Algorithm**.

The agent was developed as part of an Artificial Intelligence course project and achieved **3rd place in the course AI agent competition**.

> **Note:** The underlying game implementation and framework were developed by the authors of the original [Hand of the King repository](https://github.com/Mohammad-Momeni/Hand-of-the-King).
> This repository is a fork of that project. My contribution focuses specifically on the **AI agent, heuristic evaluation strategy, and genetic optimization pipeline** described below.

---

## Our Contribution

My work in this project focuses on developing and optimizing an intelligent game-playing agent.

The main contributions are:

* Implementation of a **Minimax-based game-playing agent**
* **Alpha-Beta Pruning** for reducing the Minimax search space
* Adaptive search depth based on the current game state
* Design of a custom **heuristic evaluation function**
* Evaluation of board state using house control, banners, collected cards, companion opportunities, and board configuration
* Optimization of heuristic coefficients using a **Genetic Algorithm**
* Automated agent-vs-agent matches for evaluating candidate heuristic weights
* Tournament-based selection of candidate solutions
* Crossover and mutation for evolving new heuristic configurations
* Final elimination tournament for selecting strong configurations
* **3rd place in the course AI agent competition**

---

# AI Agent

The main agent implementation is located in:

```text
ghadim_agent1.py
```

The agent selects its moves using:

```text
Minimax
    +
Alpha-Beta Pruning
    +
Heuristic Evaluation
```

The overall decision process is:

```text
Current Game State
        │
        ▼
Generate Valid Moves
        │
        ▼
Simulate Future Game States
        │
        ▼
Minimax Search
        │
        ├── Maximizing Player
        │
        └── Minimizing Player
        │
        ▼
Alpha-Beta Pruning
        │
        ▼
Evaluate Leaf States
        │
        ▼
Select Best Move
```

---

# Minimax Search

The agent explores future game states using the **Minimax algorithm**.

At each level of the search tree, the algorithm alternates between:

```text
MAX → Our agent attempts to maximize the evaluation score

MIN → The opponent attempts to minimize the evaluation score
```

Game states are copied before moves are simulated so that possible future actions can be evaluated without modifying the real game state.

---

## Alpha-Beta Pruning

Standard Minimax can become computationally expensive because the number of possible states grows rapidly with search depth.

To reduce unnecessary exploration, the agent uses **Alpha-Beta Pruning**.

Conceptually:

```text
                    Current State
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
           Move A      Move B      Move C
             │           │           │
             ▼           ▼           ▼
          Search       Search      Search
                         │
                         X
                    Pruned Branch
```

Branches that cannot influence the final decision are skipped, allowing the agent to search more efficiently.

---

# Adaptive Search Depth

Instead of always searching to a fixed depth, the agent changes its Minimax depth according to the game state.

The default search depth is:

```text
Depth = 3
```

As the game progresses and the number of remaining possibilities decreases, the search becomes deeper:

```text
Early Game
    ↓
Depth 3

Mid Game
    ↓
Depth 5

Late Game / Reduced Companion Space
    ↓
Depth 7
```

This allows the agent to balance computational cost with decision quality.

During the early game, where the branching factor is large, a shallower search is used.

Later in the game, when fewer cards and actions remain, deeper search becomes computationally feasible.

---

# Heuristic Evaluation Function

Minimax cannot search the complete game tree during most game states.

Therefore, when the search reaches its depth limit, the resulting state must be assigned an estimated value.

The agent uses a custom heuristic function:

```text
evaluate_state(...)
```

The evaluation function combines several strategic characteristics of a game state into a single score.

A larger score represents a more favorable state for the agent, while a smaller score represents a state favoring the opponent.

---

## House-Specific Weights

The seven houses do not necessarily have the same strategic value.

The heuristic therefore maintains separate coefficients for:

```text
Stark
Greyjoy
Lannister
Targaryen
Baratheon
Tyrell
Tully
```

The final optimized agent uses the following coefficients:

```text
Stark       = 13
Greyjoy     = 5
Lannister   = 15
Targaryen   = 6
Baratheon   = 11
Tyrell      = 8
Tully       = 10
```

Additional heuristic parameters include:

```text
Half        = -2
Companion   = -5
Combo       = 12
```

Rather than selecting all of these coefficients manually, candidate configurations were explored using a **Genetic Algorithm**.

---

# Board-State Evaluation

The heuristic considers several aspects of the current game state.

## Banner Control

Owning a house banner contributes positively to the evaluation score.

If the opponent controls that banner, the corresponding value is subtracted.

This allows Minimax to prefer states where the agent controls strategically valuable houses.

---

## Collected House Cards

The heuristic also considers how many members of each house have already been collected.

This provides additional information beyond simply checking the current banner owner.

The value of collecting additional members changes depending on how much of a house has already been acquired.

---

## Varys Position

Because the position of **Varys** determines which character cards can be selected during a normal move, the evaluation function also analyzes the board relative to Varys.

The remaining cards are examined in the four directions around Varys:

```text
                 UP
                  │
                  │
        LEFT ── VARYS ── RIGHT
                  │
                  │
                 DOWN
```

This allows the heuristic to estimate the strategic opportunities available from the current board configuration.

---

## Companion Opportunities

The evaluation function also considers situations where taking the final member of a house may enable access to companion-card actions.

These opportunities are incorporated into the state score through a dedicated heuristic coefficient.

---

## Card Combinations

Potential combinations of cards belonging to the same house along available directions are also considered.

This gives the agent information about whether the current Varys position may allow useful sequences of acquisitions.

---

# Companion Card Search

The agent does not limit Minimax to ordinary Varys movements.

It also evaluates possible actions involving companion cards.

Depending on the companion card, different move structures may need to be generated.

The search considers the available choices and simulates their effect on:

```text
Board state
Player cards
Banner ownership
Remaining companion cards
Future Minimax states
```

This allows companion-card decisions to become part of the search tree instead of being handled entirely separately from the agent's normal strategy.

---

# Genetic Algorithm

A major part of this project is the optimization of the heuristic evaluation function.

Instead of relying exclusively on manually selected coefficients, a **Genetic Algorithm (GA)** was implemented to search for stronger parameter configurations.

The optimization pipeline is implemented in:

```text
gen_algorithm.py
```

Each individual in the genetic population represents a candidate set of heuristic weights.

Conceptually:

```text
Individual
│
├── Stark Weight
├── Greyjoy Weight
├── Lannister Weight
├── Targaryen Weight
├── Baratheon Weight
├── Tyrell Weight
├── Tully Weight
├── Half Weight
├── Companion Weight
└── Combo Weight
```

---

# Initial Population

The optimization starts by generating randomized candidate parameter configurations.

Candidate weights are stored as text files under:

```text
generations/
```

A configuration may conceptually look like:

```text
Stark 13
Greyjoy 5
Lannister 15
Targaryen 6
Baratheon 11
Tyrell 8
Tully 10
Half -2
Companion -5
Combo 12
```

Each configuration represents one candidate heuristic function.

---

# Fitness Through Actual Games

Instead of assigning fitness using a static mathematical objective, candidate configurations are evaluated through **actual matches**.

Two configurations are loaded and their corresponding agents play against each other using the game engine.

Conceptually:

```text
Candidate A
     │
     ▼
Agent A ───────┐
               │
               ▼
             MATCH
               │
               ▲
Agent B ───────┘
     ▲
     │
Candidate B
```

The winner survives the selection process.

This means optimization is directly connected to game-playing performance.

---

# Tournament Selection

Candidate configurations are randomly paired.

For each pair:

```text
Candidate A
      │
      ├────► Game ────► Winner
      │
Candidate B
```

The losing configuration is eliminated while the winning configuration survives.

This provides the selection pressure used by the genetic algorithm.

---

# Crossover

Surviving configurations are paired to generate new children.

For each heuristic coefficient, the child may inherit the value from either parent.

For example:

```text
Parent A

Stark      13
Greyjoy     7
Lannister  10


Parent B

Stark       9
Greyjoy    12
Lannister  15


            │
            ▼

         Crossover

            │
            ▼

Child

Stark      13
Greyjoy    12
Lannister  15
```

This allows successful characteristics from different agents to be combined.

---

# Mutation

After crossover, candidate parameters may also undergo random mutation.

The implementation applies mutation probabilistically to individual coefficients.

A selected value receives a small random modification:

```text
weight → weight + random(-2, 2)
```

Mutation introduces additional diversity into the population and helps the search explore configurations that were not present in the original population.

---

# Evolution Process

The overall optimization process can be summarized as:

```text
Generate Initial Population
            │
            ▼
     Candidate Weights
            │
            ▼
      Play Matches
            │
            ▼
   Tournament Selection
            │
            ▼
     Keep Winners
            │
            ▼
        Crossover
            │
            ▼
         Mutation
            │
            ▼
      New Generation
            │
            └───────────────┐
                            │
                            ▼
                     Repeat Process
```

The training script performs this evolutionary process over multiple generations.

---

# Final Elimination Tournament

A separate script:

```text
elimination_gen.py
```

implements a knockout tournament between generated configurations.

Candidate weight files are randomly paired and play matches against one another.

After every match, the losing configuration is removed.

The process continues until:

```text
N candidates
     │
     ▼
N / 2
     │
     ▼
N / 4
     │
     ▼
...
     │
     ▼
1 Winner
```

This provides an additional mechanism for selecting a final candidate from the generated population.

---

# AI Pipeline

The complete development process can be summarized as:

```text
               Hand of the King
                  Game Engine
                       │
                       ▼
              Minimax AI Agent
                       │
                       ▼
           Heuristic Evaluation
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
  Strategic Features        Heuristic Weights
                                    │
                                    ▼
                            Genetic Algorithm
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                   Agent Matches         Tournament
                         │                     │
                         └──────────┬──────────┘
                                    ▼
                              Best Weights
                                    │
                                    ▼
                          Final Minimax Agent
                                    │
                                    ▼
                            AI Competition
                                    │
                                    ▼
                               3rd Place
```

---

# Competition Result

The final agent was submitted to the **course AI agent competition**, where agents developed by different students competed against each other.

The agent achieved:

## 🥉 3rd Place

The competition agent combined:

```text
Minimax Search
+
Alpha-Beta Pruning
+
Adaptive Search Depth
+
Custom State Evaluation
+
Genetically Optimized Heuristic Weights
```

---

# Files Added for This Agent

The primary files associated with my contribution are:

```text
ghadim_agent1.py
gen_algorithm.py
elimination_gen.py
```

### `ghadim_agent1.py`

Contains the main AI agent, including:

* Valid-move generation
* State evaluation
* Minimax
* Alpha-Beta Pruning
* Companion-card search
* Adaptive search depth
* Final heuristic coefficients

### `gen_algorithm.py`

Contains the heuristic-weight optimization pipeline, including:

* Population generation
* Automated agent matches
* Tournament selection
* Crossover
* Mutation
* Generation management

### `elimination_gen.py`

Runs a knockout tournament among generated configurations to identify a final surviving candidate.

---

# Original Game

The underlying **Hand of the King** implementation was developed by the authors of the original repository:

**[Mohammad-Momeni/Hand-of-the-King](https://github.com/Mohammad-Momeni/Hand-of-the-King)**

The original repository contains the game engine, graphical assets, board definitions, utilities, and baseline agents used by this project.

This repository was created as a **fork** so that the original work remains clearly attributed while the AI agent and optimization work can be presented separately.

---

# Running the Agent

## Requirements

The original project requires Python and its game-related dependencies.

Clone this fork:

```bash
git clone https://github.com/SMousavi7/Hand-of-the-King-ai-agent.git
cd Hand-of-the-King-ai-agent
```

Install the dependencies required by the original game environment.

For compatibility with the original project setup, the game may require packages such as:

```bash
pip install pygame-ce
pip install moviepy==1.0.3
```

> Depending on the Python version, the original `pygame` package may require a compatible Python release. `pygame-ce` can provide the `pygame` module on newer environments.

---

## Run the Agent

The game accepts player agents through command-line arguments.

For example, to play manually against the agent:

```bash
python main.py --player1 human --player2 ghadim_agent1
```

The exact player position can be reversed if desired:

```bash
python main.py --player1 ghadim_agent1 --player2 human
```

---

# Technologies & Concepts

* Python
* Artificial Intelligence
* Game AI
* Minimax
* Alpha-Beta Pruning
* Genetic Algorithms
* Evolutionary Optimization
* Heuristic Search
* Adversarial Search
* Game-Tree Search
* Tournament Selection
* Crossover
* Mutation

---

## Attribution

The game framework is based on the original **Hand of the King** implementation:

[Original Repository — Mohammad-Momeni/Hand-of-the-King](https://github.com/Mohammad-Momeni/Hand-of-the-King)

My contribution is limited to the AI agent and the associated heuristic-optimization/evaluation pipeline described in this README.

## Authors

The AI agent and genetic optimization pipeline were developed collaboratively by:

- **[@SMousavi7](https://github.com/SMousavi7)**
- **[@TEAMMATE_GITHUB_USERNAME](https://github.com/TEAMMATE_GITHUB_USERNAME)**

The underlying game framework belongs to the authors of the original repository:

[Original Hand of the King Repository](https://github.com/Mohammad-Momeni/Hand-of-the-King)
