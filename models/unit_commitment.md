# Unit Commitment

Schedule generators over multiple time periods to meet demand at minimum
cost, subject to operating limits and ramping constraints.

## Sets

- $G = \{0,1\}$ — generators
- $T = \{0,1,2,3\}$ — time periods

## Parameters

- $\text{cost}_g$: per-MW generation cost
- $\text{p\_min}_g$: minimum output when on
- $\text{p\_max}_g$: maximum output
- $\text{ramp\_up}_g$: maximum increase between consecutive periods
- $\text{startup\_cost}_g$: cost incurred when a generator starts up
- $\text{demand}_t$: load that must be met
- $\text{p\_init}_g$: output at $t=-1$ (before the horizon)
- $\text{u\_init}_g$: on/off status at $t=-1$

## Decision Variables

- $p_{g,t} \geq 0$ — power output of generator $g$ in period $t$
- $u_{g,t} \in \{0,1\}$ — 1 if generator $g$ is on in period $t$
- $v_{g,t} \in \{0,1\}$ — 1 if generator $g$ starts up in period $t$

## Objective

$$\min \sum_{g \in G} \sum_{t \in T}
\bigl(\text{cost}_g \cdot p_{g,t} + \text{startup\_cost}_g \cdot v_{g,t}\bigr)$$

## Constraints

**Demand satisfaction:**
$$\sum_{g \in G} p_{g,t} \geq \text{demand}_t \quad \forall t \in T$$

**Minimum output:**
$$p_{g,t} \geq \text{p\_min}_g \cdot u_{g,t} \quad \forall g \in G,\; t \in T$$

**Maximum output:**
$$p_{g,t} \leq \text{p\_max}_g \cdot u_{g,t} \quad \forall g \in G,\; t \in T$$

**Ramp (first period):**
$$p_{g,0} - \text{p\_init}_g \leq \text{ramp\_up}_g \quad \forall g \in G$$

**Ramp (subsequent periods):**
$$p_{g,t} - p_{g,t-1} \leq \text{ramp\_up}_g \quad \forall g \in G,\; t \in T$$

**Startup detection (first period):**
$$v_{g,0} \geq u_{g,0} - \text{u\_init}_g \quad \forall g \in G$$

**Startup detection (subsequent periods):**
$$v_{g,t} \geq u_{g,t} - u_{g,t-1} \quad \forall g \in G,\; t \in T$$
