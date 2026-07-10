"""
step9_baseline_policies.py  — Step 9 (regenerated on corrected grid)
======================================================================
Reruns all four baseline policies on the updated grid_world.csv
(slope <= 20° passability threshold, energy budget = 650).

Fixes vs original baseline_policy_results.csv:
  - Grid now uses slope<=20° (was 15°) → paths are different
  - Uncertainty Aware cost function correctly applied (was identical to Shortest Path)
  - Energy proxy column added (was missing)
  - Hazard exposure column added (was missing)
  - Recovery after failure column added (not applicable for nominal run → N/A)
  - distance_m computed as physical distance (25m cardinal, 35.36m diagonal)

Outputs:
  outputs/baseline_policy_results.csv   (corrected)
  outputs/baseline_policy_maps.png      (path visualisations, 2×2 grid)
"""

import numpy as np
import pandas as pd
import heapq
import time
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('outputs', exist_ok=True)

# ================================================================
# LOAD ENVIRONMENT
# ================================================================
CSV_PATH = (
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\Risks and grid world\grid_world.csv"
)
print("Loading grid world...")
df = pd.read_csv(CSV_PATH)

ROWS, COLS     = 200, 200
START          = (0, 199)
GOAL           = (199, 0)
ENERGY_BUDGET  = 650
SCIENCE_THRESH = 0.5

TERRAIN_RISK   = df['terrain_risk'].values.reshape(ROWS, COLS).astype(np.float32)
SHADOW_RISK    = df['shadow_risk'].values.reshape(ROWS, COLS).astype(np.float32)
CONFIDENCE     = df['confidence'].values.reshape(ROWS, COLS).astype(np.float32)
SCIENCE_REWARD = df['science_reward'].values.reshape(ROWS, COLS).astype(np.float32)
MOVEMENT_COST  = df['movement_cost'].values.reshape(ROWS, COLS).astype(np.float32)
IS_PASSABLE    = df['is_passable'].values.reshape(ROWS, COLS).astype(bool)

ACTIONS = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

print(f"Grid: {ROWS}×{COLS} | Passable: {IS_PASSABLE.sum():,} | "
      f"Energy budget: {ENERGY_BUDGET}")


# ================================================================
# A* (fixed stale-entry check — heap stores (f, g, state))
# ================================================================
def astar(cost_fn, heuristic_fn=None):
    if heuristic_fn is None:
        heuristic_fn = lambda r, c: 0.0

    dist = {START: 0.0}
    prev = {START: None}
    heap = [(heuristic_fn(*START), 0.0, START)]
    explored = 0

    t0 = time.perf_counter()
    while heap:
        f, g, (r, c) = heapq.heappop(heap)
        explored += 1
        if (r, c) == GOAL:
            break
        if g > dist.get((r, c), float('inf')) + 1e-9:
            continue
        for dr, dc in ACTIONS:
            nr, nc = r+dr, c+dc
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            if not IS_PASSABLE[nr, nc]:
                continue
            step_cost = cost_fn(r, c, nr, nc)
            if np.isinf(step_cost):
                continue
            new_g = g + step_cost
            if new_g < dist.get((nr, nc), float('inf')):
                dist[(nr, nc)] = new_g
                prev[(nr, nc)] = (r, c)
                heapq.heappush(heap,
                    (new_g + heuristic_fn(nr, nc), new_g, (nr, nc)))

    elapsed = time.perf_counter() - t0

    path, cur = [], GOAL
    if GOAL in prev:
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
    return path, explored, elapsed


def chebyshev(r, c):
    return max(abs(r - GOAL[0]), abs(c - GOAL[1]))


# ================================================================
# POLICY COST FUNCTIONS
# ================================================================
def cost_shortest(r, c, nr, nc):
    return 1.4142 if (abs(nr-r)==1 and abs(nc-c)==1) else 1.0


def cost_safest(r, c, nr, nc):
    dmul = 1.4142 if (abs(nr-r)==1 and abs(nc-c)==1) else 1.0
    tr   = float(TERRAIN_RISK[nr, nc])
    sh   = float(SHADOW_RISK[nr, nc])
    return (1 + 2*(tr + sh)) * dmul


def cost_science(r, c, nr, nc):
    dmul = 1.4142 if (abs(nr-r)==1 and abs(nc-c)==1) else 1.0
    mc   = float(MOVEMENT_COST[nr, nc])
    sc   = float(SCIENCE_REWARD[nr, nc])
    # FIX: discount scaled to keep cost >= 0.5 (avoids near-zero cost explosion)
    disc = 0.5 * sc if sc > SCIENCE_THRESH else 0.0
    return max(0.5, mc * dmul - disc)


def cost_uncertainty(r, c, nr, nc):
    # FIX: correctly applies uncertainty-aware cost (was missing in original)
    dmul = 1.4142 if (abs(nr-r)==1 and abs(nc-c)==1) else 1.0
    cf   = float(CONFIDENCE[nr, nc])
    tr   = float(TERRAIN_RISK[nr, nc])
    return (1 + 3*((1-cf) + 0.5*tr)) * dmul


# ================================================================
# COMPUTE PATH METRICS
# ================================================================
def compute_metrics(path):
    """
    Given a path (list of (row,col)), compute all required metrics.
    """
    if not path or path[-1] != GOAL:
        return None   # policy failed

    steps         = len(path) - 1   # number of moves
    distance_m    = 0.0
    terrain_exp   = 0.0
    shadow_exp    = 0.0
    science_ret   = 0.0
    conf_vals     = []
    energy_proxy  = 0.0
    hazard_cells  = 0     # cells with terrain_risk > 0.6 (slope > 15°)

    for i in range(1, len(path)):
        r, c   = path[i]
        pr, pc = path[i-1]
        diag   = (abs(r-pr)==1 and abs(c-pc)==1)
        dmul   = 1.4142 if diag else 1.0
        phys_d = 25.0 * dmul           # physical distance in metres

        distance_m   += phys_d
        terrain_exp  += float(TERRAIN_RISK[r, c])
        shadow_exp   += float(SHADOW_RISK[r, c])
        science_ret  += float(SCIENCE_REWARD[r, c])
        conf_vals.append(float(CONFIDENCE[r, c]))
        energy_proxy += float(MOVEMENT_COST[r, c]) * dmul

        if TERRAIN_RISK[r, c] > 0.6:   # slope > 15° (high risk band)
            hazard_cells += 1

    return {
        'success'              : True,
        'steps'                : steps,
        'distance_m'           : round(distance_m, 2),
        'terrain_exposure'     : round(terrain_exp, 3),
        'shadow_exposure'      : round(shadow_exp, 3),
        'science_return'       : round(science_ret, 3),
        'avg_confidence'       : round(float(np.mean(conf_vals)), 3),
        'energy_proxy'         : round(energy_proxy, 3),
        'hazard_exposure'      : hazard_cells,
        'within_energy_budget' : energy_proxy <= ENERGY_BUDGET,
        'recovery_after_failure': 'N/A (nominal run)',
    }


# ================================================================
# RUN ALL POLICIES
# ================================================================
policy_defs = [
    ("Shortest Path",    cost_shortest,    chebyshev),
    ("Safest Path",      cost_safest,      chebyshev),
    ("Science Priority", cost_science,     chebyshev),
    ("Uncertainty Aware",cost_uncertainty, chebyshev),
]

results = []
paths   = {}

print(f"\nRunning baseline policies on updated grid (slope<=20°) ...\n")

for name, cost_fn, h_fn in policy_defs:
    t0   = time.perf_counter()
    path, nodes, _ = astar(cost_fn, h_fn)
    runtime = time.perf_counter() - t0

    metrics = compute_metrics(path)

    if metrics is None:
        print(f"  {name}: FAILED — no path found")
        results.append({'policy': name, 'success': False,
                        'runtime_sec': round(runtime, 6)})
        paths[name] = []
        continue

    metrics['policy']      = name
    metrics['runtime_sec'] = round(runtime, 6)
    results.append(metrics)
    paths[name] = path

    print(f"  {name}:")
    print(f"    Steps           : {metrics['steps']}")
    print(f"    Distance        : {metrics['distance_m']:.1f} m")
    print(f"    Energy proxy    : {metrics['energy_proxy']:.1f} / {ENERGY_BUDGET}")
    print(f"    Terrain exposure: {metrics['terrain_exposure']:.3f}")
    print(f"    Shadow exposure : {metrics['shadow_exposure']:.3f}")
    print(f"    Science return  : {metrics['science_return']:.3f}")
    print(f"    Avg confidence  : {metrics['avg_confidence']:.3f}")
    print(f"    Hazard cells    : {metrics['hazard_exposure']}")
    print(f"    Within budget   : {metrics['within_energy_budget']}")
    print(f"    Runtime         : {runtime*1000:.2f} ms")


# ================================================================
# VERIFY: Uncertainty Aware ≠ Shortest Path
# ================================================================
sp = next(r for r in results if r['policy']=='Shortest Path')
ua = next(r for r in results if r['policy']=='Uncertainty Aware')
if sp['steps'] == ua['steps'] and sp['terrain_exposure'] == ua['terrain_exposure']:
    print("\n⚠️  WARNING: Uncertainty Aware still identical to Shortest Path!")
    print("   Check cost_uncertainty function.")
else:
    print(f"\n✅ Uncertainty Aware correctly differs from Shortest Path "
          f"({ua['steps']} vs {sp['steps']} steps)")


# ================================================================
# SAVE baseline_policy_results.csv
# ================================================================
col_order = [
    'policy', 'success',
    'steps', 'distance_m',
    'terrain_exposure', 'shadow_exposure',
    'science_return', 'avg_confidence',
    'energy_proxy', 'hazard_exposure',
    'within_energy_budget',
    'recovery_after_failure',
    'runtime_sec',
]
out_df = pd.DataFrame(results)[col_order]

out_path = (
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\baseline_policy_results.csv"
)
out_df.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}")
print(out_df.to_string(index=False))


# ================================================================
# PLOT: 2×2 path maps
# ================================================================
print("\nGenerating path maps ...")

# Background: terrain risk (impassable in dark)
bg = np.where(IS_PASSABLE, TERRAIN_RISK, 1.5)

fig, axes = plt.subplots(2, 2, figsize=(14, 14))
fig.suptitle(
    'Step 9 — Baseline Policy Paths\n'
    '200×200 grid | 25m/cell | slope≤20° passability | energy budget=650',
    fontsize=13
)
axes = axes.flatten()

policy_names = ["Shortest Path", "Safest Path",
                "Science Priority", "Uncertainty Aware"]

for idx, name in enumerate(policy_names):
    ax   = axes[idx]
    path = paths.get(name, [])
    row  = next((r for r in results if r['policy']==name), {})

    im = ax.imshow(bg, cmap='RdYlGn_r', vmin=0, vmax=1.5,
                   origin='upper', interpolation='nearest')

    if path:
        rows_p = [p[0] for p in path]
        cols_p = [p[1] for p in path]
        ax.plot(cols_p, rows_p, color='dodgerblue', linewidth=1.5,
                alpha=0.85, zorder=3)

    # Start and Goal markers
    ax.plot(START[1], START[0], 'g^', markersize=9,
            label='Start', zorder=5)
    ax.plot(GOAL[1],  GOAL[0],  'r*', markersize=11,
            label='Goal',  zorder=5)

    steps_str = str(row.get('steps','?'))
    energy_str = f"{row.get('energy_proxy','?'):.1f}" if row.get('energy_proxy') else '?'
    ax.set_title(
        f"{name}\n"
        f"steps={steps_str}  energy={energy_str}/{ENERGY_BUDGET}  "
        f"science={row.get('science_return','?'):.2f}",
        fontsize=10
    )
    ax.set_xlabel('col (25m steps)')
    ax.set_ylabel('row (25m steps)')
    ax.legend(loc='upper left', fontsize=8)

plt.colorbar(im, ax=axes[-1], label='Terrain Risk (dark=impassable)')
plt.tight_layout()

map_path = (
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\baseline_policy_maps.png"
)
plt.savefig(map_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {map_path}")
print("\nStep 9 complete.")
