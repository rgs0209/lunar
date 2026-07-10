 # CONSENSUS AREA GUIDE

## Why These Areas Were Selected

Consensus Areas A and B contain groups of qualified science-priority regions that also remain relevant to confidence, path-cost, and rover-policy analysis. They are used to reduce the CV work from a full lunar scene to two reproducible study areas.

The areas are defined from Intern 3 region IDs, not from the hand-drawn circles in the reference screenshot. A fixed 2.5 km margin is added around the combined region boundaries.

## Consensus Area A

Included ranked regions:

| Rank | Region ID |
|---:|---:|
| 3 | 7446 |
| 4 | 7454 |
| 5 | 4071 |
| 6 | 7584 |
| 8 | 8991 |
| 14 | 6565 |
| 19 | 6375 |
| 20 | 8949 |

Approximate physical size: 19.6 km by 16.8 km on the LOLA 25 m grid.

## Consensus Area B

Included ranked regions:

| Rank | Region ID |
|---:|---:|
| 2 | 9163 |
| 9 | 10987 |
| 11 | 6912 |
| 13 | 10385 |
| 15 | 7687 |
| 16 | 12486 |
| 17 | 9162 |
| 18 | 3628 |

Approximate physical size: 30.1 km by 31.7 km on the LOLA 25 m grid.

## Experimental Use

Use both areas for cross-area validation:

```text
Experiment 1: develop on Area A and test on Area B
Experiment 2: develop on Area B and test on Area A
```

Do not treat nearby image patches from the same area as fully independent geographic tests.

## Grid Relationship

- The decision/reference grid is LOLA 25 m.
- The optical and local terrain layers are supplied at 5 m.
- The 5 m and 25 m products share the same lunar polar stereographic origin.
- Each 25 m cell corresponds to 5 by 5 cells on the supplied 5 m layers.

