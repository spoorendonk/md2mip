# Fire Station Placement

We need to figure out where to build fire stations so every neighborhood
is within response range of at least one station.

## Neighborhoods

We have 10 neighborhoods to protect.

## Candidate Sites

7 possible locations for stations, with different construction costs:

| Station | Cost | Covers neighborhoods |
|---------|------|---------------------|
| S1 | 45 | 1, 2, 3 |
| S2 | 35 | 2, 4, 5 |
| S3 | 50 | 3, 5, 6, 7 |
| S4 | 30 | 1, 6, 8 |
| S5 | 40 | 7, 8, 9 |
| S6 | 25 | 9, 10 |
| S7 | 55 | 4, 5, 8, 9, 10 |

Every neighborhood must have at least one station that can reach it.
Find the cheapest set of stations to build.
