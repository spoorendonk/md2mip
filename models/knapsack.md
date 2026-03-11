# 0-1 Knapsack

We have 5 items. Knapsack capacity W=15.

Values: $v = (4, 2, 10, 1, 2)$

Weights: $w = (12, 1, 4, 1, 2)$

Pick items to maximize value:

$$\max \sum_{i=1}^{5} v_i x_i$$
$$\text{s.t.} \quad \sum_{i=1}^{5} w_i x_i \leq W$$
$$x_i \in \{0, 1\}$$
