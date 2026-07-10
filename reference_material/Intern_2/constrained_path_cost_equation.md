# Constrained Path-Cost Equation (Step 9, v4)

Applies to feasible cells only (Step 8): slope <= 30 deg AND confidence class != Insignificant.
Non-feasible cells are set to NaN (excluded from the navigable graph).

v4 = v3 with median-aligned (skewed) moderate triangular MFs for slope and roughness.
Feasible mask unchanged from v3 (0 cells flipped); R95 unchanged (27.514 m).

## Penalty terms (each normalized to [0, 1])

P_slope = clip(slope_deg / 30, 0, 1)
  Normalized to the 30 deg rover traversability limit (NASA GRC; Shrivastava et al. 2020).

P_rough = clip(roughness / 27.514, 0, 1)
  27.514 m = 95th-percentile roughness of FEASIBLE cells (robust to outliers; verified on v4).

P_shadow = clip(shadow_fraction, 0, 1)
  Static solar-power-loss proxy (Lamarre et al. 2024; Tang et al. 2026).

## Base terrain cost

base_cost = 0.6*P_slope + 0.1*P_rough + 0.3*P_shadow

  Weights are a project design choice (slope = primary traversability driver; roughness and
  shadow equal secondary). Equation STRUCTURE (per-cell DEM-derived slope+roughness cost)
  follows Ji et al. 2023, NNPP (arXiv:2308.04792). Weights are NOT from that paper.
  To be supported by a weight sensitivity analysis (Step 11).

## Confidence multiplier (project contribution)

multiplier = 1 + (1 - confidence_score)
  Range [1, 2]; observed [1.153, 1.847] on feasible cells.
  Low data confidence inflates cost but never blocks a cell (consistent with Step 8).
  confidence_score -> 1 gives multiplier -> 1 (no penalty);
  confidence_score -> 0 gives multiplier -> 2 (cost doubled).

## Science reward

science_reward = 0.0
  Placeholder; instantiated at path-planning time from M3 spectral context for the chosen destination (Step 11).

## Final equation

path_cost = base_cost * multiplier - science_reward

Fully expanded:
path_cost = (0.6*P_slope + 0.1*P_rough + 0.3*P_shadow) * (1 + (1 - confidence_score)) - science_reward

Observed range on v4 feasible cells: 0.005 to 1.847, median 0.723, mean 0.794.

## References

- NASA Glenn Research Center. Exploration Rover Concepts and Development Challenges. (30 deg locomotion limit on friable lunar slopes.)
- Shrivastava, S., et al. (2020). Material remodeling and unconventional gaits facilitate locomotion of a robophysical rover over granular terrain. Science Robotics 5, eaba3499.
- Ji, Y., Liu, Y., Xie, G., Ma, B., Xie, Z., Cao, B. (2023). NNPP: A Learning-Based Heuristic Model for Accelerating Optimal Path Planning on Uneven Terrain. arXiv:2308.04792.
- Lamarre, O., et al. (2024). Safe Mission-Level Path Planning for Exploration of Lunar Shadowed Regions by a Solar-Powered Rover. IEEE Aerospace Conference. arXiv:2401.08558.
- Tang et al. (2026). High-resolution accessibility and energy cost assessment of 31 priority permanently shadowed regions at the lunar south pole. Frontiers in Astronomy and Space Sciences. (Verify author list before citing.)
