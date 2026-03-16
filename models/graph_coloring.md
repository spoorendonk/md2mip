# Graph Coloring

Given a graph with vertices $V = \{1, 2, 3, 4, 5, 6\}$ and colors
$K = \{1, 2, 3, 4\}$, assign a color to each vertex so that no two adjacent
vertices share the same color, using as few colors as possible.

## Adjacency

The adjacency matrix $\text{adj}_{v_1, v_2} \in \{0, 1\}$ indicates whether
vertices $v_1$ and $v_2$ are connected by an edge.

## Decision Variables

- $x_{v,k} \in \{0, 1\}$: 1 if vertex $v$ is assigned color $k$
- $\text{used}_k \in \{0, 1\}$: 1 if color $k$ is used by any vertex

## Objective

Minimize the number of colors used:

$$\min \sum_{k \in K} \text{used}_k$$

## Constraints

**Assignment:** each vertex gets exactly one color:
$$\sum_{k \in K} x_{v,k} = 1 \quad \forall v \in V$$

**Conflict:** adjacent vertices cannot share a color:
$$\text{adj}_{v_1, v_2} \, x_{v_1, k} + \text{adj}_{v_1, v_2} \, x_{v_2, k} \leq 1 \quad \forall v_1 \in V, \; v_2 \in V, \; k \in K$$

**Color usage linking:** a color is used if any vertex has it:
$$x_{v,k} \leq \text{used}_k \quad \forall v \in V, \; k \in K$$
