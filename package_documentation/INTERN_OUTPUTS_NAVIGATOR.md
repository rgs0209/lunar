# INTERN OUTPUTS NAVIGATOR

## Purpose

Use this file to navigate the submitted outputs from Interns 2, 3, and 4 in `Intern_outputs/`.

The mapping below follows the approved project briefs step by step. It is based on a surface-level inspection of filenames, folders, table headers, script headers, and report names. It does not validate the scientific correctness of every equation, threshold, map, or result.

## Status Labels

- **FOUND**: The requested deliverable is present.
- **RENAMED**: The deliverable is present under a different filename or extension.
- **PARTIAL**: Some evidence or code is present, but one or more required files are missing.
- **NOT LOCATED**: The requested deliverable was not found in the submitted folder.
- **OLDER VERSION**: Retained for history; do not use as the current result unless comparing revisions.

## Quick Overview

| Intern | Submitted files | Approximate size | Main organization |
|---|---:|---:|---|
| Intern 2 | 200 | 1.3 GB | notebooks, outputs, figures, reports, and many versioned revisions |
| Intern 3 | 38 | 118 MB | scientific-stage folders plus one final script and notebook |
| Intern 4 | 29 | 21 MB | scripts, grid-world tables, policy results, Q-learning results, and scenario tests |

## Recommended Reading Order

1. Read the relevant step table in this navigator.
2. Open the recommended current result, not the first similarly named file.
3. Use notebooks/scripts to understand how an output was produced.
4. Use figures for visual interpretation only after checking the corresponding CSV or method file.
5. Treat files marked `draft`, `review`, or older version numbers as supporting history.

# Intern 2: Confidence Classes and Path Planning

## Main Entry Points

- Report draft: `Intern-2_outputs/ppts/reports/report_lunar_project_draftv1.pdf`
- Report source: `Intern-2_outputs/ppts/reports/report_draft1.tex`
- Fuzzy method: `Intern-2_outputs/outputs/confidence_rules.md`
- Path-cost equation: `Intern-2_outputs/outputs/constrained_path_cost_equation.md`
- Notebooks: `Intern-2_outputs/notebooks/`
- Current figures: `Intern-2_outputs/figures/`

## Version Guidance

Use the following versions as the current submitted branch:

- Confidence classes: `v4`
- Path-cost surface: `v6`
- Multi-region classical path comparison: `v6_multi`
- Step 11 path figures: `figures/step11_path_v6/`

Version numbers belong to individual output families. For example, confidence `v4` is current while path-cost `v4` is older than path-cost `v6`. Keep earlier files for comparison, but do not mix values across version families.

## Step-by-Step Navigation

| Plan Step | Required work | Status | Submitted files to open |
|---:|---|---|---|
| 1 | Read and describe input files | **FOUND** | `outputs/file_description_table.csv`; `outputs/file_role_summary.md`; `notebooks/step1_describe_files.ipynb` |
| 2 | Create terrain-risk features | **FOUND** | `outputs/terrain_features.csv`; `figures/slope_risk_map.png`; `figures/roughness_map_5m.png`; `notebooks/step2_terrain_features.ipynb` |
| 3 | Create shadow-risk feature | **FOUND** | `figures/shadow_risk_map.png`; `figures/shadow_risk_map_25m.png`; `notebooks/step_3_shadow_risk.ipynb` |
| 4 | Create radar data-support features | **FOUND** | `outputs/data_support_table.csv`; `figures/data_support_map.png`; `figures/radar_support_combined.png`; `notebooks/step4_radar_coverage.ipynb` |
| 5 | Record optional destination context | **FOUND** | `outputs/destination_context_note.md`; `figures/m3_broad_context.png`; `notebooks/step5_optional_destination_context.ipynb` |
| 6 | Define fuzzy confidence rules | **RENAMED** | Brief expected `confidence_rules.txt`; submitted as `outputs/confidence_rules.md`. Supporting notebook: `notebooks/step6_confidence_rules.ipynb` |
| 7 | Assign confidence classes | **FOUND** | Current branch: `outputs/confidence_class_table_v4.csv`, `outputs/confidence_class_25m_v4.tif`, `outputs/confidence_continuous_25m_v4.tif`, `figures/confidence_class_map_v4.png`, `figures/confidence_continuous_map_v4.png`; notebook: `notebooks/step7_fuzzy_confidence_classes.ipynb` |
| 8 | Define rover navigation constraints | **FOUND** | `outputs/path_constraints_table.csv`; `figures/feasible_navigation_area_map.png`; `figures/exclusion_categories_v4.png`; `notebooks/step8_rover_navigation_constraints.ipynb` |
| 9 | Define constrained path-cost equation | **RENAMED** | Brief expected `.txt`; submitted as `outputs/constrained_path_cost_equation.md`; notebook: `notebooks/step9_path_cost_equation.ipynb` |
| 10 | Generate path-cost map | **FOUND** | Current branch: `figures/path_cost_map_v6.png`, `outputs/path_cost_table_v6.csv`, `outputs/path_cost_25m_v6.npy`; notebook: `notebooks/step10_generation_path_cost_map.ipynb` |
| 11 | Run classical path planning | **FOUND** | `outputs/classical_path_metrics_v6_multi.csv`; `figures/step11_path_v6/`; `figures/step11_window_preview_v6.png`; `notebooks/draft_step11_classical_path_planning.ipynb` |
| 12 | Formulate QAOA path planning | **NOT LOCATED** | No `qaoa_path_formulation.md` found |
| 13 | Formulate Grover-based path search | **NOT LOCATED** | No `grover_path_search_formulation.md` found |
| 14 | Test quantum-inspired evolutionary path planning | **NOT LOCATED** | No quantum-genetic result image or metrics file found |
| 15 | Compare classical and quantum methods | **NOT LOCATED** | No `path_method_comparison.csv` or comparison plot found |
| 16 | Prepare final report and presentation | **PARTIAL** | A 44-page draft report is present: `ppts/reports/report_lunar_project_draftv1.pdf`. Review PDFs are in `ppts/`. No final PPTX was located |

## Files to Avoid Mixing

- `confidence_class_map.png`, `_v2`, `_v3`, and `_v4` are different iterations.
- `path_cost_map.png`, `_v4`, `_v5`, and `_v6` are different iterations.
- `step11_multi/`, `step11_path_psr/`, and `step11_path_v6/` represent different path-planning branches.
- `report_changes/` contains later replacement assets and should not be treated as a complete separate pipeline.

## Main Missing Deliverables

- QAOA formulation.
- Grover formulation.
- Quantum genetic or quantum-inspired evolutionary result.
- Classical-versus-quantum comparison table and plot.
- Final presentation file.
- A clearly labelled final report replacing the current draft name.

# Intern 3: Rover-Accessible Science Priority Mapping

## Main Entry Points

- Final notebook: `Intern-3_outputs/THE FINAL SCRIPT AND IPYNB/FINAL.ipynb`
- Consolidated script: `Intern-3_outputs/THE FINAL SCRIPT AND IPYNB/ALL STEPS - FINAL PIPELINE.py`
- Candidate-region stage: `Intern-3_outputs/Candidate_Regions/`
- Accepted-region stage: `Intern-3_outputs/Accepted_Outputs/`
- Science scoring and ranking: `Intern-3_outputs/Science_Scoring_and_Ranking/`

## Branch Guidance

The submitted folder contains both general candidate-region outputs and a later `psr_only` branch. The consolidated pipeline identifies the PSR-only branch as its final branch. Use these as the primary accepted-region files:

- `candidate_region_qualification_psr_only.csv`
- `accepted_candidate_regions_psr_only.csv`
- `Accepted_Outputs/accepted_candidate_regions_psr_only.tif`
- `Accepted_Outputs/accepted_candidate_regions_map_psr_only.png`

Files containing `(1)` are submitted-copy filenames, not necessarily scientific version numbers.

## Step-by-Step Navigation

| Plan Step | Required work | Status | Submitted files to open |
|---:|---|---|---|
| 1 | Read and describe input files | **RENAMED** | `file_description_table (1).csv` |
| 2 | Approve minimum mapping unit | **PARTIAL** | The `0.0784 km2` minimum area, corresponding to `280 m x 280 m`, is implemented in the final script/notebook. The required `target_region_size_justification.md` and `target_region_approval_record.md` were not located |
| 3 | Generate watershed candidate regions | **PARTIAL** | `Candidate_Regions/watershed_candidate_regions (1).tif`; `Candidate_Regions/candidate_regions_map (1).png`; `candidate_regions (1).csv`. The required standalone `watershed_method_parameters.md` was not located |
| 4 | Qualify and accept candidate regions | **FOUND** | Primary branch: `candidate_region_qualification_psr_only.csv`, `accepted_candidate_regions_psr_only.csv`, `uncertain_candidate_regions_psr_only.csv`, and files in `Accepted_Outputs/` |
| 5 | Measure physical accessibility quantities | **RENAMED** | `accessibility_quantities (1).csv` |
| 6 | Create shadow-risk feature | **PARTIAL** | `Candidate_Regions/shadow_fraction_by_region (1).csv`; `PSR_Mapping/`; `Accessibility_Analysis/psr_vs_lroc_shadow_comparison.png`. A file specifically named `shadow_risk_map.png` was not located |
| 7 | Create radar-support features | **RENAMED** | `radar_features (1).csv` |
| 8 | Create M3 and GRAIL science-context features | **RENAMED** | `Regional_Context_Data/science_context_features (1).csv`; `Regional_Context_Data/grail_regional_context_only (1).csv` |
| 9 | Create science-value score | **RENAMED** | `science_score (1).csv`; `Science_Scoring_and_Ranking/science_score_map (1).png` |
| 10 | Define rover accessibility constraints | **RENAMED** | `Accessibility_Analysis/rover_accessibility_constraints (1).csv` |
| 11 | Identify feasible and excluded targets | **PARTIAL** | `feasible_target_regions (1).csv`; `Accessibility_Analysis/feasible_target_map.png`. No clearly named `excluded_target_regions_with_reason.csv` was located; uncertain/removed-region tables may contain part of this information |
| 12 | Rank feasible targets | **RENAMED** | `science_priority_ranked.csv`; `Science_Scoring_and_Ranking/ranked_targets_map.png` |
| 13 | Compare selection strategies using Pareto analysis | **NOT LOCATED / RETIRED** | No Pareto comparison CSV or strategy-comparison plot found. The consolidated script labels this stage as retired, but it remains part of the approved brief |
| 14 | Run sensitivity tests | **FOUND** | `constraint_sensitivity_results.csv`; `Science_Scoring_and_Ranking/sensitivity_summary.png` |
| 15 | Prepare final report and presentation | **NOT LOCATED** | No final report or final presentation was found |

## Main Missing Deliverables

- Minimum-mapping-unit justification document.
- Supervisor approval record.
- Watershed parameter record.
- Explicit excluded-target table with exclusion reasons.
- Pareto target comparison and strategy-comparison plot.
- Final report and presentation.

# Intern 4: Policy and Reinforcement-Learning Mission Resilience

## Main Entry Points

Recommended execution/review order:

1. `Intern-4_outputs/grid_wold.py`
2. `Intern-4_outputs/grid_world.csv`
3. `Intern-4_outputs/action_space/action_space.txt`
4. `Intern-4_outputs/policy_based_results/step9_baseline_policies.py`
5. `Intern-4_outputs/q-learning_results/q_learning_updated.py`
6. `Intern-4_outputs/policy_based_results/step11_policy_compute_cost.py`
7. `Intern-4_outputs/Scenario_tests/step12_scenario_tests.py`
8. `Intern-4_outputs/mission_resilince.py`

The filenames `grid_wold.py` and `mission_resilince.py` contain spelling errors, but they are listed exactly as submitted.

## Step-by-Step Navigation

| Plan Step | Required work | Status | Submitted files to open |
|---:|---|---|---|
| 1 | Define reference lunar rover | **NOT LOCATED** | No `reference_rover_architecture.md` found |
| 2 | Record rover hardware and onboard constraints | **NOT LOCATED** | No sensors/payload or power/compute/communication constraint tables found |
| 3 | Describe input raster files | **NOT LOCATED** | No `file_description_table.csv` found |
| 4 | Select and map the study area | **NOT LOCATED** | No `study_area_map.png` found |
| 5 | Prepare policy input layers | **PARTIAL** | Arrays are present in `npy_files/`: terrain risk, shadow risk, confidence, and science reward. The required maps and `policy_input_layers_definition.csv` were not located |
| 6 | Build grid-world | **FOUND** | `grid_world.csv`; `grid_world.npy`; `grid_cell_properties.csv`; `grid_wold.py` |
| 7 | Define rover actions | **FOUND** | `action_space/action_space.txt` |
| 8 | Define reward, penalty, and operating rules | **PARTIAL** | Reward and constraint logic is embedded in `grid_wold.py`, `q-learning_results/q_learning_updated.py`, and other policy scripts. The required standalone `reward_function.txt` and `operating_constraints_table.csv` were not located |
| 9 | Implement baseline policies | **FOUND** | `policy_based_results/baseline_policy_results.csv`; `policy_based_results/baseline_policy_maps.png`; `policy_based_results/step9_baseline_policies.py` |
| 10 | Train Q-learning offline | **FOUND** | `q-learning_results/q_learning_results.csv`; `q_learning_summary.csv`; `q_learning_episode_metrics.csv`; `learning_curve.png`; `q_policy_map.png`; `q_learning_updated.py` |
| 11 | Evaluate onboard policy cost | **PARTIAL** | `policy_based_results/step11_policy_compute_cost.py` exists and declares the required outputs, but `policy_compute_cost_comparison.csv` and `offline_vs_onboard_execution_plan.md` were not copied into the submitted folder |
| 12 | Run mission failure scenarios | **FOUND** | `Scenario_tests/scenario_results.csv`; `Scenario_tests/scenario_plots.png`; `Scenario_tests/step12_scenario_tests.py` |
| 13 | Measure mission resilience | **FOUND** | `resilience_metrics.csv`; aggregation logic in `mission_resilince.py` |
| 14 | Compare policies | **PARTIAL** | `policy_based_results/policy_comparison_plots.png` is present. The required `policy_comparison_table.csv` was not found, although `mission_resilince.py` contains code to generate it |
| 15 | Prepare final report and presentation | **NOT LOCATED** | No final report or final presentation was found |

## Important Reproducibility Notes

- Several scripts contain hard-coded paths from the intern's Windows computer. They will not run directly from `Intern_outputs/` without changing the path configuration.
- Some scripts write to directories that are not present in this submitted package.
- `step11_policy_compute_cost.py` states a `RAD750` compute assumption. The later guide instruction was to use a SHAKTI-class processor assumption, so this should be revised before the final report.
- `grid_wold.py` changes the passability limit from 15 degrees to 20 degrees to obtain a connected grid. This decision should be explicitly documented and approved because it changes the navigation environment.

## Main Missing Deliverables

- Reference-rover architecture.
- Rover sensors/payload table.
- Power, compute, and communication constraint table.
- Dataset description table and study-area map.
- Policy input maps and definition table.
- Standalone reward-function and operating-constraint files.
- Policy compute-cost CSV and offline/onboard plan.
- Policy comparison table.
- Final report and presentation.

# Recommended Documentation Cleanup

The current submission should not be reorganized destructively. Use the following structure for the next submission:

```text
Intern-X_outputs/
  README.md
  final/
    report/
    code/
    tables/
    figures/
    rasters/
  archive/
    earlier_versions/
  deliverable_manifest.csv
```

Each intern's `README.md` should contain:

- Approved project title and research question.
- Exact execution order.
- Current/final version name.
- Input files required.
- Output files produced by each step.
- Missing or incomplete steps.
- Assumptions and known limitations.

The `deliverable_manifest.csv` should use these columns:

```text
plan_step,deliverable_name,actual_relative_path,status,current_version,generated_by,notes
```

This root navigator can remain the common index. The per-intern `README.md` files and manifests will make each submission independently reproducible and easier to convert into reports and papers.
