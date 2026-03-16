# Shortest Round Trip

Visit each of 5 cities exactly once and return to the start, minimizing total distance. Uses the MTZ subtour elimination approach.

Set $N$ contains the cities. Parameters: $\text{dist}[i,j]$ for distances, scalar $\text{n\_cities}$ for the count, and $\text{mtz\_ub}[i,j]$ which is 0 for pairs where both cities are non-depot and distinct, and large otherwise (to deactivate the MTZ constraint for those pairs).

Binary variables $x[i,j]$ indicate edges in the tour. Continuous variables $u[i]$ (bounded 0 to 4) give city ordering.

Minimize total distance. Each city must have exactly one outgoing and one incoming edge. Self-loops are forbidden. MTZ constraints eliminate subtours using position variables, with mtz_ub relaxing the constraint for depot-related and self-loop pairs.
