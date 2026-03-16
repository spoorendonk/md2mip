# Constraint Satisfaction Puzzle

Here's an interesting discrete puzzle. We have a square grid of size 4 by 4, split into four 2x2 blocks. We must place values from {1,2,3,4} in each cell such that no repetitions occur within any row, column, or block. Some cells already have assigned values.

The sets are rows $R$, columns $C$, digit-values $V$, and blocks $B$, each of size 4. Parameter $\text{blk}[r,c,b]$ is 1 when cell $(r,c)$ lies in block $b$. Parameter $\text{clue}[r,c,v]$ is 1 if the cell is given value $v$ as a clue.

Binary variables $x[r,c,v]$ indicate the digit assignment.

The model is pure feasibility, so we minimize a trivial zero objective.

Constraints enforce: exactly one value per cell, each value once per row, each value once per column, each value once per block, and clue cells fixed.
