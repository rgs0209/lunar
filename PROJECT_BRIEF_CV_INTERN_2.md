# PROJECT BRIEF

## Project Title

Visual Rover Localization and Route Tracking Under Battery and Compute
Constraints

## Project Objective

The objective of this project is to develop a computer-vision method that
estimates the position of a simulated lunar rover from a local LROC rover-view
proxy and keeps the rover close to its planned route.

The method should decide when image capture, visual localization, route
correction, replanning, return-to-start, or stopping is necessary while
respecting declared battery and onboard-compute limits.

## Research Question

Can adaptive visual localization and route correction keep a simulated lunar
rover on its planned route while using less battery and compute than fixed-rate
visual localization?

## Environment

Use a Python georeferenced grid-world with OpenCV-based visual localization.
Use the supplied Area A and B rasters. Unity and Isaac Sim are not required for
the main experiments.

Run development on the available computer and report a declared SHAKTI-class
processor assumption for the onboard-compute discussion. Do not claim that the
available computer is a rover flight processor.

## Methods To Use

Route-planning methods:

- A* algorithm
- Dijkstra's algorithm as a check or fallback
- Fixed supplied path-cost and feasibility layers

Visual-localization methods:

- ORB keypoint detection and descriptor matching
- RANSAC geometric verification
- Normalized cross-correlation or template matching for low-feature views
- Position-error and cross-track-error calculation

Policies to compare:

- No Visual Correction Policy
- Fixed-Rate Visual Localization Policy
- Adaptive Battery-Aware Visual Localization Policy

Disturbance tests:

- Position drift
- Illumination change
- Image noise
- Partial image loss
- Reduced battery budget
- Delayed or skipped localization

Metrics:

- Localization error
- Cross-track error
- Route deviation
- Goal and return success
- Path length
- Number of image captures and localization calls
- Number of route corrections and replans
- Simulated energy cost
- Runtime and memory requirement

## Working Rules

- Do not overwrite any supplied file.
- Save all generated files inside an `outputs` folder.
- Follow `../APPROVED_THRESHOLDS.md` exactly.
- This project does not detect or classify terrain hazards.
- Treat feasibility, exclusion, confidence, path-cost, accepted-region, and
  science-goal layers as fixed navigation inputs.
- Use mean slope up to 15 degrees as the green baseline.
- Show 16, 17, 18, 19, and 20 degrees as separate yellow manageable-risk
  capability tests. Do not call them safe.
- Do not reuse Intern 4's old 200 by 200 grid, start cell, or goal cell.
- Build new georeferenced grid worlds for Areas A and B.
- Use an LROC window only as a simulated rover-view proxy, not a real rover-
  camera image.
- Work simultaneously with CV Intern 1. Do not use or wait for CV Intern 1
  outputs.
- Keep the same visual-matching, battery, and policy settings when comparing
  Area A with Area B.
- State every simulated energy and compute assumption clearly.

## Use of Previous Intern Reports

The supplied Intern 2 report may be read to understand the confidence,
feasibility, and path-cost products. The Intern 3 report may be read to
understand accepted regions and science-target ranking. The Intern 4 report and
reference scripts may be read to understand grid-world policies, Q-learning,
scenario tests, energy proxies, and compute-cost reporting.

The earlier reports and scripts are references. Build new Area A and B grids,
routes, rover-view observations, localization results, policies, metrics, code,
and conclusions for this project from the supplied georeferenced inputs.

## Integration Rule

Export route, localization, battery, and policy results with map coordinates,
area name, time step, and cell identifier. This allows the module to be added
later to the digital twin without depending on CV Intern 1 during the
internship.

## Primary Analysis Unit

Use the 25 m grid as the navigation and decision grid. Use LROC 5 m windows as
local visual observations. Convert between the two grids using map coordinates
and Rasterio transforms.

Each simulation step must store at least:

- true rover cell and map coordinate;
- estimated rover cell and map coordinate;
- planned-route cell;
- localization confidence;
- cross-track error;
- remaining simulated energy;
- action selected;
- whether replanning or return was triggered.

## Software and Environment Setup

### Step A: Create a project environment

Open Command Prompt or the Visual Studio Code terminal inside your project
folder and run:

```text
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib rasterio opencv-python scipy scikit-image networkx psutil jupyter
```

Python 3.10 may be used if Python 3.11 is not available.

### Step B: Check the installation

Run:

```text
python -c "import rasterio, cv2, numpy, pandas, networkx; print('Environment ready')"
```

The terminal should print `Environment ready` without an error.

### Step C: Create working folders

Create the following folders inside your project folder:

```text
notebooks/
src/
outputs/
outputs/tables/
outputs/maps/
outputs/figures/
outputs/logs/
outputs/routes/
```

Record the final package versions using:

```text
python -m pip freeze > outputs/software_versions.txt
```

Do not begin by running the old Intern 4 scripts. First build the new Area A
and B grids from the supplied GeoTIFFs.

## Methodology

### Step 1: Read the project instructions and intern reports

Task: Understand the fixed inputs and identify which older materials are only
references.

How:

- Read `DATASET_GUIDE.md`, `CONSENSUS_AREA_GUIDE.md`, and
  `APPROVED_THRESHOLDS.md` from the package root.
- Read the Intern 2, Intern 3, and Intern 4 reports in the `reports` folder.
- Record the meaning of path cost, feasible mask, exclusion mask, confidence,
  accepted region, science rank, and goal mask.
- List every historical value that must not be reused, including the old 200 by
  200 grid and 20-degree green-safe interpretation.

Output:

- `outputs/input_role_table.csv`
- `outputs/historical_values_not_reused.md`

Check:

- Every input must be marked as `working input`, `goal context`, `method
  reference`, or `not used`.

### Step 2: Inspect and align the Area A and Area B rasters

Task: Confirm that the supplied layers can be connected by map location.

How:

- Use Rasterio to record filename, shape, CRS, transform, resolution, data
  type, no-data, and valid percentage.
- Confirm alignment among all 25 m layers within each area.
- Confirm that each 5 m LROC crop covers the same physical area as the matching
  25 m grid.
- Plot the path cost, feasible mask, confidence, goal mask, LROC, and LOLA.

Output:

- `outputs/tables/raster_inventory.csv`
- `outputs/figures/navigation_input_quicklook.png`

Check:

- Categorical masks must be read as class codes and never averaged.

### Step 3: Build new georeferenced grid worlds

Task: Convert the supplied 25 m products into navigation tables for Areas A
and B.

How:

- Create one table row for every 25 m cell.
- Store row, column, map x, map y, path cost, feasibility, exclusion,
  confidence, accepted-region ID, science rank, and goal flag.
- Preserve no-data as missing, not zero.
- Apply the 15-degree green baseline and create separate 16, 17, 18, 19, and
  20-degree yellow sensitivity versions.
- Do not copy the old Intern 4 grid.

Output:

- `outputs/tables/grid_world_area_A.csv`
- `outputs/tables/grid_world_area_B.csv`
- `outputs/tables/grid_schema.csv`

Check:

- Convert several table cells back to map coordinates and confirm they overlay
  the correct raster cells.

### Step 4: Select start and goal locations

Task: Choose valid route endpoints using declared rules.

How:

- Select science goals from the consensus goal mask and target tables.
- Select start cells from feasible green-baseline cells with valid LROC support.
- Ensure the start and goal are connected under the tested route condition.
- Record the reason for selecting every start and goal.
- Use more than one start-goal pair in each area where time permits.

Output:

- `outputs/tables/start_goal_pairs.csv`
- `outputs/figures/start_goal_map.png`

Check:

- Do not use the fixed start and goal coordinates from Intern 4.

### Step 5: Plan the initial routes

Task: Create the routes that the simulated rover should follow.

How:

- Use A* on the supplied path-cost surface.
- Use eight movement directions, cardinal multiplier `1.0`, and diagonal
  multiplier `sqrt(2)`.
- Prevent movement through excluded or impassable cells.
- Verify one route using Dijkstra's algorithm.
- Repeat route-feasibility checks for the green baseline and each yellow
  capability case.

Output:

- `outputs/routes/initial_routes.csv`
- `outputs/tables/initial_route_metrics.csv`
- `outputs/figures/initial_route_maps.png`

Check:

- Yellow sensitivity routes must remain visually and numerically separate from
  the green baseline.

### Step 6: Generate simulated rover-view observations

Task: Create local image windows for known true rover positions.

How:

- Choose route locations at regular intervals.
- Convert each true 25 m route cell to the corresponding LROC 5 m coordinate.
- Extract a fixed local LROC window centred on the true location.
- Reject windows that cross the raster boundary or contain excessive no-data.
- Save the true coordinate, window size, route step, and area name.

Output:

- `outputs/tables/rover_view_manifest.csv`
- `outputs/figures/rover_view_examples.png`

Check:

- Call these windows simulated rover-view proxies, not real camera images.

### Step 7: Implement the visual-localization baseline

Task: Estimate the rover location from each local LROC window.

How:

- Detect ORB keypoints in the local observation and the larger reference search
  area.
- Match descriptors and retain geometrically consistent matches with RANSAC.
- Estimate the local-window centre in reference-map coordinates.
- If ORB has too few valid features, run normalized cross-correlation or
  template matching as a declared fallback.
- Record method used, match count, inlier count, inlier ratio, similarity
  score, estimated coordinate, and runtime.

Output:

- `outputs/tables/visual_match_results.csv`
- `outputs/figures/match_examples.png`

Check:

- A high raw match count is not sufficient without geometric verification.

### Step 8: Validate the visual-matching thresholds

Task: Select evidence-based acceptance rules for localization.

How:

- On the development area, test minimum match count, RANSAC inlier count or
  ratio, reprojection tolerance, and normalized cross-correlation threshold.
- Choose thresholds before opening the final test results from the other area.
- Apply unchanged thresholds to the other area.
- Reverse the areas and repeat.
- Reject low-confidence localizations rather than forcing a coordinate.

Output:

- `outputs/tables/localization_threshold_tests.csv`?????
- `outputs/localization_acceptance_rules.md`

Check:

- Every final threshold must have a table or plot showing why it was selected.

### Step 9: Calculate localization and route errors

Task: Measure how far the estimate is from the true and planned locations.

How:

- Calculate pixel, cell, and metre error between true and estimated positions.
- Calculate cross-track distance from the estimated position to the planned
  route.
- Introduce controlled drift so the predicted rover state moves away from the
  true state between localizations.
- Record when localization reduces or fails to reduce the error.

Output:

- `outputs/tables/localization_error.csv`
- `outputs/figures/localization_error_maps.png`
- `outputs/figures/cross_track_error_plot.png`

Check:

- Do not calculate error using row and column alone when map distance in metres
  is available.

### Step 10: Define battery and compute costs

Task: Create transparent simulation costs for rover actions.

How:

- Assign cost units to movement, image capture, feature extraction, matching,
  replanning, waiting, and return travel.
- Use 650 cost units as the nominal budget and 430 as the limited-energy test.
- Measure image-processing runtime and memory on the available computer.
- Record image size, feature count, and matching operations as compute proxies.
- Explain how the algorithm would be constrained under the declared SHAKTI-
  class assumption.

Output:

- `outputs/battery_compute_cost_equations.md`
- `outputs/tables/action_costs.csv`
- `outputs/tables/localization_compute_cost.csv`

Check:

- Cost units are simulated values, not watt-hours or flight-hardware
  measurements.

### Step 11: Define rover actions and operating rules

Task: State what the simulated rover is allowed to do.

How:

- Include `move`, `capture image`, `localize`, `continue`, `replan`, `return`,
  and `stop`.
- State the conditions that enable each action.
- Reserve enough simulated energy for required return travel.
- Stop or return when localization is unreliable and the declared risk rule is
  reached.
- Keep terrain hazards as fixed input constraints; do not classify them.

Output:

- `outputs/action_space.md`
- `outputs/operating_rules.md`

Check:

- Every policy decision must be traceable to a written rule.

### Step 12: Implement the three comparison policies

Task: Compare how often the rover should localize and correct its route.

How:

- No Visual Correction: follow the initial route while drift accumulates.
- Fixed-Rate Localization: localize after a fixed number of movement steps.
- Adaptive Battery-Aware Localization: localize when predicted error,
  confidence, route deviation, and remaining energy justify the cost.
- Use the same start-goal pair and disturbance sequence for all three policies.

Output:

- `outputs/tables/policy_results.csv`
- `outputs/figures/policy_route_comparison.png`
- `outputs/figures/battery_profiles.png`

Check:

- A policy comparison is fair only when all policies receive the same route and
  disturbance conditions.

### Step 13: Implement route correction, replanning, and return

Task: Respond when the estimated rover position differs from the plan.

How:

- Correct the internal rover position only when localization passes the
  acceptance rules.
- Rejoin the route when cross-track error exceeds the validated threshold.
- Replan from the corrected position if the planned route is no longer valid.
- Estimate the energy needed to return to the start or declared safe endpoint.
- Trigger return or stop before the reserve is exhausted.

Output:

- `outputs/tables/correction_replan_log.csv`
- `outputs/figures/corrected_route_examples.png`

Check:

- A failed visual match must not silently update the rover position.

### Step 14: Run controlled disturbance scenarios

Task: Test whether the policies remain useful when observations or mission
conditions worsen.

How:

- Apply controlled position drift.
- Apply brightness and contrast changes.
- Add image noise and partial masking.
- Use the 430-unit limited-energy case.
- Skip or delay selected localization calls.
- Run the same scenarios in Areas A and B.

Output:

- `outputs/tables/scenario_results.csv`
- `outputs/figures/scenario_comparison.png`

Check:

- Store the random seed and disturbance level so every scenario can be
  reproduced.

### Step 15: Compare areas, policies, and slope cases

Task: Identify which approach provides the best route tracking for its cost.

How:

- Compare localization error, cross-track error, route length, goal success,
  return success, localization count, replans, simulated energy, runtime, and
  memory.
- Develop settings on Area A and test unchanged on Area B, then reverse.
- Compare the 15-degree green baseline with each 16-to-20-degree yellow
  capability case.
- Explain where adaptive localization saves cost and where it fails.

Output:

- `outputs/tables/cross_area_policy_comparison.csv`
- `outputs/tables/slope_case_comparison.csv`
- `outputs/figures/final_policy_comparison.png`

Check:

- Do not combine all yellow cases into one result or call them safe.

### Step 16: Evaluate onboard suitability

Task: Check whether the visual-localization policy is reasonable for constrained
onboard execution.

How:

- Measure median and worst-case localization runtime over repeated runs.
- Record peak memory, feature count, descriptor size, and policy storage size.
- Compare fixed-rate and adaptive policies by total localization calls and
  compute time.
- Discuss suitability under the declared SHAKTI-class assumption without
  claiming flight qualification.

Output:

- `outputs/tables/onboard_compute_comparison.csv`
- `outputs/offline_vs_onboard_execution_plan.md`
- `outputs/software_versions.txt`

Check:

- Separate measured development-computer results from estimated onboard
  implications.

### Step 17: Prepare the final report and presentation

Task: Present the complete visual-localization and route-tracking study.

How:

- Follow the supplied internship report format.
- Include the research question, grid construction, start-goal selection,
  route planning, rover-view generation, visual localization, threshold
  validation, drift model, battery and compute equations, policy rules,
  scenarios, cross-area results, and limitations.
- Use the same map extent, legend, and colour meaning when comparing methods.
- State clearly that hazards were supplied as fixed navigation inputs.

Output:

- `outputs/final_report.pdf` or `outputs/final_report.docx`
- `outputs/final_presentation.pptx`
- `outputs/final_code/`

## Expected Outputs

- Input-role table and historical-values note.
- Raster inventory and input quicklook.
- Georeferenced Area A and B grid-world tables.
- Start-goal records and initial routes.
- Rover-view manifest.
- Visual-match and localization-threshold tables.
- Localization-error and cross-track-error results.
- Battery and compute-cost equations.
- Action space and operating rules.
- No-correction, fixed-rate, and adaptive-policy results.
- Route-correction, replanning, and return logs.
- Scenario and cross-area comparison tables.
- Green-baseline and yellow sensitivity comparison.
- Onboard-compute assessment.
- Reproducible code, final report, and presentation.

## Daily Timeline

| Date | Daily Goal | Output Due By End of Day |
|---|---|---|
| Monday, 22/06/2026 | Set up Python, read all common guides and Intern 2-4 reports, and separate working inputs from historical references. | `software_versions.txt`, input-role table, and historical-values note |
| Tuesday, 23/06/2026 | Inspect all Area A/B rasters and build the two new georeferenced 25 m grid-world tables. | Raster inventory, quicklook, and Area A/B grids |
| Wednesday, 24/06/2026 | Select valid start-goal pairs, plan green-baseline routes, and create yellow sensitivity route cases. | Start-goal table, initial routes, metrics, and route maps |
| Thursday, 25/06/2026 | Generate LROC rover-view proxies and implement ORB plus RANSAC localization with the fallback method. | Rover-view manifest, visual-match table, and match examples |
| Friday, 26/06/2026 | Validate localization thresholds, calculate position/cross-track error, and implement controlled drift. | Acceptance rules, threshold tests, and error plots |
| Monday, 29/06/2026 | Define battery/compute costs, rover actions, operating rules, and the three comparison policies. | Cost equations, action costs, operating rules, and policy code |
| Tuesday, 30/06/2026 | Run no-correction, fixed-rate, and adaptive policies with correction, replanning, return, and stop actions. | Policy results, route comparison, battery profiles, and action logs |
| Wednesday, 01/07/2026 | Run image disturbances, limited-energy tests, delayed localization, and all approved slope sensitivity cases. | Scenario results and slope-case comparison |
| Thursday, 02/07/2026 | Complete cross-area comparison, runtime/memory assessment, final figures, code organization, and report draft. | Cross-area metrics, onboard-compute table, figures, and report draft |
| Friday, 03/07/2026 | Check reproducibility and terminology, correct inconsistencies, and submit the final report and presentation. | Final report, presentation, code, and output inventory |

## Learning References

- Raster reading: [Rasterio Quickstart](https://rasterio.readthedocs.io/en/stable/quickstart.html)
- ORB features: [OpenCV ORB](https://docs.opencv.org/4.x/d1/d89/tutorial_py_orb.html)
- Feature matching: [OpenCV Feature Matching](https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html)
- Geometric verification: [OpenCV Feature Matching and Homography](https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html)
- Template matching: [OpenCV Template Matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
- A* path planning: [Red Blob Games A* Introduction](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- Graph algorithms: [NetworkX Shortest Paths](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
- Python profiling: [Python Profilers](https://docs.python.org/3/library/profile.html)
- SHAKTI processor background: [SHAKTI Processors](https://shakti.org.in/)
- LROC background: [Arizona State University LROC](https://www.lroc.asu.edu/)
