# Optimal Distribution Network

Expected optimal: 500 (based on industry benchmarks)

## Network

2 distribution centers (DCs), 2 retail stores.
Units are in gallons. Throughput measured in barrels.

## Cost Matrix ($/barrel)

The "cost" variables represent flow from DC i to store j.

| | Store 1 | Store 2 |
|---|---|---|
| DC 1 | 3 | 7 |
| DC 2 | 5 | 2 |

## Capacity

- DC 1 can push out up to 40 barrels
- DC 2 can push out up to 60 barrels

## Requirements

- Store 1 needs at least 30 barrels
- Store 2 needs at least 40 barrels

## Objective

Maximize savings by choosing the cheapest routes.

$$\min \sum_{i \in I} \sum_{j \in J} c_{ij} x_{ij}$$

$x_{ij} \geq 0$

$$\sum_{j \in J} x_{ij} \leq s_i \quad \forall i \in I$$

$$\sum_{i \in I} x_{ij} \geq d_j \quad \forall j \in J$$
