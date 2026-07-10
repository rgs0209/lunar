# APPROVED THRESHOLDS FOR THE CV INTERN PROJECTS

## Purpose

Use the values below so the CV projects remain consistent with the submitted
Intern 2, Intern 3, and Intern 4 reports reviewed by the guide. Do not change a
listed value without recording the reason and obtaining supervisor approval.

## Supervisor Correction: Slope Interpretation

The operational safe-slope limit is **15 degrees**.

| Mean slope | Display | Interpretation |
|---|---|---|
| `<= 15 degrees` | Green | Safe/acceptable baseline |
| `> 15 to <= 20 degrees` | Yellow | Manageable risk for rover-capability testing; not safe |
| `> 20 degrees` | Red | High risk/unsafe |

Run separate rover-capability sensitivity cases at `16`, `17`, `18`, `19`,
and `20 degrees`. These cases must remain yellow in maps and tables. The
20-degree value used by Intern 4 to obtain grid connectivity is a sensitivity
or capability case, not the approved safe limit.

## CV Intern 1: Terrain Perception and Confidence

### Analysis Scale

| Quantity | Approved value |
|---|---:|
| Decision grid | 25 m |
| LOLA roughness window | 7 x 7 cells = 175 m |
| Roughness-estimate relative error at 7 x 7 | approximately 10.2% |

### Confidence Classes

| Confidence score | Class |
|---|---|
| `< 0.35` | Low |
| `0.35 to < 0.65` | Medium |
| `>= 0.65` | High |
| Missing required inputs | Insignificant/unknown |

### Intern 2 Fuzzy Membership Breakpoints

These fuzzy slope sets estimate **data confidence**. They must not be used to
label terrain above 15 degrees as safe.

| Variable | Set | Breakpoints |
|---|---|---|
| Slope (degrees) | Gentle trapezoid | `(0, 0, 10, 20)` |
| Slope (degrees) | Moderate triangle | `(15, 20.5, 25)` |
| Slope (degrees) | Steep trapezoid | `(20, 30, 71, 71)` |
| Roughness (m) | Smooth trapezoid | `(0, 0, 9, 18.56)` |
| Roughness (m) | Moderate triangle | `(13, 18.56, 35)` |
| Roughness (m) | Rough trapezoid | `(28, 50, 77, 77)` |
| Shadow fraction | Lit trapezoid | `(0, 0, 0.2, 0.6)` |
| Shadow fraction | Shadowed trapezoid | `(0.4, 0.8, 1, 1)` |
| Radar support | None / partial / full | `0 / 1 / 2` |
| Output confidence | Low trapezoid | `(0, 0, 0.2, 0.4)` |
| Output confidence | Medium triangle | `(0.3, 0.5, 0.7)` |
| Output confidence | High trapezoid | `(0.6, 0.8, 1, 1)` |

### Intern 3 Region Qualification and Risk Display

| Check | Threshold | Use |
|---|---:|---|
| Mean slope | `<= 15 degrees` | Green safe/acceptable baseline |
| Mean slope sensitivity | `16, 17, 18, 19, 20 degrees` | Yellow manageable-risk cases, not safe |
| Mean slope | `> 20 degrees` | Red high-risk/unsafe |
| Maximum slope | `<= 30 degrees` | Hard condition |
| Pixels with slope above 25 degrees | `<= 10%` | Hard condition |
| Annual PSR illumination definition | illumination fraction `< 0.001` | PSR pixel |
| PSR fraction in a region | `<= 0.50` | Hard condition |
| Valid LOLA coverage | `>= 0.80` | Hard condition |
| Region area | `>= 0.0784 km2` | One 280 m x 280 m M3 footprint |
| Bounding-box aspect ratio | `<= 10` | Reject sliver regions above this value |
| Slope standard deviation | `<= 5 degrees` | Above this is uncertain |
| Roughness mean | `<= 10 m` | Above this is uncertain |
| Roughness standard deviation | `<= 10 m` | Above this is uncertain |
| Region fill ratio | `>= 0.25` | Below this is uncertain |
| DFSAR or Mini-RF valid coverage | at least one `>= 0.10` | Both below 10% is uncertain |

Roughness and slope-variation limits create an **uncertain** label; they are not
automatic hard hazard removals.

## CV Intern 2: Localization, Route Tracking, Battery and Compute

CV Intern 2 does not detect hazards. The following values are fixed operating
constraints inherited from the prior navigation simulations.

| Parameter | Approved value |
|---|---:|
| Safe baseline slope | `<= 15 degrees` |
| Rover-capability sensitivity limits | `16, 17, 18, 19, 20 degrees` |
| Terrain-risk impassability threshold | `0.90` |
| Nominal simulated energy budget | `650 cost units` |
| Limited-energy test budget | `430 cost units` |
| Movement directions | 8 |
| Cardinal movement multiplier | `1.0` |
| Diagonal movement multiplier | `sqrt(2)` |
| Terrain cost weight | `0.6` |
| Shadow cost weight | `0.3` |
| Confidence/uncertainty cost weight | `0.1` |
| Science-priority threshold, when tested | 95th percentile of passable cells |
| Sensor-dropout scenario | 25% of non-impassable cells |
| Science-value noise scenario | Gaussian noise, sigma `0.1` |
| Terrain-uncertainty scenario | risk multiplied by `1.1` |
| Communication-delay scenario | 5 additional steps |

If Q-learning is retained only as a comparison baseline:

| Parameter | Approved value |
|---|---:|
| Training episodes | 150,000 |
| Learning rate, alpha | `0.1` |
| Discount factor, gamma | `0.99` |

The `650` and `430` values are approved **simulation cost units**, not measured
rover battery capacities. They must not be reported as watt-hours or flight
hardware specifications.

## Values That Must Not Be Reused

- Do not present the Intern 4 `20 degrees` connectivity workaround as safe.
  Values from 16 to 20 degrees are yellow manageable-risk sensitivity cases.
- Do not merge the 16-to-20-degree cases into the green baseline results.
- Do not reuse Intern 4's old `200 x 200` grid, `(0, 199)` start cell, `(199, 0)`
  goal cell, or 5 km x 5 km extent. Create new Area A and Area B grids.
- Do not use `99th percentile` for the science-priority threshold. The final
  report uses the `95th percentile`.
- Do not treat Intern 4's terrain-risk formula as a CV threshold. Its report
  records a known normalization inconsistency. Use the supplied fixed risk and
  cost layers instead of rebuilding them.

## New CV Thresholds Still Requiring Validation

The earlier reports do not provide thresholds for visual localization. CV
Intern 2 must test and justify the following before fixing them:

- minimum ORB match count;
- minimum RANSAC inlier count or inlier ratio;
- RANSAC reprojection tolerance;
- normalized cross-correlation acceptance value;
- maximum allowed localization or cross-track error;
- adaptive relocalization trigger;
- image-capture and localization compute cost.

These new thresholds must be selected using Area A development experiments and
checked on Area B, then reversed, without changing values after seeing the test
results.

## Source Reports

- `report_lunar_project-7.pdf`: confidence classes and constrained path cost.
- `main.pdf`: rover accessibility and science-priority region ranking.
- `report.pdf`: policy/RL resilience, energy, and compute simulation.
