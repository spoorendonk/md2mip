# knapsack problm

ok so we have 5 items and a bag that holds W=15 units of weight

values are v_1=4, v2=2, v_3=10, v4=1, v_5=2
weights: w1=12, w_2=1, w3=4, w4=1, w_5=2

we want to pick items to get the most value without going over capacity

Σ v_i * xi for all items should be maximized

constraint: Σ w_i * xi ≤ W

xi binary (either take item or dont)
