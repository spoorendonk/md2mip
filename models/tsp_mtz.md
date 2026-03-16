# Travelling Salesman (MTZ Formulation)

Find the shortest Hamiltonian tour through 5 cities using the
Miller–Tucker–Zemlin subtour elimination formulation.

## Sets

- $N = \{0,1,2,3,4\}$ — cities

## Parameters

- $\text{dist}_{i,j}$: travel distance from city $i$ to city $j$
- $\text{n\_cities}$: number of cities (scalar)
- $\text{mtz\_ub}_{i,j}$: deactivation bound — 0 for active MTZ pairs ($i \geq 1, j \geq 1, i \neq j$), large otherwise

## Decision Variables

- $x_{i,j} \in \{0,1\}$: 1 if the tour travels directly from city $i$ to city $j$
- $u_i \geq 0$: position of city $i$ in the tour (continuous, upper bound 4)

## Objective

$$\min \sum_{i \in N} \sum_{j \in N} \text{dist}_{i,j} \cdot x_{i,j}$$

## Constraints

**Leave each city exactly once:**
$$\sum_{j \in N} x_{i,j} = 1 \quad \forall i \in N$$

**Enter each city exactly once:**
$$\sum_{j \in N} x_{j,i} = 1 \quad \forall i \in N$$

**No self-loops:**
$$x_{i,i} \leq 0 \quad \forall i \in N$$

**MTZ subtour elimination:**
$$u_i - u_j + \text{n\_cities} \cdot x_{i,j} \leq \text{n\_cities} - 1 + \text{mtz\_ub}_{i,j} \quad \forall i \in N,\; j \in N$$
