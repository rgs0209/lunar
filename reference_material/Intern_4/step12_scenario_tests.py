"""
step12_scenario_tests.py — Step 12
====================================
Runs 6 mission failure scenarios across all 5 policies.
Each scenario modifies the environment and measures performance
degradation vs the nominal baseline.

Scenarios:
  1. Sensor Dropout      — 25% of cells lose sensor data (risk→0, conf→0.6)
  2. Blocked Path        — band of cells around path midpoint blocked
  3. Limited Energy      — budget reduced from 650 → 430
  4. Wrong Resource Est. — science_reward perturbed with ±0.3 noise
  5. Increased Terrain   — terrain_risk + Gaussian noise σ=0.15
  6. Communication Delay — rover executes action from 5 steps ago

Output:
  outputs/scenario_results.csv   (30 rows: 6 scenarios × 5 policies)
  outputs/scenario_plots.png     (heatmap + bar charts)
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
SEED = 42
np.random.seed(SEED)

# ================================================================
# LOAD ENVIRONMENT
# ================================================================
CSV_PATH = (
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\Risks and grid world\grid_world.csv"
)
Q_NPY_PATH = (
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\Reaward_q_learning\q-learning_results\q_policy_map.npy"
)
BASELINE_PATH = (
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\Reaward_q_learning\policy_based_results\baseline_policy_results.csv"
)

print("Loading environment...")
df = pd.read_csv(CSV_PATH)

ROWS, COLS     = 200, 200
START          = (0, 199)
GOAL           = (199, 0)
NOMINAL_BUDGET = 650
SCIENCE_THRESH = 0.5

# Base arrays (never modified — scenarios make copies)
BASE_TERRAIN   = df['terrain_risk'].values.reshape(ROWS,COLS).astype(np.float32)
BASE_SHADOW    = df['shadow_risk'].values.reshape(ROWS,COLS).astype(np.float32)
BASE_CONFIDENCE= df['confidence'].values.reshape(ROWS,COLS).astype(np.float32)
BASE_SCIENCE   = df['science_reward'].values.reshape(ROWS,COLS).astype(np.float32)
BASE_MC        = df['movement_cost'].values.reshape(ROWS,COLS).astype(np.float32)
BASE_PASSABLE  = df['is_passable'].values.reshape(ROWS,COLS).astype(bool)

Q_POLICY   = np.load(Q_NPY_PATH)          # (200,200) uint8
BASELINE   = pd.read_csv(BASELINE_PATH)
ACTIONS    = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

# Baseline values for recovery calculation
BL = {row['policy']: row for _, row in BASELINE.iterrows()}
BL_QL = {
    'steps': 268, 'energy_proxy': 440.5, 'success': True,
    'terrain_exposure': None, 'shadow_exposure': None,
    'science_return': 26.508, 'hazard_exposure': None
}

print(f"Grid: {ROWS}×{COLS} | Passable: {BASE_PASSABLE.sum():,}")


# ================================================================
# A* (fixed stale-entry check)
# ================================================================
def chebyshev(r, c):
    return max(abs(r - GOAL[0]), abs(c - GOAL[1]))


def astar(cost_fn, passable_mask, h_fn=None):
    if h_fn is None:
        h_fn = chebyshev
    dist = {START: 0.0}
    prev = {START: None}
    heap = [(h_fn(*START), 0.0, START)]
    while heap:
        f, g, (r, c) = heapq.heappop(heap)
        if (r, c) == GOAL:
            break
        if g > dist.get((r, c), float('inf')) + 1e-9:
            continue
        for dr, dc in ACTIONS:
            nr, nc = r+dr, c+dc
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            if not passable_mask[nr, nc]:
                continue
            sc = cost_fn(r, c, nr, nc)
            if np.isinf(sc):
                continue
            new_g = g + sc
            if new_g < dist.get((nr, nc), float('inf')):
                dist[(nr, nc)] = new_g
                prev[(nr, nc)] = (r, c)
                heapq.heappush(heap, (new_g + h_fn(nr,nc), new_g, (nr,nc)))
    path, cur = [], GOAL
    if GOAL in prev:
        while cur is not None:
            path.append(cur); cur = prev[cur]
        path.reverse()
    return path


# ================================================================
# POLICY COST FUNCTIONS (take arrays as parameters for scenarios)
# ================================================================
def make_costs(terrain, shadow, confidence, science, mc):
    def cost_shortest(r, c, nr, nc):
        return 1.4142 if (abs(nr-r)==1 and abs(nc-c)==1) else 1.0

    def cost_safest(r, c, nr, nc):
        dmul = 1.4142 if (abs(nr-r)==1 and abs(nc-c)==1) else 1.0
        return (1 + 2*(float(terrain[nr,nc]) + float(shadow[nr,nc]))) * dmul

    def cost_science(r, c, nr, nc):
        dmul = 1.4142 if (abs(nr-r)==1 and abs(nc-c)==1) else 1.0
        sc_  = float(science[nr, nc])
        mc_  = float(mc[nr, nc])
        disc = 0.5 * sc_ if sc_ > SCIENCE_THRESH else 0.0
        return max(0.5, mc_ * dmul - disc)

    def cost_uncertainty(r, c, nr, nc):
        dmul = 1.4142 if (abs(nr-r)==1 and abs(nc-c)==1) else 1.0
        cf_  = float(confidence[nr, nc])
        tr_  = float(terrain[nr, nc])
        return (1 + 3*((1-cf_) + 0.5*tr_)) * dmul

    return {
        'Shortest Path'   : cost_shortest,
        'Safest Path'     : cost_safest,
        'Science Priority': cost_science,
        'Uncertainty Aware':cost_uncertainty,
    }


# ================================================================
# METRICS FROM PATH
# ================================================================
def path_metrics(path, terrain, shadow, confidence, science,
                 mc, energy_budget, passable):
    if not path or path[-1] != GOAL:
        return {
            'success': False, 'steps': 0, 'distance_m': 0.0,
            'terrain_exposure': 0.0, 'shadow_exposure': 0.0,
            'science_return': 0.0, 'avg_confidence': 0.0,
            'energy_proxy': 0.0, 'hazard_exposure': 0,
            'within_energy_budget': False,
        }
    steps = len(path) - 1
    dist_m = tr_exp = sh_exp = sci_ret = energy = 0.0
    conf_vals = []
    hazard = 0

    for i in range(1, len(path)):
        r, c   = path[i]
        pr, pc = path[i-1]
        diag   = (abs(r-pr)==1 and abs(c-pc)==1)
        dmul   = 1.4142 if diag else 1.0
        dist_m  += 25.0 * dmul
        tr_exp  += float(terrain[r, c])
        sh_exp  += float(shadow[r, c])
        sci_ret += float(science[r, c])
        conf_vals.append(float(confidence[r, c]))
        energy  += float(mc[r, c]) * dmul
        if terrain[r, c] > 0.6:
            hazard += 1
        if energy > energy_budget:
            # path found but energy exceeded mid-way
            return {
                'success': False, 'steps': i, 'distance_m': round(dist_m,2),
                'terrain_exposure': round(tr_exp,3),
                'shadow_exposure': round(sh_exp,3),
                'science_return': round(sci_ret,3),
                'avg_confidence': round(float(np.mean(conf_vals)),3),
                'energy_proxy': round(energy,3),
                'hazard_exposure': hazard,
                'within_energy_budget': False,
            }
    return {
        'success': True,
        'steps': steps,
        'distance_m': round(dist_m, 2),
        'terrain_exposure': round(tr_exp, 3),
        'shadow_exposure': round(sh_exp, 3),
        'science_return': round(sci_ret, 3),
        'avg_confidence': round(float(np.mean(conf_vals)), 3),
        'energy_proxy': round(energy, 3),
        'hazard_exposure': hazard,
        'within_energy_budget': energy <= energy_budget,
    }


# ================================================================
# Q-LEARNING EXECUTION (greedy policy map)
# ================================================================
def run_qlearning(terrain, shadow, confidence, science,
                  mc, passable, energy_budget,
                  comm_delay=0):
    r, c    = START
    energy  = 0.0
    path    = [START]
    action_history = []

    for _ in range(1000):
        action = int(Q_POLICY[r, c])
        action_history.append(action)

        # Communication delay: use action from N steps ago
        if comm_delay > 0 and len(action_history) > comm_delay:
            action = action_history[-1 - comm_delay]

        dr, dc = ACTIONS[action]
        nr, nc = r+dr, c+dc

        # Boundary
        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            nr, nc = r, c
        # Impassable
        elif not passable[nr, nc]:
            nr, nc = r, c

        mc_val = float(mc[nr, nc]) if passable[nr,nc] else 0.0
        diag   = (abs(nr-r)==1 and abs(nc-c)==1)
        dmul   = 1.4142 if diag else 1.0
        energy += mc_val * dmul

        r, c = nr, nc
        path.append((r, c))
        if energy > energy_budget:
            break
        if (r, c) == GOAL:
            break

    return path


def ql_metrics(path, terrain, shadow, confidence, science, mc, energy_budget):
    # Use path_metrics but report partial stats even on failure
    if not path:
        return {
            'success': False, 'steps': 0, 'distance_m': 0.0,
            'terrain_exposure': 0.0, 'shadow_exposure': 0.0,
            'science_return': 0.0, 'avg_confidence': 0.0,
            'energy_proxy': 0.0, 'hazard_exposure': 0,
            'within_energy_budget': False,
        }
    return path_metrics(path, terrain, shadow, confidence,
                        science, mc, energy_budget, BASE_PASSABLE)


# ================================================================
# RECOVERY METRIC
# ================================================================
def recovery(scenario_metric, policy_name, is_ql=False):
    """
    Recovery after failure = ratio of scenario performance to baseline.
    Returns string 'X.XX (Y%)' where Y% is % of baseline retained.
    """
    if is_ql:
        bl_steps  = BL_QL['steps']
        bl_energy = BL_QL['energy_proxy']
        bl_sci    = BL_QL['science_return']
    else:
        bl        = BL[policy_name]
        bl_steps  = bl['steps']
        bl_energy = bl['energy_proxy']
        bl_sci    = bl['science_return']

    if not scenario_metric['success']:
        return "0% (failed)"

    steps_pct  = (1 - (scenario_metric['steps'] - bl_steps)
                  / max(bl_steps, 1)) * 100
    energy_pct = (1 - abs(scenario_metric['energy_proxy'] - bl_energy)
                  / max(bl_energy, 1)) * 100
    sci_pct    = (scenario_metric['science_return']
                  / max(bl_sci, 0.001)) * 100

    avg_pct = (steps_pct + energy_pct + sci_pct) / 3
    return f"{avg_pct:.1f}%"


# ================================================================
# SCENARIO DEFINITIONS
# ================================================================
def get_scenarios():
    """Returns list of (scenario_id, name, description, env_modifier_fn)"""

    # Scenario 1: Sensor Dropout
    # 25% of passable cells lose sensor readings
    # terrain_risk → 0 (appears safe), confidence → 0.6 (floor)
    dropout_mask = np.zeros((ROWS, COLS), dtype=bool)
    passable_idx = np.argwhere(BASE_PASSABLE)
    chosen = passable_idx[
        np.random.choice(len(passable_idx),
                         size=int(len(passable_idx)*0.25),
                         replace=False)
    ]
    for r, c in chosen:
        dropout_mask[r, c] = True

    def env_sensor_dropout():
        terrain    = BASE_TERRAIN.copy()
        shadow     = BASE_SHADOW.copy()
        confidence = BASE_CONFIDENCE.copy()
        science    = BASE_SCIENCE.copy()
        mc         = BASE_MC.copy()
        passable   = BASE_PASSABLE.copy()
        # Sensor dropout: perceived risk drops to 0 (looks safe)
        # confidence drops to minimum (0.6)
        terrain[dropout_mask]    = 0.0
        confidence[dropout_mask] = 0.6
        # Recompute movement cost for dropped cells
        mc = np.where(
            passable,
            1.0*(1 + 0.6*terrain + 0.3*shadow + 0.1*(1-confidence)),
            np.inf
        ).astype(np.float32)
        return terrain, shadow, confidence, science, mc, passable, NOMINAL_BUDGET

    # Scenario 2: Blocked Path
    # Block a band across the main corridor midpoint (rows 110-120, cols 80-100)
    block_mask = np.zeros((ROWS, COLS), dtype=bool)
    for r in range(110, 121):
        for c in range(80, 101):
            if BASE_PASSABLE[r, c]:
                block_mask[r, c] = True

    def env_blocked_path():
        terrain    = BASE_TERRAIN.copy()
        shadow     = BASE_SHADOW.copy()
        confidence = BASE_CONFIDENCE.copy()
        science    = BASE_SCIENCE.copy()
        mc         = BASE_MC.copy()
        passable   = BASE_PASSABLE.copy()
        passable[block_mask] = False
        mc[block_mask]       = np.inf
        return terrain, shadow, confidence, science, mc, passable, NOMINAL_BUDGET

    # Scenario 3: Limited Energy
    # Budget reduced to 430 (just above BFS min 412, below all baseline values)
    def env_limited_energy():
        return (BASE_TERRAIN.copy(), BASE_SHADOW.copy(),
                BASE_CONFIDENCE.copy(), BASE_SCIENCE.copy(),
                BASE_MC.copy(), BASE_PASSABLE.copy(), 430)

    # Scenario 4: Wrong Resource Estimate
    # Science reward perturbed with Gaussian noise σ=0.3, clamped [0,1]
    sci_noise = BASE_SCIENCE + np.random.normal(0, 0.3, (ROWS, COLS)).astype(np.float32)
    sci_noise = np.clip(sci_noise, 0.0, 1.0).astype(np.float32)

    def env_wrong_resource():
        terrain    = BASE_TERRAIN.copy()
        shadow     = BASE_SHADOW.copy()
        confidence = BASE_CONFIDENCE.copy()
        science    = sci_noise.copy()   # perturbed science
        mc         = BASE_MC.copy()
        passable   = BASE_PASSABLE.copy()
        return terrain, shadow, confidence, science, mc, passable, NOMINAL_BUDGET

    # Scenario 5: Increased Terrain Uncertainty
    # terrain_risk + Gaussian noise σ=0.15, clamped [0,1]
    tr_noise = BASE_TERRAIN + np.random.normal(0, 0.15, (ROWS, COLS)).astype(np.float32)
    tr_noise = np.clip(tr_noise, 0.0, 1.0).astype(np.float32)

    def env_terrain_uncertainty():
        terrain    = tr_noise.copy()
        shadow     = BASE_SHADOW.copy()
        confidence = BASE_CONFIDENCE.copy()
        science    = BASE_SCIENCE.copy()
        mc         = np.where(
            BASE_PASSABLE,
            1.0*(1 + 0.6*terrain + 0.3*shadow + 0.1*(1-confidence)),
            np.inf
        ).astype(np.float32)
        passable   = BASE_PASSABLE.copy()
        return terrain, shadow, confidence, science, mc, passable, NOMINAL_BUDGET

    # Scenario 6: Communication Delay
    # Q-learning executes action from 5 steps ago
    # Baselines: path-follow delayed by 5 steps (rover is 5 waypoints behind)
    def env_comm_delay():
        shadow = BASE_SHADOW.copy()
        shadow[50:80, 60:130] = np.clip(shadow[50:80, 60:130] + 0.7, 0.0, 1.0)
        mc = np.where(
            BASE_PASSABLE,
            1.0*(1 + 0.6*BASE_TERRAIN + 0.3*shadow + 0.1*(1-BASE_CONFIDENCE)),
            np.inf
        ).astype(np.float32)
        return (BASE_TERRAIN.copy(), shadow, BASE_CONFIDENCE.copy(),
                BASE_SCIENCE.copy(), mc, BASE_PASSABLE.copy(), NOMINAL_BUDGET)

    return [
        (1, "Sensor Dropout",
         "25% of passable cells lose sensor data (terrain→0, conf→0.6)",
         env_sensor_dropout, False),
        (2, "Blocked Path",
         "Rows 110-120, cols 80-100 blocked (simulates rockfall/reassessment)",
         env_blocked_path, False),
        (3, "Limited Energy",
         "Energy budget reduced from 650 to 430",
         env_limited_energy, False),
        (4, "Wrong Resource Estimate",
         "science_reward perturbed with Gaussian noise σ=0.3",
         env_wrong_resource, False),
        (5, "Increased Terrain Uncertainty",
         "terrain_risk perturbed with Gaussian noise σ=0.15",
         env_terrain_uncertainty, False),
        (6, "Communication Delay",
         "Rover executes action from 5 steps ago (5-step delay)",
         env_comm_delay, True),   # True = comm delay scenario
    ]


# ================================================================
# RUN ALL SCENARIOS × ALL POLICIES
# ================================================================
scenarios = get_scenarios()
all_results = []

print(f"\nRunning {len(scenarios)} scenarios × 5 policies ...\n")

for sc_id, sc_name, sc_desc, env_fn, is_comm_delay in scenarios:
    print(f"{'─'*55}")
    print(f"Scenario {sc_id}: {sc_name}")
    print(f"  {sc_desc}")

    terrain, shadow, confidence, science, mc, passable, budget = env_fn()

    costs = make_costs(terrain, shadow, confidence, science, mc)

    # --- Baseline policies ---
    for policy_name, cost_fn in costs.items():
        t0   = time.perf_counter()

        if is_comm_delay:
            # Comm delay: baseline follows pre-planned path with 5-step lag
            # Re-plan on nominal env, then simulate delayed execution
           # Plan on nominal (stale) env, walk into modified env
            nom_costs = make_costs(BASE_TERRAIN, BASE_SHADOW,
                                BASE_CONFIDENCE, BASE_SCIENCE, BASE_MC)
            path = astar(nom_costs[policy_name], BASE_PASSABLE)
            # path is evaluated against modified env below (terrain/mc already updated)
        else:
            path = astar(cost_fn, passable)

        elapsed = time.perf_counter() - t0
        eval_science = BASE_SCIENCE if sc_id == 4 else science
        m = path_metrics(path, terrain, shadow, confidence,
                 eval_science, mc, budget, passable)

        rec = recovery(m, policy_name, is_ql=False)
        status = "✅" if m['success'] else "❌"
        print(f"  {status} {policy_name}: steps={m['steps']}, "
              f"energy={m['energy_proxy']:.1f}/{budget}, "
              f"science={m['science_return']:.2f}, "
              f"recovery={rec}")

        all_results.append({
            'scenario_id'          : sc_id,
            'scenario_name'        : sc_name,
            'scenario_description' : sc_desc,
            'policy'               : policy_name,
            'success'              : m['success'],
            'steps'                : m['steps'],
            'distance_m'           : m['distance_m'],
            'terrain_exposure'     : m['terrain_exposure'],
            'shadow_exposure'      : m['shadow_exposure'],
            'science_return'       : m['science_return'],
            'avg_confidence'       : m['avg_confidence'],
            'energy_proxy'         : m['energy_proxy'],
            'hazard_exposure'      : m['hazard_exposure'],
            'within_energy_budget' : m['within_energy_budget'],
            'recovery_after_failure': rec,
            'runtime_sec'          : round(elapsed, 4),
            'energy_budget_used'   : budget,
        })

    # --- Q-Learning ---
    t0 = time.perf_counter()
    comm_d = 5 if is_comm_delay else 0
    ql_path = run_qlearning(terrain, shadow, confidence, science,
                            mc, passable, budget, comm_delay=comm_d)
    elapsed = time.perf_counter() - t0
    eval_science = BASE_SCIENCE if sc_id == 4 else science
    m = ql_metrics(ql_path, terrain, shadow, confidence, eval_science, mc, budget)
    rec = recovery(m, 'Q-Learning', is_ql=True)
    status = "✅" if m['success'] else "❌"
    print(f"  {status} Q-Learning:       steps={m['steps']}, "
          f"energy={m['energy_proxy']:.1f}/{budget}, "
          f"science={m['science_return']:.2f}, "
          f"recovery={rec}")

    all_results.append({
        'scenario_id'          : sc_id,
        'scenario_name'        : sc_name,
        'scenario_description' : sc_desc,
        'policy'               : 'Q-Learning',
        'success'              : m['success'],
        'steps'                : m['steps'],
        'distance_m'           : m['distance_m'],
        'terrain_exposure'     : m['terrain_exposure'],
        'shadow_exposure'      : m['shadow_exposure'],
        'science_return'       : m['science_return'],
        'avg_confidence'       : m['avg_confidence'],
        'energy_proxy'         : m['energy_proxy'],
        'hazard_exposure'      : m['hazard_exposure'],
        'within_energy_budget' : m['within_energy_budget'],
        'recovery_after_failure': rec,
        'runtime_sec'          : round(elapsed, 4),
        'energy_budget_used'   : budget,
    })

print(f"\n{'─'*55}")

# ================================================================
# SAVE scenario_results.csv
# ================================================================
out_df = pd.DataFrame(all_results)
out_path = (
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\scenario_results.csv"
)
out_df.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}")
print(f"Rows: {len(out_df)} ({len(scenarios)} scenarios × 5 policies)")

# Quick summary table
print("\n=== SUCCESS RATE PER SCENARIO ===")
summary = out_df.groupby('scenario_name')['success'].agg(['sum','count'])
summary['success_rate'] = (summary['sum']/summary['count']*100).round(1)
print(summary[['sum','count','success_rate']].to_string())

print("\n=== SUCCESS RATE PER POLICY ===")
summary2 = out_df.groupby('policy')['success'].agg(['sum','count'])
summary2['success_rate'] = (summary2['sum']/summary2['count']*100).round(1)
print(summary2[['sum','count','success_rate']].to_string())


# ================================================================
# PLOTS
# ================================================================
print("\nGenerating scenario plots ...")

policies   = ['Shortest Path','Safest Path','Science Priority',
              'Uncertainty Aware','Q-Learning']
sc_names   = [s[1] for s in scenarios]
sc_names_s = ['S1\nDropout','S2\nBlocked','S3\nEnergy',
              'S4\nScience','S5\nTerrain','S6\nDelay']

# ── Plot 1: Success heatmap ──────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Step 12 — Scenario Test Results', fontsize=14, y=1.02)

success_mat = np.zeros((len(sc_names), len(policies)))
energy_mat  = np.zeros((len(sc_names), len(policies)))
science_mat = np.zeros((len(sc_names), len(policies)))

for row in all_results:
    si = [s[1] for s in scenarios].index(row['scenario_name'])
    pi = policies.index(row['policy'])
    success_mat[si, pi] = 1 if row['success'] else 0
    energy_mat[si, pi]  = row['energy_proxy']
    science_mat[si, pi] = row['science_return']

# Heatmap: success
im0 = axes[0].imshow(success_mat, cmap='RdYlGn', vmin=0, vmax=1,
                     aspect='auto')
axes[0].set_xticks(range(len(policies)))
axes[0].set_xticklabels([p.replace(' ','\n') for p in policies], fontsize=8)
axes[0].set_yticks(range(len(sc_names)))
axes[0].set_yticklabels(sc_names_s, fontsize=9)
axes[0].set_title('Success (green=pass, red=fail)')
for i in range(len(sc_names)):
    for j in range(len(policies)):
        axes[0].text(j, i, '✓' if success_mat[i,j] else '✗',
                     ha='center', va='center', fontsize=12,
                     color='black')

# Bar: energy proxy per scenario
x = np.arange(len(sc_names))
w = 0.15
colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd']
for pi, (pol, col) in enumerate(zip(policies, colors)):
    axes[1].bar(x + pi*w, energy_mat[:, pi], w,
                label=pol, color=col, alpha=0.85)
axes[1].axhline(NOMINAL_BUDGET, color='black', linestyle='--',
                linewidth=1, label='Budget=650')
axes[1].axhline(350, color='red', linestyle=':',
                linewidth=1, label='Limited budget=430')
axes[1].set_xticks(x + w*2)
axes[1].set_xticklabels(sc_names_s, fontsize=8)
axes[1].set_ylabel('Energy Proxy (cost units)')
axes[1].set_title('Energy Used per Scenario')
axes[1].legend(fontsize=7, loc='upper right')

# Bar: science return per scenario
for pi, (pol, col) in enumerate(zip(policies, colors)):
    axes[2].bar(x + pi*w, science_mat[:, pi], w,
                label=pol, color=col, alpha=0.85)
axes[2].set_xticks(x + w*2)
axes[2].set_xticklabels(sc_names_s, fontsize=8)
axes[2].set_ylabel('Science Return (cumulative)')
axes[2].set_title('Science Return per Scenario')
axes[2].legend(fontsize=7, loc='upper right')

plt.tight_layout()
plot_path = (
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\scenario_plots.png"
)
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {plot_path}")
print("\nStep 12 complete.")
