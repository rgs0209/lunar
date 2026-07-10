# INPUTS: CV INTERN 2

## Start Here

1. Read `../DATASET_GUIDE.md`, `../CONSENSUS_AREA_GUIDE.md`, and
   `../APPROVED_THRESHOLDS.md` from the package root.
2. Open the orientation presentation.
3. Build new Area A/B grids from the supplied 25 m layers.
4. Read Intern 2 path-cost and confidence documents.
5. Use Intern 3 target tables to select goals.
6. Plan an initial route using the fixed feasibility and path-cost layers.
7. Create local rover-view proxies from the supplied LROC crops and implement
   visual position matching against the area reference image.
8. Read Intern 4 policy scripts only after the new grids are prepared.

## Main Files

- `raster_layers/Consensus_A/`
- `raster_layers/Consensus_B/`
- `reference_material/Intern_2/`
- `reference_material/Intern_3/`
- `reference_material/Intern_4/`

The Intern 4 grid is included only as a reference example. It is not the final grid for either consensus area.

This project does not require outputs from CV Intern 1 during the internship.
The two projects will be integrated only after both interns complete their work.

The supplied terrain-risk layers are fixed navigation constraints. Do not
perform terrain-hazard detection or classification in this project.
