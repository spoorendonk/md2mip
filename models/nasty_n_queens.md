# Board Placement Puzzle

Place exactly one piece in each row and each column of a 4×4 grid. Additionally, no two pieces may be on the same diagonal.

Sets are $R$ (rows) and $C$ (columns), both of size 4. A precomputed binary parameter $\text{diag}[r_1,c_1,r_2,c_2]$ equals 1 when two distinct cells share a diagonal.

Binary variables $x[r,c]$ indicate piece placement.

The objective is trivial (minimize 0) since this is a feasibility problem.

Constraints: one piece per row, one piece per column, and for all pairs of cells, the diagonal parameter times both placement variables must not exceed 1.
