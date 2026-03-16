# Set Covering Problem

A city has $I = \{1, 2, 3, 4, 5, 6, 7, 8, 9, 10\}$ regions that must each be
covered by at least one facility. There are $J = \{1, 2, 3, 4, 5, 6, 7\}$
candidate facility locations, each with an opening cost $c_j$.

The coverage matrix $a_{i,j} \in \{0, 1\}$ indicates whether facility $j$ can
cover region $i$.

## Decision Variables

- $y_j \in \{0, 1\}$: 1 if facility $j$ is opened

## Objective

Minimize total facility cost:

$$\min \sum_{j \in J} c_j \, y_j$$

## Constraints

Each region must be covered by at least one open facility:

$$\sum_{j \in J} a_{i,j} \, y_j \geq 1 \quad \forall i \in I$$
