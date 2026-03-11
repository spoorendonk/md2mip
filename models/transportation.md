# Transportation Problem

## Sets

- $I = \{1, 2\}$ — Sources (factories)
- $J = \{1, 2, 3\}$ — Destinations (warehouses)

## Parameters

| | $j=1$ | $j=2$ | $j=3$ |
|---|---|---|---|
| $c_{1j}$ | 4 | 8 | 1 |
| $c_{2j}$ | 7 | 2 | 3 |

- Supply: $s_1 = 30, \; s_2 = 50$
- Demand: $d_1 = 20, \; d_2 = 25, \; d_3 = 35$

## Variables

$x_{ij} \geq 0 \quad \forall i \in I, \; j \in J$

## Formulation

$$\min \sum_{i \in I} \sum_{j \in J} c_{ij} x_{ij}$$

subject to:

$$\sum_{j \in J} x_{ij} \leq s_i \quad \forall i \in I$$

$$\sum_{i \in I} x_{ij} \geq d_j \quad \forall j \in J$$
