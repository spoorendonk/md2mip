# Network Routing Problem

We have a directed graph with nodes and arcs. Multiple types of goods (commodities) must be shipped from sources to destinations. Each arc has a capacity limiting total flow across all commodities, and each commodity has its own per-unit shipping cost on each arc.

Sets: $N$ (nodes), $K$ (commodities). Parameters include arc capacities $\text{cap}[i,j]$, costs $\text{cost}[i,j,k]$, and supply/demand $\text{supply}[i,k]$.

Continuous variables $\text{flow}[i,j,k]$ represent the amount of commodity $k$ sent along arc $(i,j)$.

Minimize total shipping cost. Flow balance must hold at every node for each commodity. The sum of all commodity flows on each arc must not exceed its capacity.
