# Generator Scheduling

We need to decide which generators to turn on/off across several time periods, and how much each should produce, to meet electricity demand at minimum total cost (generation + startup).

Sets are $G$ (generators) and $T$ (time periods). Each generator has a cost per MW, min/max output levels, a ramp-up limit, and a startup cost. Demand varies by period. Initial conditions (output and status before the horizon) are given as parameters.

Continuous variables $p[g,t]$ represent power output. Binary variables $u[g,t]$ indicate on/off status, and $v[g,t]$ indicate startup events.

Constraints: meet demand, respect min/max when on, limit ramp-up between consecutive periods, and detect startups (with separate handling for the first period using initial conditions).
