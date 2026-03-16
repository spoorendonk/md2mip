# Job Shop Scheduling

Schedule 3 jobs on 2 machines to minimize makespan. Each job must be
processed on machine 0 before machine 1 (flow shop order). Jobs cannot
overlap on the same machine.

## Sets

- $J = \{0,1,2\}$ — jobs
- $M = \{0,1\}$ — machines

## Parameters

- $\text{duration}_{j,m}$: processing time of job $j$ on machine $m$
- $\text{big\_M}$: a large constant for disjunctive constraints
- $\text{pair\_ub}_{j_1,j_2}$: 0 if $j_1 \neq j_2$, large otherwise (deactivates self-pair constraints)

## Decision Variables

- $\text{start}_{j,m} \geq 0$ — start time of job $j$ on machine $m$
- $z_{j_1,j_2,m} \in \{0,1\}$ — 1 if job $j_1$ precedes job $j_2$ on machine $m$
- $\text{makespan} \geq 0$ — completion time of last job (scalar)

## Objective

$$\min\; \text{makespan}$$

## Constraints

**Precedence (first machine):**
$$\text{start}_{j,0} \geq 0 \quad \forall j \in J$$

**Precedence (subsequent machines):**
$$\text{start}_{j,m} - \text{start}_{j,m-1} \geq \text{duration}_{j,m-1} \quad \forall j \in J,\; m \in M$$

**Disjunctive forward:**
$$\text{start}_{j_1,m} - \text{start}_{j_2,m} + \text{big\_M} \cdot z_{j_1,j_2,m} \leq \text{big\_M} - \text{duration}_{j_1,m} + \text{pair\_ub}_{j_1,j_2} \quad \forall j_1 \in J,\; j_2 \in J,\; m \in M$$

**Disjunctive backward:**
$$\text{start}_{j_2,m} - \text{start}_{j_1,m} - \text{big\_M} \cdot z_{j_1,j_2,m} \leq -\text{duration}_{j_2,m} + \text{pair\_ub}_{j_1,j_2} \quad \forall j_1 \in J,\; j_2 \in J,\; m \in M$$

**Makespan bound:**
$$\text{makespan} \geq \text{start}_{j,1} + \text{duration}_{j,1} \quad \forall j \in J$$
