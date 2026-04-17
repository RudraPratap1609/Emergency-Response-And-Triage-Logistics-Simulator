# Emergency Response Triage Logistics Simulator (Crisis Command System)

## Overview
The Crisis Command System is an interactive pedagogical tool built around the 0/1 Knapsack problem solved via Dynamic Programming. In disaster triage operations, transport vehicles such as helicopters and drones operate under strict payload limits. This pygame-based simulator trains human operators by exposing them to randomly generated supply scenarios, capturing their loadout decisions under time pressure, and revealing the true mathematical optimum computed by a DP engine in real time.

This project bridges the gap between static algorithm textbooks and interactive decision-making under constraints.

## Key Features
- **Space-Optimised 1D DP:** Implements a rolling 1D array approach for the 0/1 Knapsack, reducing memory to O(W) while preserving the same time complexity O(n × W) by iterating in reverse order.
- **Three-Way Comparison:** Compares performance immediately between the User's loadout, a Greedy Heuristic baseline, and the DP Optimal solution.
- **Live State Visualisation:** Displays a live heat-map grid of the K[w] state array across all item iterations, allowing students to trace exactly how the algorithm builds the solution from scratch.
- **Procedural Scenario Generation:** Uses a 48-item supply depot dataset across 8 operational categories (grounded in real WHO and ICRC relief kit specifications).
- **Time Pressure:** Implements countdown timers across difficulty tiers (EASY: 120s, MEDIUM: 90s, HARD: 60s) to simulate real emergency conditions.
- **Player History Tracking:** A persistent module that displays a session log and an efficiency bar chart over time.
- **Custom Mode:** Allows instructors to define custom item counts, weight capacities, and timers to force scenarios where heuristics fail.

## System Architecture
The simulator follows a three-tier architecture:
1. **Data Layer (`items.py`):** Contains the 48-item supply depot dataset.
2. **Backend Logic Engine (`knapsack.py`):** Contains the core algorithm functions (`solve_01_knapsack()`, `solve_greedy()`, and `evaluate()`).
3. **Frontend UI (`main.py`):** Handles the scenario generation, user interaction (`draw_packing()`), timer module, DP visualiser (`draw_results()`), and history tracker (`draw_history()`).

## Complexity Analysis

| Algorithm | Time Complexity | Space Complexity | Guarantee |
| :--- | :--- | :--- | :--- |
| **Greedy (val/wt ratio)** | O(n log n) | O(n) | Approximate only |
| **Space-Optimised 1D DP** | O(n × W) | O(W) | Optimal |

## How to Play
1. Pick **EASY**, **MEDIUM**, **HARD**, or set your own **CUSTOM** difficulty.
2. You have a limited **TIME** to pack a rescue vehicle.
3. Click items on the left to add them. Watch the weight bar!
4. When done, hit **SUBMIT**. See if you beat the computer's optimal solution.
5. Check **HISTORY** to see how you've improved over time.

## Author Information
**Rudra Pratap** Registration No: 24BCE0415  
Design and Analysis of Algorithms (DAA)  
Vellore Institute of Technology, Vellore, Tamil Nadu
