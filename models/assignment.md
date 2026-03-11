# Assignment Problem

Assign 4 workers to 4 tasks. Cost matrix:

```
     T1  T2  T3  T4
W1 [  9   2  7   8 ]
W2 [  6   4  3   7 ]
W3 [  5   8  1   8 ]
W4 [  7   6  9   4 ]
```

min sum_i sum_j c_ij * x_ij

Each worker does exactly one task:
  sum_j x_ij = 1  for all i

Each task gets exactly one worker:
  sum_i x_ij = 1  for all j

x_ij in {0,1}
