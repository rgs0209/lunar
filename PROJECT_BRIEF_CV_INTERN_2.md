# PROJECT BRIEF

## Project Title

Visual Rover Localization and Route Tracking Under Battery and Compute Constraints

## Objective

Develop a computer-vision method that estimates the position of a simulated
lunar rover from a local rover-view proxy and keeps the rover close to its
planned route. The method must decide when visual localization, route
correction, replanning, or return-to-start is necessary while respecting a
declared battery reserve and onboard compute limit.

## Research Question

Can adaptive visual localization and route correction keep a simulated lunar
rover on its planned route while using less battery and compute than fixed-rate
visual localization?

## Primary Inputs

- Area A and B LROC optical crops for reference-map and rover-view simulation.
- LOLA terrain layers for map geometry and route context.
- Intern 2 feasibility, exclusion, confidence, and path-cost layers as fixed
  navigation constraints.
- Intern 3 accepted regions, science rank, and consensus goal layers for goal
  selection.
- Intern 4 grid-world and policy code as reference implementations.

## Method

1. Build separate georeferenced 25 m grid worlds for Consensus Areas A and B.
2. Select valid start cells and science-goal cells using 15 degrees as the safe
   baseline slope limit.
3. Plan the green-baseline route using A* or Dijkstra's algorithm on the
   supplied path-cost surface.
4. Repeat route-feasibility tests at slope limits of 16, 17, 18, 19, and 20
   degrees. Mark these routes and cells yellow as manageable risk, not safe.
5. Simulate a local rover view by extracting a small LROC image window around
   the rover's true position.
6. Estimate the rover position by matching the local window with the Area A or
   B reference image. Begin with ORB feature matching and RANSAC; use normalized
   cross-correlation or template matching as a fallback for low-feature views.
7. Introduce controlled position drift so the estimated rover position can
   differ from the true simulated position.
8. Compare the estimated position with the expected route position and measure
   cross-track error.
9. Correct the route when the localization confidence is sufficient and the
   route error exceeds a declared threshold.
10. Add battery costs for movement, image capture, visual matching, replanning,
   and return travel.
11. Add actions: move, capture image, localize, continue, replan, return, and
    stop.
12. Compare three policies: no visual correction, fixed-rate visual
    localization, and adaptive battery-aware visual localization.
13. Repeat the same experiments in Areas A and B under position drift,
    illumination change, image noise, and partial image loss.
14. Measure runtime and memory under a declared SHAKTI-class processor
    assumption.

## Required Outputs

- Area A and B georeferenced grid-world tables.
- Start, goal, and initial-route records.
- Rover-view window manifest with true and estimated coordinates.
- Visual match table containing matched features, inliers, localization
  confidence, and position error.
- Localization-error maps and route-tracking plots.
- Battery and compute-cost equations with all parameter values.
- Battery profile along every tested route.
- Comparison of no-correction, fixed-rate, and adaptive-localization policies.
- Position error, route deviation, path length, localization count, replan
  count, goal success, return success, runtime, and memory results.
- Failure-scenario and cross-area comparison tables.
- Green-baseline versus yellow manageable-risk route comparison for slope
  limits 15, 16, 17, 18, 19, and 20 degrees.
- Final report and presentation.

## Working Rules

- Follow the approved passability, energy, movement-cost, and test-scenario
  values in `../APPROVED_THRESHOLDS.md`.
- This project does not detect or classify terrain hazards.
- Use 15 degrees as the safe baseline. Values 16 through 20 degrees are
  capability sensitivity tests and must be labelled manageable risk, not safe.
- Treat the supplied feasibility, exclusion, confidence, and path-cost layers
  as fixed navigation inputs; do not rebuild their hazard calculations.
- Do not use or wait for CV Intern 1 outputs.
- Do not reuse Intern 4's old 200 by 200 grid as if it were georeferenced to
  Areas A or B. Build new grids from the supplied area layers.
- Use the LROC window only as a simulated rover-view proxy. Do not claim that
  it is a real rover-camera image.
- Keep the same localization, battery, and route-correction settings when
  comparing Area A with Area B.
- State every simulated battery and compute assumption clearly.
- Use a SHAKTI-class processor assumption in the final compute discussion; do
  not retain the earlier RAD750 assumption.
