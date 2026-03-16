# Mini-Sudoku (4×4)

Fill a 4×4 grid with digits 1–4 so that each row, column, and 2×2 block
contains each digit exactly once. Some cells are pre-filled (clues).

## Sets

- $R = \{0,1,2,3\}$ — rows
- $C = \{0,1,2,3\}$ — columns
- $V = \{0,1,2,3\}$ — values (representing digits 1–4)
- $B = \{0,1,2,3\}$ — blocks (2×2 sub-grids)

## Parameters

- $\text{blk}_{r,c,b} \in \{0,1\}$: 1 if cell $(r,c)$ belongs to block $b$
- $\text{clue}_{r,c,v} \in \{0,1\}$: 1 if cell $(r,c)$ is pre-filled with value $v$

## Decision Variables

- $x_{r,c,v} \in \{0,1\}$: 1 if cell $(r,c)$ is assigned value $v$

## Objective

Pure feasibility — no optimization needed:

$$\min\; 0$$

## Constraints

**One value per cell:**
$$\sum_{v \in V} x_{r,c,v} = 1 \quad \forall r \in R,\; c \in C$$

**Row uniqueness:**
$$\sum_{c \in C} x_{r,c,v} = 1 \quad \forall r \in R,\; v \in V$$

**Column uniqueness:**
$$\sum_{r \in R} x_{r,c,v} = 1 \quad \forall c \in C,\; v \in V$$

**Block uniqueness:**
$$\sum_{r \in R} \sum_{c \in C} \text{blk}_{r,c,b} \cdot x_{r,c,v} = 1 \quad \forall b \in B,\; v \in V$$

**Clue fixing:**
$$x_{r,c,v} \geq \text{clue}_{r,c,v} \quad \forall r \in R,\; c \in C,\; v \in V$$
