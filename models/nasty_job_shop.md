# Production Line Timing

Three tasks must each visit two workstations in order (station 0 then station 1). No two tasks can use the same station at the same time. We want to finish everything as early as possible.

Sets: $J$ (jobs) and $M$ (machines). Parameters are processing times $\text{duration}[j,m]$, a big-M constant $\text{big\_M}$, and a deactivation parameter $\text{pair\_ub}[j_1,j_2]$ that is 0 for distinct job pairs and large for self-pairs.

Continuous variables $\text{start}[j,m]$ give start times. Binary variables $z[j_1,j_2,m]$ encode job ordering on each machine. A scalar variable $\text{makespan}$ tracks the latest completion.

Minimize makespan. Enforce machine precedence (each job goes through machines in order, with lag constraints using m-1), disjunctive no-overlap via big-M with pair_ub added to the RHS to deactivate self-pairs, and makespan lower bounds from the last machine.
