# N-Queens (4×4)

Place 4 queens on a 4×4 chessboard so that no two queens share the same
row, column, or diagonal.

## Sets

- $R = \{0,1,2,3\}$ — rows
- $C = \{0,1,2,3\}$ — columns

## Parameters

- $\text{diag}_{r_1,c_1,r_2,c_2} \in \{0,1\}$: 1 if cells $(r_1,c_1)$ and $(r_2,c_2)$ share a diagonal and are distinct

## Decision Variables

- $x_{r,c} \in \{0,1\}$: 1 if a queen is placed at $(r,c)$

## Objective

Pure feasibility — no optimization needed:

$$\min\; 0$$

## Constraints

**One queen per row:**
$$\sum_{c \in C} x_{r,c} = 1 \quad \forall r \in R$$

**One queen per column:**
$$\sum_{r \in R} x_{r,c} = 1 \quad \forall c \in C$$

**No diagonal conflicts:**
$$\text{diag}_{r_1,c_1,r_2,c_2} \cdot x_{r_1,c_1} + \text{diag}_{r_1,c_1,r_2,c_2} \cdot x_{r_2,c_2} \leq 1 \quad \forall r_1 \in R,\; c_1 \in C,\; r_2 \in R,\; c_2 \in C$$
