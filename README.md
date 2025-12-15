#  Mancala AI Solver: Minimax & Alpha-Beta Pruning

This project is a complete implementation of the African board game **Mancala (Kalah)** developed in Python, using the Pygame library for the graphical user interface.

The main objective was to design and analyze the effectiveness of Artificial Intelligence using the **Minimax algorithm with Alpha-Beta Pruning**.

## ⚙️ Project Features

* **Full Rule Implementation:** Handles core Mancala rules, including sowing, captures, free turns, and proper endgame scoring.
* **Minimax Algorithm:** The AI's decision-making core, optimized with Alpha-Beta Pruning for efficient search up to a configurable `MAX_DEPTH = 4`.
* **Game Modes:**
    * `Human vs Computer (HvC)`: A user plays against an AI using Heuristic 1 (H1).
    * `Computer vs Computer (CvC)`: A simulation where the Simple AI (H1) plays against the Strategic AI (H2).
* **AI Visualization:** The pit selected by the AI is highlighted in gold before the move executes, providing visual feedback on the AI's strategy.

## 🧠 AI Heuristics

Two distinct evaluation functions (heuristics) are implemented to compare strategic approaches:

### 1. Heuristic H1 (Simple / Foundational)

* **Description:** The basic, purely **tactical** evaluation function. It focuses exclusively on the immediate score difference.
* **Formula:** $$\text{H1} = \text{Score}_{\text{MAX}} - \text{Score}_{\text{MIN}}$$

### 2. Heuristic H2 (Strategic / Resource Control)

* **Description:** An advanced heuristic designed to introduce a **long-term strategic vision** by rewarding the retention of seeds on the player's side.
* **Formula:** $$\text{H2} = \underbrace{\text{H1}}_{\text{Store Score}} + \underbrace{(\mathbf{0.5} \times \text{Seeds in MAX's Pits})}_{\text{Resource Control Bonus}}$$
* **Rationale:** By adding a weighted bonus for seeds still in the player's pits, the AI is encouraged to favor moves that preserve offensive potential and maintain control over the board, even if the immediate score gain is slightly smaller.

## 🚀 Installation and Launch

### Prerequisites
You need Python (version 3.x recommended) and the Pygame library installed.

```bash
pip install pygame
