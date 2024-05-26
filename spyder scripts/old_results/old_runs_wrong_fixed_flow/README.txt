### old settings that are changed for new runs

- flow_caught_fixed_solution will now be calculated correctly and using inverse matrices instead of LP with fixed solution
- before this, RADIUS_SHORE_IMPACT was always equal to 50. now it is equal to MAX_DIST_NODES/2
- init distribution was highly concentrated at Delft station, will be changed in next version
- some runs for impact factor are still missing
- some runs are still missing the 0.2 steps and only have B = 1, 2, 3, 4