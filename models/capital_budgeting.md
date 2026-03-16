# Capital Budgeting

A firm is considering $P = \{1, 2, 3, 4, 5, 6\}$ projects over $T = \{1, 2, 3\}$
budget periods. Each project $p$ has a net present value $\text{npv}_p$ and a cost
$\text{cost}_{p,t}$ in each period $t$. The firm has a budget $B_t$ per period and
can select at most $K$ projects.

## Decision Variables

- $y_p \in \{0, 1\}$: 1 if project $p$ is selected

## Objective

Maximize total NPV:

$$\max \sum_{p \in P} \text{npv}_p \, y_p$$

## Constraints

**Cardinality:** at most $K$ projects selected:
$$\sum_{p \in P} y_p \leq K$$

**Budget per period:**
$$\sum_{p \in P} \text{cost}_{p,t} \, y_p \leq B_t \quad \forall t \in T$$

**Implication:** project 3 requires project 1:
$$y_3 \leq y_1$$

**Mutual exclusion:** projects 4 and 5 cannot both be selected:
$$y_4 + y_5 \leq 1$$
