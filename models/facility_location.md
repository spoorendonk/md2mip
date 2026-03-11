# Uncapacitated Facility Location Problem (UFLP)

Consider a set of potential facility locations $I = \{A, B, C\}$ and a set of
customers $J = \{1, 2, 3, 4\}$. Opening facility $i$ incurs a fixed cost $f_i$.
Serving customer $j$ from facility $i$ costs $c_{ij}$ per unit. Each customer
has a demand of 1 unit that must be satisfied by exactly one facility.

**Fixed costs:**
- $f_A = 100, \quad f_B = 150, \quad f_C = 120$

**Service costs $c_{ij}$:**

|  | 1 | 2 | 3 | 4 |
|--|---|---|---|---|
| A | 10 | 25 | 40 | 15 |
| B | 30 | 5 | 10 | 20 |
| C | 20 | 15 | 20 | 10 |

**Decision variables:**
- $y_i = 1$ if facility $i$ is opened, 0 otherwise
- $x_{ij} = 1$ if customer $j$ is served from facility $i$, 0 otherwise

**Minimize** total cost:

$$\min \; \sum_{i \in I} f_i y_i + \sum_{i \in I} \sum_{j \in J} c_{ij} x_{ij}$$

**Subject to:**

Each customer is served by exactly one facility:
$$\sum_{i \in I} x_{ij} = 1 \quad \forall j \in J$$

A customer can only be served from an open facility:
$$x_{ij} \leq y_i \quad \forall i \in I, \; j \in J$$

$x_{ij} \in \{0, 1\}, \; y_i \in \{0, 1\}$
