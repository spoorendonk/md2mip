# Production Planning / Lot Sizing

Multi-period production planning.

**Sets:** $T = \{0, 1, \ldots, 7\}$ (8 weeks), but production starts at $t=0$.

**Parameters:**
- Demand: $d = [10, 15, 20, 18, 12, 25, 22, 16]$ (indexed 0..7)
- Production cost: $p_t = 5 \;\; \forall t$
- Holding cost: $h = 2$ per unit per period
- Setup cost: $K = 50$
- Max production: $M = 40$
- Initial inventory: $I_0^{\text{init}} = 5$

**Variables:**
- $x_t \geq 0$ — units produced in period $t$
- $I_t \geq 0$ — inventory at end of period $t$
- $z_t \in \{0,1\}$ — whether production occurs in $t$

$$\min \sum_{t \in T} \left( p_t x_t + h \cdot I_t + K \cdot z_t \right)$$

s.t.

$$I_t = I_{t-1} + x_t - d_t \quad \forall t \in T$$

where $I_{-1} = I_0^{\text{init}} = 5$.

$$x_t \leq M \cdot z_t \quad \forall t \in T$$

$$x_t \geq 0, \quad I_t \geq 0, \quad z_t \in \{0,1\} \quad \forall t \in T$$
