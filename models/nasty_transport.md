# shipping stuff between factories and warehouses

We have 2 factories and 3 warehouses. Need to figure out cheapest way
to ship goods from factories to warehouses.

Shipping costs per unit (factory -> warehouse):
- factory 1 -> WH1: 4, WH2: 8, WH3: 1
- factory 2 -> WH1: 7, WH2: 2, WH3: 3

Supply limits: 30 and 50 respectively (factory 1 has 30, factory 2 has 50)

Each warehouse needs at least: WH1 needs 20, WH2 needs 25, WH3 needs 35

Variables: x(i,j) = how much to ship from factory i to warehouse j, must be >= 0

Minimize total shipping cost = sum of cost(i,j) * x(i,j) over all routes

Can't ship more than a factory has (supply constraint for each factory)
Each warehouse demand must be met (demand constraint for each warehouse)
