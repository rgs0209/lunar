# COMMON DATASET GUIDE FOR THE COMPUTER-VISION INTERN PROJECTS

## Purpose

This guide explains every dataset and reference file supplied for the two
computer-vision internship projects. Read it before starting the project brief.

The guide is written for a beginner. It explains what each file stores, what
the numbers mean, when each intern should use it, and what must not be claimed
from it.

The package contains prepared crops for two study areas. Do not search for a
different study area or change these bounds after seeing the results.

## Reading Order

Read the package in this order:

1. `DATASET_GUIDE.md` - understand the files.
2. `CONSENSUS_AREA_GUIDE.md` - understand Areas A and B.
3. `APPROVED_THRESHOLDS.md` - understand fixed limits and colour meanings.
4. Your own `PROJECT_BRIEF_CV_INTERN_*.md` - understand the project.
5. Your own `README_inputs.md` - identify the files to open first.
6. The previous intern reports in `reports/` - understand how derived layers
   were produced.
7. Previous code in `reference_material/` - use only when the brief tells you
   to refer to it.

## Big Picture

| Layer group | Simple meaning | Main use |
|---|---|---|
| LROC optical | Grayscale view of the lunar surface | Visual texture and simulated rover-view windows |
| LROC shadow mask | Illuminated, shadowed, or no-data cells | Shadow awareness and valid optical support |
| LOLA terrain | Surface elevation represented on 5 m and 25 m grids | Terrain geometry, slope context, and map coordinates |
| Confidence layers | Earlier fuzzy estimate of data trust | Supporting confidence and uncertainty context |
| Navigation layers | Earlier cost and feasibility products | Fixed route-planning context for CV Intern 2 |
| Region layers | Terrain objects produced by watershed segmentation | Region identity and science-target boundaries |
| Science layers | Earlier regional ranking/context scores | Goal selection, not resource confirmation |

## The Two Projects

### CV Intern 1: Terrain Perception

CV Intern 1 studies whether local orbital-image windows can be used as rover-
view proxies for terrain perception. The main visual inputs are LROC, the LROC
shadow mask, and LOLA terrain support. Confidence and region layers provide
labels or context; they are not replacements for the intern's own validation.

### CV Intern 2: Visual Localization and Route Tracking

CV Intern 2 studies whether a local LROC window can be matched back to the
larger Area A or B reference map to estimate rover position. The intern then
tests route correction under battery and compute limits. This intern does not
perform terrain-hazard detection. Existing feasibility, exclusion, confidence,
and path-cost products are supplied as fixed navigation context.

The two interns work simultaneously. Neither intern waits for the other's
outputs.

## Folder Layout

Each intern folder follows this structure:

```text
PROJECT_BRIEF_CV_INTERN_*.md
README_inputs.md
orientation/
raster_layers/
  Consensus_A/
  Consensus_B/
reference_material/
reports/
```

- `orientation/` contains the common presentation.
- `raster_layers/` contains the actual Area A and B working data.
- `reference_material/` contains selected earlier intern tables and code.
- `reports/` contains the final Intern 2, 3, and 4 reports.
- `package_documentation/` at the package root contains provenance, manifests,
  checksums, validation results, and the consensus-area overview figure.

## Raster Basics

### Raster

A raster is a map made of rows and columns. Each small cell stores a number.
It looks like an image, but the number may represent brightness, elevation,
confidence, cost, a class code, or a region identifier.

### Pixel or Cell

In this guide, pixel and cell both mean one raster location. A 5 m pixel covers
approximately 5 m by 5 m on the working map. A 25 m cell covers approximately
25 m by 25 m.

### Band

A band is one two-dimensional layer inside a raster. Every supplied GeoTIFF in
this CV package has one band.

### GeoTIFF

A `.tif` or GeoTIFF stores the raster values together with map information,
including coordinate reference system, pixel size, and map position.

### CRS and Transform

The coordinate reference system, or CRS, explains how map coordinates relate
to the Moon. The affine transform records where the top-left cell is located
and how cell indices convert to map coordinates. Preserve both when creating
new GeoTIFF outputs.

### Resolution or GSD

Resolution describes the ground distance represented by one cell. Smaller
numbers show finer spatial detail. A 5 m layer has five times as many cells
along each direction as the corresponding 25 m layer.

```text
one 25 m cell = 5 x 5 cells on the aligned 5 m grid
```

This relationship allows coordinates to be transferred between the two grids.
It does not mean that every sensor originally measured the surface at 5 m.

### Continuous Raster

A continuous raster stores measured or calculated numbers such as elevation,
confidence score, or path cost. Arithmetic may be meaningful after checking
units, validity, and no-data.

### Categorical Raster

A categorical raster stores labels such as `0`, `1`, or `2`. The numbers are
codes, not quantities. Do not average category codes with bilinear or cubic
resampling. Use nearest-neighbour handling if resampling is unavoidable.

### No-Data

No-data means that a cell has no usable value. No-data may be stored as `NaN`,
`255`, `-9999`, `0`, or a very large negative number depending on the file.
Always read `src.nodata`; never assume that zero means no-data for every layer.

### Mask

A mask marks whether a condition is present. For example, a shadow mask uses
codes for illuminated, shadowed, and no-data cells.

### Crop or ROI

A crop is a smaller window cut from a larger map. ROI means region of interest.
Areas A and B are fixed crops of the same lunar south-pole source products.

## Consensus Areas

The two areas were selected from groups of Intern 3 science-priority regions
that remained relevant across the earlier confidence, path-cost, and policy
projects. A fixed 2.5 km margin surrounds each target group.

| Property | Area A | Area B |
|---|---:|---:|
| 25 m raster shape | 785 rows x 670 columns | 1204 rows x 1269 columns |
| 5 m raster shape | 3925 rows x 3350 columns | 6020 rows x 6345 columns |
| Approximate physical size | 19.625 km x 16.750 km | 30.100 km x 31.725 km |
| Selected target regions | 8 | 8 |

Use both areas for geographic cross-validation:

```text
Experiment 1: develop on Area A and test on Area B
Experiment 2: develop on Area B and test on Area A
```

Nearby windows from the same area are not independent geographic tests.

## Common Filename Words

### `area_A` and `area_B`

These suffixes identify which consensus crop the file contains.

### `5m` and `25m`

These identify the product-grid cell size. They do not always describe the
original native resolution of the instrument.

### `v4` and `v6`

These identify the submitted version of an earlier intern product. Do not mix
values from older versions unless the project brief specifically requires it.

### `class`

A class file contains integer labels. Read the class legend before using it.

### `continuous`

A continuous file contains a numerical score rather than a discrete label.

### `mask`

A mask marks selected, feasible, excluded, shadowed, or PSR cells.

### `PSR`

PSR means permanently shadowed region. It represents persistent illumination
conditions, not proof of water ice.

### `region_id`

A region identifier is only a unique label for one segmented terrain object.
Region 8000 is not physically larger or better than Region 4000 merely because
its number is higher.

### `rank`

Rank 1 is better than Rank 2 in the submitted science-priority ordering. Rank
is an order, not a physical measurement.

## Perception and Terrain Files

### `lroc_5m_area_A.tif` and `lroc_5m_area_B.tif`

**Simple meaning:** These are the main grayscale LROC optical crops.

**Source:** Lunar Reconnaissance Orbiter Camera optical product prepared on the
5 m working grid.

**Data type and no-data:** `float32`; no-data is a very large negative value
near `-3.4e38`.

**What each value means:** A valid value represents optical brightness or
reflectance-like image intensity. Higher brightness is not automatically safer,
higher, rougher, or more scientifically valuable.

**How CV Intern 1 uses it:** Extract local observation windows; calculate
gradients, edges, contrast, texture, keypoints, and visual confidence. Call each
window a `simulated local observation` or `rover-view proxy`.

**How CV Intern 2 uses it:** Use the full area crop as the reference map and
smaller windows as simulated rover views. Match the small window back to the
reference image using ORB/RANSAC and a template-matching fallback.

**Allowed processing:** Valid-data masking, local contrast adjustment,
normalization for an algorithm, controlled blur/noise/illumination tests, and
window extraction. Record every preprocessing operation.

**What not to claim:** This is not a real rover-camera frame. It lacks rover
camera perspective, wheel-height viewpoint, occlusion, motion blur, and actual
onboard camera calibration. LROC brightness alone does not prove composition,
ice, elevation, or safety.

**Common mistake:** Treating dark pixels as topographic depressions. Darkness
may be caused by illumination and shadow.

**Beginner analogy:** This is the large reference photograph from which the
computer extracts and matches smaller pieces.

### `lroc_shadow_mask_5m_area_A.tif` and `lroc_shadow_mask_5m_area_B.tif`

**Simple meaning:** These files mark illumination state on the 5 m grid.

**Data type:** `uint8`, categorical.

**Codes:**

| Value | Meaning |
|---:|---|
| `0` | Illuminated; retain as valid optical support |
| `1` | Shadow |
| `255` | No-data; exclude |

**How CV Intern 1 uses it:** Calculate shadow fraction inside each local
window, distinguish low visual information from genuine texture, and report
results separately for illuminated and shadowed observations.

**How CV Intern 2 uses it:** Mark visual-localization tests by illumination
condition and measure whether matching fails more often in shadowed windows.

**Allowed processing:** Count real 5 m codes or aggregate shadow fraction. If
the categorical raster is ever resampled, use nearest neighbour.

**What not to claim:** Shadow does not prove water ice. A single shadow product
also does not describe every future illumination condition.

**Common mistake:** Inverting the codes. The correct rule is `0=illuminated`
and `1=shadow`.

**Beginner analogy:** This is a labelled transparency placed over the optical
image to show which cells are dark.

### `lola_5m_area_A.tif` and `lola_5m_area_B.tif`

**Simple meaning:** These are LOLA-derived elevation values represented on the
same 5 m geometry as LROC.

**Source and resolution warning:** The file was matched to the LROC 5 m grid.
The 5 m representation is not a new native 5 m LOLA measurement.

**Data type and no-data:** `float32`; no-data is near `-3.4e38`.

**What each value means:** Valid values are elevation in metres in the source
vertical reference.

**How CV Intern 1 uses it:** Provide terrain support and derive reference slope
or local elevation variation for labels and validation. Do not use elevation as
an optical feature.

**How CV Intern 2 uses it:** Check map geometry and relate 5 m visual windows to
the terrain beneath them. The route itself remains on the 25 m decision grid.

**Allowed processing:** Terrain derivatives, local statistics, aligned window
extraction, and comparison with LROC geometry.

**What not to claim:** Do not report 5 m represented cells as independent 5 m
altimeter measurements.

**Beginner analogy:** This is a height sheet placed beneath the optical image.

### `lola_25m_area_A.tif` and `lola_25m_area_B.tif`

**Simple meaning:** These are the elevation crops on the main 25 m decision
grid.

**Role:** This is the reference geometry for confidence, region, science,
cost, target, and navigation layers.

**Data type and no-data:** `float32`; no-data is near `-3.4e38`.

**How CV Intern 1 uses it:** Evaluate slope-based ground-reference classes and
place perception outputs onto the 25 m grid.

**How CV Intern 2 uses it:** Build Area A and B grid worlds, convert row/column
indices to coordinates, and associate visual-localization estimates with route
cells.

**Approved interpretation:** Mean slope up to 15 degrees is the green baseline.
Limits 16, 17, 18, 19, and 20 degrees are separate yellow manageable-risk
capability tests. They must not be called safe.

**Common mistake:** Treating a historical `feasible` cell as green-safe without
checking the approved 15-degree rule.

## Confidence and Navigation Files

### `confidence_class_25m_v4_area_A.tif` and `confidence_class_25m_v4_area_B.tif`

**Simple meaning:** These files store Intern 2's fuzzy data-confidence class.

**Data type:** `uint8`, categorical. The file metadata uses class `3` as
no-data/invalid.

| Value | Meaning |
|---:|---|
| `0` | Low confidence |
| `1` | Medium confidence |
| `2` | High confidence |
| `3` | Insignificant/invalid; required inputs were unavailable |

**How CV Intern 1 uses it:** Compare perception reliability with the earlier
data-confidence class. It may support an uncertainty label, but it is not the
ground truth for visual hazard classification.

**How CV Intern 2 uses it:** Record whether a localization result occurs in a
low-, medium-, high-, or invalid-confidence map cell. Do not use it as the
visual match confidence itself.

**Threshold source:** Read `APPROVED_THRESHOLDS.md`. The controlling confidence
boundaries are 0.35 and 0.65.

**Common mistake:** Assuming class `2` means safe terrain. It means high data
confidence under the earlier fuzzy model.

### `confidence_continuous_25m_v4_area_A.tif` and `confidence_continuous_25m_v4_area_B.tif`

**Simple meaning:** These files store the continuous fuzzy confidence score
before class conversion.

**Data type and no-data:** `float32`; no-data is `NaN`.

**Observed packaged range:** Approximately 0.153 to 0.847 in both areas.

**How to use it:** Use it as supporting uncertainty context, compare results
across confidence ranges, or include it as a soft route-context value.

**What not to claim:** It is not a calibrated probability. A value of 0.80 does
not prove an 80% probability of correctness or safety.

**Common mistake:** Mixing this score with CV Intern 2's own visual matching
confidence. Give the two quantities different column names.

### `path_cost_25m_v6_area_A.tif` and `path_cost_25m_v6_area_B.tif`

**Simple meaning:** These files store Intern 2's earlier per-cell path cost.

**Data type and no-data:** `float32`; no-data is `NaN`.

**Observed packaged range:** Area A is approximately 0.005 to 1.847; Area B is
approximately 0.003 to 1.847 for finite cells.

**Interpretation:** Lower finite values were preferred by the submitted path
planner. The score combined terrain, shadow, roughness, and confidence context.

**How CV Intern 1 uses it:** Normally not a primary perception input. It may be
used only for later comparison between perception results and route context.

**How CV Intern 2 uses it:** Use it as the fixed base cost for A* or Dijkstra
route construction. Add separately declared battery costs for image capture,
localization, replanning, and return travel.

**What not to claim:** This is dimensionless model cost, not joules, watt-hours,
or measured rover energy. It was produced using earlier operating assumptions
and is not a safety certificate.

### `feasible_mask_25m_v6_area_A.tif` and `feasible_mask_25m_v6_area_B.tif`

**Simple meaning:** These files mark cells considered feasible by the submitted
Intern 2 model.

**Data type:** `uint8`, categorical.

| Value | Meaning |
|---:|---|
| `0` | Excluded by the submitted model |
| `1` | Feasible under the submitted model |
| `255` | Reserved no-data value |

**How CV Intern 2 uses it:** Use it to define the historical navigation domain
and to avoid cells where the submitted cost is undefined.

**Supervisor correction:** A value of `1` does not automatically mean green-
safe. Apply the approved green baseline of slope up to 15 degrees. Test limits
16 through 20 degrees separately in yellow.

**Common mistake:** Reporting the percentage of value `1` cells as the final
safe area.

### `exclusion_mask_25m_v4_area_A.tif` and `exclusion_mask_25m_v4_area_B.tif`

**Simple meaning:** These files explain Intern 2's historical exclusion
categories.

**Data type:** `uint8`, categorical.

| Value | Historical meaning |
|---:|---|
| `0` | Traversable under the submitted Intern 2 assumptions |
| `1` | Slope-null/steep category in the old model (`>30 degrees`) |
| `2` | Insignificant/invalid confidence data |
| `255` | Reserved GeoTIFF no-data value |

Area A happens to contain only valid codes 0 and 1. Area B contains 0, 1, and
2. This difference does not mean that either file is broken.

**How CV Intern 2 uses it:** Use the codes to understand why historical path
cost may be unavailable. Do not rebuild CV Intern 1's hazard classes from this
file.

**Supervisor correction:** Code `0` follows an old model and must not be called
green-safe. The approved green limit is 15 degrees.

### `psr_binary_25m_area_A.tif` and `psr_binary_25m_area_B.tif`

**Simple meaning:** These are Intern 3's annual-illumination PSR masks.

**Data type:** `uint8`, categorical; no-data is `255`.

| Value | Meaning |
|---:|---|
| `0` | Not classified as PSR |
| `1` | PSR under the submitted annual-illumination rule |
| `255` | No-data |

The submitted PSR rule used annual illumination fraction below 0.001. Read the
approved threshold file before using the mask.

Area A contains only code `0` in the supplied crop. Area B contains codes `0`
and `1`. Do not invent PSR cells in Area A merely to balance the experiment.

**What not to claim:** A PSR cell is not confirmed water ice. This mask is a
submitted intern-derived product and should be checked against authoritative
illumination products before mission claims.

## Region and Science Files

### `accepted_regions_psr_only_25m_area_A.tif` and `accepted_regions_psr_only_25m_area_B.tif`

**Simple meaning:** These files store Intern 3's accepted watershed-region IDs.

**Data type:** `int32`, categorical identifiers; `0` is background/no accepted
region.

**What each positive value means:** Every positive integer identifies one
terrain region. All cells with the same number belong to the same accepted
region.

**How CV Intern 1 uses it:** Group local-window results by terrain region and
avoid splitting geographic validation randomly across cells from the same
region.

**How CV Intern 2 uses it:** Identify region boundaries, associate goals with
regions, and summarize route visits by region.

**What not to do:** Do not average region IDs, normalize them, use them as a
science score, or assume larger ID numbers are better.

### `science_composite_regions_25m_area_A.tif` and `science_composite_regions_25m_area_B.tif`

**Simple meaning:** These files map Intern 3's regional science-composite score
back onto accepted region cells.

**Data type and no-data:** `float32`; no-data is `NaN`.

**Observed packaged ranges:** Approximately 0.023 to 0.296 in Area A and 0.016
to 0.318 in Area B.

**How CV Intern 1 uses it:** Normally context only. Do not use science score as
a terrain-safety label.

**How CV Intern 2 uses it:** Support goal selection or report science context
along a route. The supervisor-selected goal mask remains the direct goal input.

**What not to claim:** The score combines submitted spectral and radar-context
evidence. It does not confirm ice, hydration, minerals, or resource abundance.

### `science_rank_regions_25m_area_A.tif` and `science_rank_regions_25m_area_B.tif`

**Simple meaning:** These files store the submitted rank for accepted regions.

**Data type and no-data:** `int16`; no-data is `-9999`.

**Interpretation:** Lower positive values are higher ranked. Rank is ordinal:
the numerical distance between Rank 2 and Rank 20 is not a physical quantity.

**How CV Intern 2 uses it:** Compare routes or goals by submitted priority.
Use it only after applying the approved accessibility and slope interpretation.

**Common mistake:** Displaying rank with a colour scale where larger values
look better. Reverse the visual ordering or label it clearly.

### `consensus_goal_mask_25m_area_A.tif` and `consensus_goal_mask_25m_area_B.tif`

**Simple meaning:** These files mark the supervisor-selected target-region
groups used to define Areas A and B.

**Data type:** `uint8`, categorical; no-data is `255`.

| Value | Meaning |
|---:|---|
| `0` | Other cell in the crop |
| `1` | Cell belongs to one selected target region |
| `255` | Reserved no-data value |

**How CV Intern 1 uses it:** Use only to identify the study-target context. It
is not a hazard label.

**How CV Intern 2 uses it:** Select candidate goal cells. Record the selected
region ID and coordinate; do not silently choose a new goal outside the mask.

### `science_targets_area_A.csv` and `science_targets_area_B.csv`

**Simple meaning:** Each CSV contains the eight selected target-region records
for that area.

**Important column groups:**

| Column group | Examples | Meaning |
|---|---|---|
| Identity | `region_id`, `rank` | Region label and submitted order |
| Geometry | `centroid_row`, `centroid_col`, `geo_x`, `geo_y`, `bbox_*` | Pixel and map location |
| Terrain | `slope_mean_deg`, `slope_std_deg`, `slope_max_deg`, `roughness_*` | Region terrain summaries |
| Illumination | `shadow_fraction`, `psr_fraction`, `dist_to_psr_km` | Shadow and PSR context |
| Coverage | `lola_valid_pct`, `dfsar_valid_pct`, `minirf_valid_pct`, `m3_valid_pct` | Valid data support |
| Science context | `Science_Composite`, `Evidence_Convergence_Count`, `evidence_band` | Submitted regional ranking evidence |

**How CV Intern 1 uses it:** Identify region boundaries and stratify evaluation
by terrain and illumination context.

**How CV Intern 2 uses it:** Select and record route goals. Use coordinates and
region IDs rather than copying a start/goal cell from Intern 4's old grid.

**What not to do:** Do not treat blank cells as zero measurements. Do not use
the CSV as pixel-level ground truth. Do not claim its spectral indicators prove
resources.

## How the Layers Connect

```text
LROC 5 m + shadow 5 m + LOLA terrain
                |
                +--> CV Intern 1 local perception and confidence

LROC local window + LROC area reference
                |
                +--> CV Intern 2 visual localization

LOLA 25 m + historical feasibility/path cost + goal mask
                |
                +--> CV Intern 2 route tracking and battery-aware correction

Accepted region IDs + science rank/composite + target CSV
                |
                +--> common regional and goal context
```

The package intentionally does not duplicate raw M3, Mini-RF, DFSAR, or GRAIL
rasters. Their earlier evidence is already represented in confidence, region,
and science-context products. The CV interns do not need to recreate the prior
fusion, confidence, or science-ranking projects.

## Approved Slope Display

Both interns must use the same visual language:

| Mean slope | Colour | Meaning |
|---|---|---|
| Up to 15 degrees | Green | Safe/acceptable baseline |
| Above 15 through 20 degrees | Yellow | Manageable-risk rover-capability test; not safe |
| Above 20 degrees | Red | High risk/unsafe |

Run 16, 17, 18, 19, and 20 degrees as separately labelled sensitivity cases.
Do not merge them into the green baseline.

## Previous Intern Reports

### `report_lunar_project-7.pdf`

Intern 2 report on confidence classes, path-cost construction, and classical
path planning. Use it to understand the supplied confidence and cost files.
The final approved threshold reference in this package controls any conflicting
working-note values.

### `main.pdf`

Intern 3 report on watershed regions, accessibility screening, science context,
and target ranking. Use it to understand accepted region IDs, science scores,
rank, PSR, and target CSV columns.

### `report.pdf`

Intern 4 report on grid-world policy, energy scenarios, Q-learning, compute
cost, and mission resilience. CV Intern 2 may use it as a method reference.
Do not reuse the old 200 x 200 grid, fixed start/goal cells, or the 20-degree
connectivity workaround as the green-safe limit.

## Reference Material Folders

### CV Intern 1

The supplied Intern 2 tables explain confidence classes and path constraints.
The supplied Intern 3 ranking and target tables explain the selected regions.
Intern 4 policy code is intentionally omitted because it is not needed for the
perception project.

### CV Intern 2

Intern 2 material supports fixed cost/confidence interpretation. Intern 3
material supports goal selection. Intern 4 scripts are examples of grid-world,
policy, scenario, and compute-cost implementation. They contain old paths and
assumptions; adapt the method rather than running them unchanged.

## Reference Files From Intern 2

These files describe earlier confidence and path-cost work. They are supporting
material, not new ground truth.

### `confidence_class_table_v4.csv`

This table summarizes how many cells belonged to the earlier low, medium, and
high confidence classes and gives score statistics for each class. Use it to
understand the codes in `confidence_class_25m_v4_area_*.tif`. Do not calculate
new class limits from the cell counts.

### `path_constraints_table.csv`

This table records the constraints used in an earlier navigation experiment.
Some limits are historical and conflict with the final supervisor-approved
slope display. Use it to understand provenance only. For the CV projects, the
green baseline remains 15 degrees.

### `path_cost_table_v6.csv`

This table summarizes the number and percentage of cells in earlier path-cost
categories. It helps explain `path_cost_25m_v6_area_*.tif`, but it does not
provide measured energy or a new safety threshold.

### `classical_path_metrics_v6_multi.csv`

This table compares earlier shortest and safer paths using length and risk
proxies. CV Intern 2 may use its column structure as an example when designing
new comparison tables. Do not copy its routes because they are not the new
Area A and B visual-localization experiments.

### `constrained_path_cost_equation.md`

This note explains the earlier mathematical path-cost equation. It contains
historical normalisation values and a 30-degree feasibility rule. Read it to
understand how the supplied cost raster was created; do not replace the
approved 15-degree green baseline with that historical rule.

## Reference Files From Intern 3

These files describe earlier terrain-region screening and science ranking.

### `accessibility_quantities (1).csv`

Each row represents one watershed terrain region. Columns include region area,
slope, roughness, elevation, shadow, PSR distance, radar coverage, and the
earlier qualification status. Use region identifiers and geometry as context.
Do not treat `qualification_status` as a pixel-level CV label.

### `rover_accessibility_constraints (1).csv`

This table records the earlier region-screening rules and their cited reasons.
Its 20-degree value was used in that submitted stage. It is not the green-safe
limit for the CV projects; retain 15 degrees as green and show 16 through 20
degrees only as separate yellow capability tests.

### `constraint_sensitivity_results.csv`

This table shows how the earlier number and ranking of candidate regions
changed when scoring assumptions were varied. It is useful for understanding
sensitivity analysis, not for training a CV model.

### `science_priority_ranked.csv`

This is the earlier full ranked-region table. It contains terrain, shadow,
radar, spectral, gravity-context, science-score, and rank columns. CV Intern 2
may use the selected region IDs and coordinates for goal selection. Neither
intern should use the science score as a hazard label or resource truth.

### `science_targets_area_A.csv` and `science_targets_area_B.csv`

These are the selected rows from the full ranking table that fall inside the
two fixed consensus areas. Each contains eight targets. The same filenames also
appear beside the rasters because they are direct working inputs there.

## Reference Files From Intern 4

These files are supplied only to CV Intern 2 as examples of policy, battery,
scenario, and compute-cost implementation. They were produced on an old 200 by
200 grid and are not georeferenced working inputs for Areas A and B.

### `grid_world.csv` and `grid_world.npy`

These store the earlier simulated grid in table and NumPy forms. They include
terrain risk, shadow risk, confidence, science reward, movement cost, and old
start/goal flags. Study their data structure, then build a new georeferenced
Area A/B environment from the supplied rasters. Do not reuse the old grid.

### `grid_cell_properties.csv`

This is a more detailed version of the old grid table with cell coordinates,
terrain zones, risk categories, costs, and distance-to-goal fields. Its labels
and start/goal cells belong to the historical experiment.

### `baseline_policy_results.csv`

This table records earlier shortest-path, safest-path, and related baseline
results. Its columns are useful examples for reporting success, path length,
energy proxy, science return, runtime, and exposure. Recalculate every value on
the new Area A/B environment.

### `q_learning_summary.csv`

This table summarizes the earlier Q-learning training and evaluation. It can
help CV Intern 2 understand which learning settings and compute statistics were
reported. It is not a trained policy for the new project.

### `scenario_results.csv`

This table records earlier tests for sensor dropout, blocked paths, limited
energy, wrong resource estimates, terrain changes, and communication delay.
Use its experiment-table style as a reference when defining the new
localization and route-correction disturbances.

### `resilience_metrics.csv`

This table combines earlier policy results across scenarios. It illustrates
how success rate, recovery, energy, runtime, and policy size can be compared.
Its numerical values do not transfer to Areas A and B.

### `step9_baseline_policies.py`

This script implements earlier baseline path policies. It contains an old
20-degree passability setting and old paths. Reuse only general algorithmic
ideas after replacing paths, grids, thresholds, and inputs.

### `q_learning_updated.py`

This script implements the earlier offline Q-learning experiment. It is useful
for understanding states, actions, rewards, training, and evaluation. The new
CV2 project should first establish classical visual-localization and route-
correction baselines; Q-learning is optional unless required by the brief.

### `step11_policy_compute_cost.py`

This script shows how runtime, memory, and policy size were compared. Adapt
these measurements to the new visual-matching and correction policies.

### `step12_scenario_tests.py`

This script shows how earlier failure scenarios were automated. Replace the
old scenarios with the approved CV2 disturbances, such as image noise,
illumination change, partial masking, position drift, and limited battery.

### `mission_resilince.py`

Despite the spelling in the filename, this script calculates and plots earlier
mission-resilience comparisons. Keep the filename unchanged so references do
not break. Use the method as an example, not its old numerical results.

## Package Documentation Files

These files describe how this package was assembled and checked.

- `roi_manifest.csv` records Area A/B crop bounds, grid sizes, and target
  counts.
- `layer_inventory.csv` records each prepared raster layer and its source.
- `file_inventory.csv` lists packaged files for completeness checking.
- `provenance.json` records where the packaged products came from.
- `VALIDATION_REPORT.md` records structural and raster validation results.
- `INTERN_OUTPUTS_NAVIGATOR.md` explains where the earlier intern outputs were
  located in their original submissions.
- `consensus_areas_overview.png` shows the two selected geographic areas.

## What Not To Do

- Do not change the Area A or B bounds after seeing results.
- Do not overwrite supplied raster files.
- Do not treat no-data values as real measurements.
- Do not invert the shadow mask; `0` is illuminated and `1` is shadow.
- Do not average categorical masks, classes, ranks, or region IDs.
- Do not call a historical feasible-mask cell green-safe without applying the
  approved 15-degree rule.
- Do not label 16-to-20-degree terrain safe; it is yellow manageable risk.
- Do not use science score or rank as a terrain-hazard label.
- Do not call LROC windows real rover-camera images.
- Do not claim PSR, CPR, radar score, or M3 context proves water ice.
- Do not claim path cost is measured rover energy.
- Do not call continuous confidence a calibrated probability.
- Do not reuse Intern 4's 200 x 200 grid or fixed start/goal cells.
- Do not use nearby windows from one area as independent geographic tests.

## Suggested First Exercise: Both Interns

1. Open the Area A and Area B `lola_25m` files with Rasterio.
2. Print shape, CRS, transform, resolution, data type, and no-data.
3. Open the corresponding `lroc_5m` files and repeat the check.
4. Confirm that each 5 m shape is five times the 25 m shape along both axes.
5. Plot the LROC, LOLA, confidence class, accepted regions, and goal mask.
6. Write one sentence explaining what each plotted value means.
7. Save the results in the intern's own `outputs/` folder.

## Suggested First Exercise: CV Intern 1

1. Choose one illuminated and one shadowed LROC window in Area A.
2. Calculate brightness mean, contrast, gradient magnitude, edge density, and
   shadow fraction for each window.
3. Find the corresponding 25 m cells and record slope and confidence context.
4. Repeat the same procedure in Area B without changing the feature formulas.
5. Explain which visual differences are caused by shadow and which may be
   caused by terrain texture.

## Suggested First Exercise: CV Intern 2

1. Select one valid route cell in Area A.
2. Extract a small LROC window around that true simulated position.
3. Search for the window inside a larger reference window using normalized
   cross-correlation.
4. Report the true row/column, estimated row/column, and position error.
5. Repeat after adding mild noise, contrast change, and partial masking.
6. Repeat in Area B using the same settings.

## Beginner Raster Inspection Example

```python
from pathlib import Path

import numpy as np
import rasterio

path = Path("raster_layers/Consensus_A/lola_25m_area_A.tif")

with rasterio.open(path) as src:
    data = src.read(1)
    nodata = src.nodata
    print("Shape:", data.shape)
    print("CRS:", src.crs)
    print("Transform:", src.transform)
    print("Resolution:", src.res)
    print("Data type:", src.dtypes[0])
    print("No-data:", nodata)

valid = np.isfinite(data)
if nodata is not None and np.isfinite(nodata):
    valid &= data != nodata

print("Valid cells:", int(valid.sum()))
print("Minimum:", float(data[valid].min()))
print("Maximum:", float(data[valid].max()))
```

Do not load many large 5 m rasters at the same time. Read one window at a time
when possible.

## Converting Between 25 m and 5 m Grid Indices

Because the grids are aligned:

```python
row25, col25 = 100, 200

row5_start = row25 * 5
col5_start = col25 * 5

# The corresponding 25 m footprint occupies these 5 m cells:
rows5 = slice(row5_start, row5_start + 5)
cols5 = slice(col5_start, col5_start + 5)
```

This conversion is valid for the supplied aligned crops. Still verify the CRS
and transform before using it in a new product.

## Troubleshooting

### The raster looks completely black

The display range may include an extreme no-data value. Mask no-data first and
display only valid values, possibly using percentile-based limits.

### The raster looks white or empty

Check whether the selected window contains valid data. Print the no-data value,
finite count, minimum, and maximum.

### Two files have different shapes

Check whether one is 5 m and the other is 25 m. Do not resize blindly. Use the
known 5-to-1 grid relationship or geospatial coordinates.

### A categorical map contains unexpected colours

Use a discrete colour map and an explicit legend. Do not use a continuous
colour scale for region IDs or class codes.

### Area A PSR contains no value `1`

This is expected in the packaged Area A crop. Do not fabricate PSR cells.

### Path cost contains NaN

NaN marks cells where the submitted model did not define usable path cost.
Check feasibility, exclusion, and confidence layers.

### ORB finds too few matches

Record the failure. Try the approved fallback method, controlled contrast
normalization, or template matching. Do not lower acceptance thresholds after
seeing the test-area answer without documenting and validating the change.

### The old Intern 4 script does not run

The script may contain old Windows paths, old grid dimensions, or a RAD750
assumption. Rebuild paths and grids from the files in the current package and
use the declared SHAKTI-class compute assumption.

## Glossary

| Term | Simple meaning |
|---|---|
| A* | Path algorithm that combines accumulated cost with estimated distance to goal |
| CRS | Coordinate system used to place the raster on the lunar map |
| Cross-track error | Distance between estimated rover position and planned route |
| GeoTIFF | Raster file containing values and map metadata |
| GSD | Approximate ground distance represented by one raster cell |
| LOLA | Lunar Orbiter Laser Altimeter; terrain/elevation source |
| LROC | Lunar Reconnaissance Orbiter Camera; optical-image source |
| No-data | Cell without a usable measurement or model result |
| ORB | Feature detector and descriptor used for image matching |
| PSR | Permanently shadowed region |
| RANSAC | Robust method that rejects bad feature matches while fitting a model |
| Raster | Grid of map cells containing values or labels |
| ROI | Region of interest |
| Template matching | Searching a larger image for the best match to a smaller image |
| Watershed region | Terrain object formed by segmentation around terrain boundaries |

## Learning References

- Raster reading: [Rasterio Quickstart](https://rasterio.readthedocs.io/en/stable/quickstart.html)
- Computer vision: [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- ORB feature matching: [OpenCV Feature Matching](https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html)
- Template matching: [OpenCV Template Matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
- Robust model fitting: [OpenCV Homography](https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html)
- LROC background: [Arizona State University LROC](https://www.lroc.asu.edu/)
- LOLA background: [NASA LOLA](https://lola.gsfc.nasa.gov/)
- Lunar Reconnaissance Orbiter: [NASA LRO](https://science.nasa.gov/mission/lro/)
- Basic GIS: [QGIS Training Manual](https://docs.qgis.org/latest/en/docs/training_manual/)
