# Multicommodity Flow

Route multiple commodities through a network at minimum cost,
respecting shared arc capacities.

## Sets

- $N = \{0,1,2,3\}$ — nodes
- $K = \{0,1\}$ — commodities

## Parameters

- $\text{cap}_{i,j} \geq 0$: capacity of arc $(i,j)$; 0 means no arc
- $\text{cost}_{i,j,k} \geq 0$: per-unit cost of shipping commodity $k$ on arc $(i,j)$
- $\text{supply}_{i,k}$: net supply of commodity $k$ at node $i$ (positive = supply, negative = demand)

## Decision Variables

- $\text{flow}_{i,j,k} \geq 0$: flow of commodity $k$ on arc $(i,j)$

## Objective

$$\min \sum_{i \in N} \sum_{j \in N} \sum_{k \in K} \text{cost}_{i,j,k} \cdot \text{flow}_{i,j,k}$$

## Constraints

**Flow balance** at each node for each commodity:
$$\sum_{j \in N} \text{flow}_{i,j,k} - \sum_{j \in N} \text{flow}_{j,i,k} = \text{supply}_{i,k}
\quad \forall i \in N,\; k \in K$$

**Arc capacity** shared across commodities:
$$\sum_{k \in K} \text{flow}_{i,j,k} \leq \text{cap}_{i,j}
\quad \forall i \in N,\; j \in N$$
