# Emergency-Response-And-Triage-Logistics-Simulator
My Project for the DAA Course in university based on the 0-1 Knapsack Algorithm.

Abstract
This report documents the second review submission of the Emergency Response and Triage Logistics
Simulator (Crisis Command System), a pedagogical tool built around the 0/1 Knapsack problem solved
via Dynamic Programming. The simulator has been substantially upgraded from Review 1, incorporating
a space-optimised 1D DP implementation with O(W) memory, a live visualisation of the K[w] state array
across all item iterations, a three-way performance comparison (User vs. Greedy Heuristic vs. DP
Optimal), a countdown timer per difficulty tier, a persistent Player History module, and a dataset expanded
to 48 real-world-inspired disaster relief items across 8 operational categories. The software bridges the
gap between static algorithm textbooks and interactive decision-making under constraints, providing
trainees with immediate, quantified feedback on their deviation from the mathematically optimal solution.
This paper details the system architecture, algorithmic methodology, module descriptions, UI
improvements, complexity analysis, and a comparative study against existing tools.
I. Introduction
In disaster triage operations, transport vehicles such as helicopters and drones operate under strict
payload limits. Human coordinators must make rapid decisions about which relief supplies to carry,
frequently falling back on intuitive but mathematically suboptimal heuristics. The 0/1 Knapsack problem
— choosing an indivisible subset of items to maximise total value without exceeding a weight capacity —
precisely models this scenario.
The Crisis Command System is an interactive pygame-based simulator that trains human operators by
exposing them to randomly generated supply scenarios, capturing their loadout decisions under time
pressure, and then revealing the true mathematical optimum computed by a Dynamic Programming
engine in real time. Unlike static algorithm visualisers or solved textbook examples, this tool creates
genuine decision-making pressure and produces a quantified performance gap.
Review 2 introduces six major improvements over the Review 1 prototype: (1) Space-Optimised 1D DP,
(2) expanded 48-item dataset, (3) countdown timer, (4) Custom difficulty mode, (5) Player History
tracking, and (6) a substantially improved DP state visualisation. These are detailed in the sections that
follow.
II. Literature Review
The 0/1 Knapsack problem is NP-complete in the general case but admits a pseudo-polynomial Dynamic
Programming solution in O(nW) time and O(W) space. Existing literature extensively covers the
theoretical complexity and its applications in automated supply-chain routing and portfolio optimisation.
A notable gap persists in the intersection of algorithm education and interactive training software.
Commercial emergency logistics tools (e.g., UN OCHA ReliefWeb dashboards, FEMA logistics systems)
are automated pipelines with no human decision-training component. Algorithm visualisation platforms
(VisuAlgo, CS Academy) present static demonstrations of the DP recurrence but do not generate novel
scenarios or compare human intuition against algorithmic outputs in real time.
This project fills that gap by combining procedural scenario generation, constrained human decision-
making, space-optimised DP, and a live K[w] array visualiser — producing a tool that is simultaneously
an educational simulator and a decision-support training system.
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 3
III. System Architecture
The system follows a three-tier architecture: Data Layer, Backend Logic Engine, and Frontend UI. The
diagram below illustrates data flow across all modules.
SYSTEM ARCHITECTURE — Crisis Command System (Review 2)
DATA LAYER | items.py — 48 disaster relief items (weight, value,
category)
▼
SCENARIO GENERATION MODULE | random.sample() by difficulty tier
┌──────────────────────┴─────────────────────────┐
▼ HUMAN PATH ALGORITHM PATH ▼
USER INTERACTION MODULE ALGORITHM & OPTIMISATION ENGINE
draw_packing() + Timer solve_01_knapsack() | solve_greedy()
▼ user_sel (set) ▼ dp_val, dp_sel, dp_history
USER LOADOUT OUTPUT OPTIMAL LOADOUT OUTPUT + K[w] array
└──────────────────────┬─────────────────────────┘
▼
EVALUATION & FEEDBACK MODULE | evaluate() — user vs greedy vs DP
▼
RESULTS / UI DISPLAY | 3-column comparison + 1D K[w] visualiser
▼
PLAYER HISTORY MODULE | session log + efficiency bar chart
Figure 1: System Architecture of the Crisis Command System (Review 2)
IV. Changes from Review 1 to Review 2
A. Space-Optimised 1D DP (Major Algorithmic Upgrade)
Review 1 employed a full 2D matrix K[n+1][W+1], requiring O(n×W) space. Review 2 replaces this with
the rolling 1D array approach, reducing memory to O(W) while preserving the same time complexity
O(n×W). The key difference is iterating w in reverse order for each item, ensuring that each item is
counted at most once — maintaining the 0/1 constraint without the extra dimension.
Review 1: dp = [[0]*(W+1) for _ in range(n+1)] # O(n x W) space
Review 2: dp = [0] * (W+1) # O(W) space
for i in range(n):
for w in range(max_W, wi-1, -1): # REVERSE traversal
dp[w] = max(dp[w], dp[w-wi]+val) # in-place update
The reverse traversal is critical: it prevents item i from being considered for inclusion more than once in
the same pass (which would degrade the problem to Unbounded Knapsack). This is the professor's
suggested state-space optimisation, now fully implemented.
B. Live 1D K[w] State Visualisation
The dp_history list captures snapshots of the 1D array after every item is processed. The Results screen
renders this as a grid where rows represent item iterations and columns represent weight capacities.
Cells where the value increased vs. the previous row are highlighted in bright teal (indicating the item
was 'taken' at that weight), and the final answer cell is marked in yellow. This lets a student trace exactly
how the algorithm builds the solution from scratch.
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 4
C. Three-Way Algorithm Comparison
Review 1 showed User vs. DP only. Review 2 adds the Greedy heuristic as a third baseline. The greedy
solver ranks items by value/weight ratio and greedily packs until the constraint is exceeded — exactly
the flawed intuition the simulator is designed to expose. The three-column results panel makes the
comparison immediate and intuitive.
D. Countdown Timer
Each difficulty tier now enforces a countdown: EASY 120s, MEDIUM 90s, HARD 60s. If the timer expires,
the loadout is auto-submitted, simulating the time pressure of real disaster response. The timer renders
as a colour-shifting progress bar (green → orange → red).
E. Custom Difficulty Mode
A fourth difficulty option — CUSTOM — allows the user to configure the number of items, weight capacity,
and timer independently via on-screen input fields. This enables instructors to craft specific scenarios
that highlight particular algorithm behaviours (e.g., forcing scenarios where greedy fails dramatically).
F. Player History Module
Each completed session appends a record to a persistent history list (stored in memory during the
session). The HISTORY screen displays a table of all rounds (difficulty, score, DP optimal, efficiency%,
status, items count) and a bar chart of efficiency over time, allowing trainees to visualise their
improvement across multiple rounds.
G. Dataset Expansion to 48 Items
The dataset grew from 12 items in Review 1 to 48 items across 8 categories (Medical, Power, Survival,
Comms, Rescue, Transport, Shelter, Special). Each item has an operational description grounded in
WHO and ICRC standard relief kit specifications, improving the simulator's real-world credibility.
V. Module Description
The table below maps each logical module to its implementing file and primary function.
Module File Key Function Output
Data Layer items.py 48-item supply depot dataset item list (w, val, cat)
Scenario
Generator main.py random.sample() by difficulty scenario[], max_W
User Interaction main.py draw_packing() user_sel (set of indices)
Algorithm Engine knapsack.py solve_01_knapsack() dp_val, selected, history
Greedy Engine knapsack.py solve_greedy() greedy_val, gr_sel
Evaluation Module knapsack.py evaluate() efficiency%, gaps, status
DP Visualiser main.py draw_results() - K[w] grid colour-coded 1D table
History Tracker main.py draw_history() session log + bar chart
Timer Module main.py countdown per difficulty auto-submit on timeout
Table 1: Module-to-File Mapping for Review 2
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 5
A. Scenario Generation Module
Implemented within main.py via new_scenario(diff). For preset difficulties it calls
random.sample(SUPPLY_ITEMS, n) where n varies by tier. For CUSTOM mode, the user supplies n, W,
and timer values directly. Calling new_scenario() also resets user_sel, scroll_y, and the countdown timer,
ensuring a clean state for each round.
B. User Interaction Module — draw_packing()
The left panel renders item cards for all items in the current scenario. Cards show item name, category
(with colour stripe), weight, value, and value/weight ratio. Clicking a card toggles selection if adding it
would not breach max_W. The right panel shows real-time weight progress bar (colour-shifting at 75%
and 90% utilisation), loaded items list with REMOVE buttons, the space-optimised DP recurrence
formula, and the countdown timer bar.
C. Algorithm Engine — knapsack.py
Three independent functions: solve_01_knapsack() runs the 1D space-optimised DP and records
dp_history for each item step. solve_greedy() sorts by value/weight ratio and greedily packs. evaluate()
computes all performance metrics. These are pure functions — no pygame dependencies — making
them independently testable.
D. Evaluation and Feedback Module — evaluate()
Returns a dict with: user_value, user_weight, dp_value, greedy_value, efficiency (%), dp_gap,
greedy_gap, and status string (OPTIMAL / NEAR OPTIMAL / SUBOPTIMAL / POOR). Status thresholds:
100% = OPTIMAL, ≥90% = NEAR OPTIMAL, ≥70% = SUBOPTIMAL, <70% = POOR.
E. Results Screen — draw_results()
Three columns display loaded items, weights, and gap from DP optimal for each of the three approaches.
Items present in the DP optimal loadout are marked with an asterisk. Below the comparison panel, the
full K[w] state array is rendered as a heat-map grid. Row labels show item names (truncated), column
headers show weight values w from 0 to max_W. The yellow cell (bottom-right) is always the DP answer.
F. Player History Module — draw_history()
Tracks a list of dicts, one per completed session. Renders a scrollable table and a proportional bar chart
of efficiency percentages. Bars are green for ≥90%, orange for ≥70%, red otherwise. A CLEAR HISTORY
button resets the list.
VI. Dataset and Method Description
A. Dataset Description
The 48-item supply depot in items.py spans 8 operational categories, with weights ranging from 1 kg
(Water Tablets) to 42 kg (Generator) and survival values from 30 pts (Camp Stove) to 150 pts
(Generator). All weights are integers, eliminating the fractional-weight DP indexing problem raised in
Review 1 feedback. Each item has an operational description string grounded in standard relief kit
specifications from WHO and ICRC published guidelines.
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 6
Category breakdown: Medical (12 items), Survival (8), Rescue (7), Power (5), Transport (4), Comms (4),
Shelter (4), Special (4).
B. Method Description — Space-Optimised 0/1 Knapsack
The core algorithm is the 1D space-optimised 0/1 Knapsack. Given n items each with integer weight w_i
and value v_i, and vehicle capacity W:
Space-Optimised 0/1 Knapsack Recurrence
Initialise: K[0..W] = 0
For each item i = 1 to n:
For w = W downto w_i: (reverse order — ensures 0/1 property)
K[w] = max( K[w] , val_i + K[w - w_i] )
↑ skip item i ↑ take item i
Answer: K[W] | Time: O(n × W) | Space: O(W)
Figure 2: Space-Optimised 0/1 Knapsack Recurrence (Review 2 Algorithm)
Why reverse traversal guarantees 0/1 correctness: if we iterated w forward, then when computing K[w],
K[w - w_i] would already have been updated to include item i in the current pass. The reverse traversal
ensures K[w - w_i] still reflects the state before item i was considered, so item i can only be added once
— preserving the 0/1 constraint without a second array dimension.
C. Greedy Heuristic Baseline
The greedy solver sorts items descending by ratio r_i = val_i / w_i and packs greedily. It runs in O(n log
n). It does NOT guarantee the global optimum for indivisible items — this failure is exactly what the
simulator demonstrates. In scenarios where a heavy high-value item crowds out several lighter high-ratio
items, greedy often falls significantly short of the DP optimal.
D. Traceback for Item Recovery
The dp_history list stores n+1 snapshots of the K[w] array (before and after each item). To identify which
items were selected by DP, the traceback scans backwards: if K_i[w] > K_{i-1}[w], item i was taken, w is
decremented by w_i, and the process continues for item i-1.
VII. Complexity Analysis
Algorithm Time Space Guarantee
Greedy (val/wt ratio) O(n log n) O(n) Approximate only
Review 1 — 2D DP O(n × W) O(n × W) Optimal
Review 1 — 3D DP (dual) O(n × W × V) O(n × W × V) Optimal (dual)
Review 2 — 1D DP (O(W)) O(n × W) O(W) Optimal ✓
Table 2: Complexity Comparison across Algorithm Variants
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 7
VIII. Why This Software Outperforms Existing Tools
The following comparison evaluates the Crisis Command System against the two categories of existing
software: commercial emergency logistics tools and academic algorithm visualisers.
Feature / Aspect Existing Tools
(Static DP Demos) Review 1 Simulator Review 2 (Current) Crisis
Command System
Algorithm 2D matrix (O(nW)
space)
2D + 3D dual
constraint
1D Space-Opt DP O(W)
Greedy Comparison None Greedy vs DP User vs Greedy vs DP
DP Visualisation Static diagrams Colour-coded 2D grid Live 1D K[w] state array
Scenario Generation Fixed textbook
examples
Random from 12
items
Random from 48 items
Difficulty Tiers None Easy/Medium/Hard Easy/Med/Hard/Custom
Timer Pressure None None 120s / 90s / 60s
Player History None None Full session log + chart
Expert/Student Mode None None Switchable UI modes
Real Dataset Size 3-5 items 12 items 48 relief supply items
Weight Constraint Single (weight) Dual
(weight+volume)
Single (weight, O(W))
Memory Complexity O(n×W) O(n×W×V) O(W) rolling array
Table 3: Comparative Analysis — Crisis Command System vs. Existing Solutions
A. Against Commercial Emergency Logistics Platforms
Systems like UN OCHA ReliefWeb, FEMA Logistics Management System, and WHO emergency kits are
fully automated pipelines. They compute optimal or near-optimal allocations internally but provide no
educational transparency — an operator cannot see why a particular loadout was chosen. They also
require expensive infrastructure and real operational data. The Crisis Command System exposes the
decision-making process explicitly, trains operators to understand the trade-offs, and runs on any
personal computer.
B. Against Static Algorithm Visualisers
Platforms such as VisuAlgo and CS Academy present the DP recurrence on fixed textbook examples
(e.g., a 4-item problem with W=10). They are excellent for understanding the mechanics but provide no
novel problem generation, no human-in-the-loop decision phase, and no performance measurement. A
student can watch the animation without ever engaging their own judgment.
The Crisis Command System forces genuine decision-making: the student must commit to a loadout
under time pressure before seeing the DP answer. The subsequent three-way comparison (User vs.
Greedy vs. DP) makes the cost of suboptimal thinking immediately visible and quantified.
C. Key Differentiating Features
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 8
• Procedural generation: 48-item pool randomised per session means no two scenarios are
identical — preventing memorisation of optimal answers.
• Timer pressure: simulates real emergency conditions where slow decisions have
consequences.
• 1D K[w] state visualisation: the only interactive tool (to the authors' knowledge) that renders the
rolling DP array step-by-step alongside the scenario.
• Session history: tracks efficiency improvement over multiple rounds — transforming the
simulator into a training progression system, not just a one-shot demo.
• Zero infrastructure: runs locally with pip install pygame — deployable in any classroom without
internet connectivity.
IX. Software Screenshots
Figure 3 — Main Menu (Student Mode)
The main menu presents four difficulty tiers, the algorithm explanation panel showing the space-
optimised recurrence K[w] = max(K[w], val_i + K[w-w_i]), and How to Play instructions. HISTORY and
STUDENT MODE buttons are visible in the bottom right.
Figure 3: Main Menu — Space-Optimised DP recurrence displayed at all times
Figure 4 — Expert Mode Menu
Expert Mode expands the algorithm panel to show the full problem statement (indivisibility rule,
maximisation objective) and time/space complexity. This mode is designed for students already familiar
with the basics who want deeper algorithmic context.
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 9
Figure 4: Expert Mode Menu — extended algorithm panel with complexity analysis
Figure 5 — Packing Screen (HARD difficulty)
The left panel shows all 10 scenario items as cards with weight, value, category, and value/weight ratio.
The right panel shows the countdown timer (42s remaining, colour-shifted red), weight bar at near-
capacity (54/55 kg), the space-opt DP recurrence formula, and the loaded items list with REMOVE
buttons. The '[NO ROOM]' label on Battery Bank and Radio Set shows real-time constraint enforcement.
Figure 5: Packing Screen — HARD mode, 54/55 kg loaded, 42s remaining
Figure 6 — Mission Debrief / Results Screen
Three columns compare the user (553 pts, A rank), greedy heuristic (568 pts), and DP optimal (593 pts).
Items marked with * appear in the DP optimal solution. Below, the 1D DP state visualisation shows K[w]
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 10
snapshots for all 10 items across all weight values 0–55, with the final answer (593) highlighted in yellow
at K[55].
Figure 6: Mission Debrief — 3-way comparison + 1D K[w] state visualiser (HARD, 593 pts DP optimal)
Figure 7 — Player History Screen
The history screen records all completed sessions in a table and renders an efficiency bar chart. In this
example, 4 sessions were played — two HARD rounds, one MEDIUM, one EASY — with efficiencies
ranging from 81% to 100%. The colour scheme (green ≥90%, orange 70-89%) provides instant visual
feedback on improvement trajectory.
Figure 7: Player History — 4 sessions, efficiency bar chart over time
X. Conclusion
Emergency Response Triage Logistics Simulator | Project Review 2 VIT Vellore — DAA
Rudra Pratap | Design & Analysis of Algorithms | Page 11
The Review 2 submission of the Emergency Response and Triage Logistics Simulator (Crisis Command
System) represents a complete implementation of the space-optimised 0/1 Knapsack algorithm in an
interactive educational context. All six modifications requested by the Review 1 feedback have been
addressed: the algorithm has been upgraded to a 1D rolling-array formulation (O(W) space), item
indivisibility is strictly enforced (no duplicates, 0/1 constraint maintained by reverse traversal), a three-
way comparison against the greedy heuristic is rendered in every results screen, the dataset has been
expanded to 48 real-world-inspired items, a custom difficulty mode allows instructor-defined scenarios,
and a persistent session history module tracks trainee improvement over time.
The system succeeds in its primary objective: making the superiority of Dynamic Programming over
human intuition and greedy heuristics immediately visible and quantified. By combining procedural
generation, time pressure, and a live K[w] state visualisation, it creates a learning environment that static
textbook examples and automated commercial tools cannot replicate.
Future work will explore implementing the multi-dimensional knapsack (weight + volume dual constraint)
as a selectable Expert Mode, integrating actual WHO/ICRC relief kit weights as a verified dataset, and
adding a step-by-step DP trace mode where students can manually fill in the K[w] array cell by cell
