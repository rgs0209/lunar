"""
step13_14_resilience_comparison.py
====================================
Step 13: Compute mission resilience metrics for each policy.
Step 14: Compare policies with plots and a ranked summary table.

Inputs  (edit paths as needed):
  baseline_policy_results.csv
  scenario_results.csv
  q_learning_summary.csv
  q_learning_episode_metrics.csv

Outputs:
  outputs/resilience_metrics.csv
  outputs/policy_comparison_table.csv
  outputs/policy_comparison_plots.png
  outputs/learning_curve.png          (Q-learning convergence)
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os, math

os.makedirs('outputs', exist_ok=True)

# ================================================================
# PATHS — edit to match your folder layout
# ================================================================
BASELINE_CSV  = r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern\Intern_4_policy_rl_resilience\outputs\Reaward_q_learning\policy_based_results\baseline_policy_results.csv"
SCENARIO_CSV  = r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern\Intern_4_policy_rl_resilience\outputs\Reaward_q_learning\Scenario_tests\scenario_results.csv"
QL_SUMMARY    = r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern\Intern_4_policy_rl_resilience\outputs\Reaward_q_learning\q-learning_results\q_learning_summary.csv"
QL_EPISODES   = r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern\Intern_4_policy_rl_resilience\outputs\Reaward_q_learning\q-learning_results\q_learning_episode_metrics.csv"
OUT_DIR       = r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern\Intern_4_policy_rl_resilience\outputs\Reaward_q_learning"

NOMINAL_BUDGET = 650
POLICIES = ['Shortest Path', 'Safest Path', 'Science Priority',
            'Uncertainty Aware', 'Q-Learning']

COLORS = {
    'Shortest Path'    : '#2196F3',
    'Safest Path'      : '#4CAF50',
    'Science Priority' : '#FF9800',
    'Uncertainty Aware': '#9C27B0',
    'Q-Learning'       : '#F44336',
}

# ================================================================
# LOAD DATA
# ================================================================
print("Loading data ...")
bl  = pd.read_csv(BASELINE_CSV)
sc  = pd.read_csv(SCENARIO_CSV)
qls = pd.read_csv(QL_SUMMARY)
ep  = pd.read_csv(QL_EPISODES)

# Add Q-Learning nominal row to baseline dataframe for unified processing
ql_nominal = {
    'policy'          : 'Q-Learning',
    'success'         : True,
    'steps'           : float(qls['eval_avg_steps'].iloc[0]),
    'distance_m'      : float(qls['eval_avg_steps'].iloc[0]) * 25.0,
    'terrain_exposure': None,
    'shadow_exposure' : None,
    'science_return'  : 81.776,                          # ← moved here
    'avg_confidence'  : None,
    'energy_proxy'    : float(qls['eval_avg_energy'].iloc[0]),  # ← restored
    'hazard_exposure' : 79,                              # avg of S1/S4/S5: (62+88+88)/3
    'within_energy_budget': True,
    'recovery_after_failure': 'N/A',
    'runtime_sec'     : float(qls['train_time_s'].iloc[0]),
}
bl_full = pd.concat([bl, pd.DataFrame([ql_nominal])], ignore_index=True)

print(f"Baseline rows    : {len(bl_full)}")
print(f"Scenario rows    : {len(sc)}")
print(f"Training episodes: {len(ep):,}")

# Number of scenarios (exclude S6 comm delay — all zeros, not representative)
N_SCENARIOS = sc['scenario_id'].nunique()
print(f"Scenarios        : {N_SCENARIOS}")


# ================================================================
# STEP 13 — RESILIENCE METRICS
# ================================================================
print("\n=== STEP 13: Computing Resilience Metrics ===")

records = []

for pol in POLICIES:
    # ── Nominal baseline values ──────────────────────────────────
    bl_row  = bl_full[bl_full['policy'] == pol].iloc[0]
    nom_steps   = float(bl_row['steps'])       if not pd.isna(bl_row['steps'])           else None
    nom_energy  = float(bl_row['energy_proxy'])if not pd.isna(bl_row['energy_proxy'])    else None
    nom_science = float(bl_row['science_return']) if not pd.isna(bl_row['science_return']) else None
    nom_hazard  = float(bl_row['hazard_exposure']) if (
        'hazard_exposure' in bl_row and not pd.isna(bl_row.get('hazard_exposure'))) else None
    nom_terrain = float(bl_row['terrain_exposure']) if (
        'terrain_exposure' in bl_row and not pd.isna(bl_row.get('terrain_exposure'))) else None
    nom_shadow  = float(bl_row['shadow_exposure']) if (
        'shadow_exposure' in bl_row and not pd.isna(bl_row.get('shadow_exposure'))) else None

    # ── Scenario rows for this policy ───────────────────────────
    pol_sc = sc[sc['policy'] == pol].copy()

    # Exclude S6 (comm delay all-zero) from aggregate metrics
    pol_sc_valid = pol_sc[pol_sc['scenario_id'] != 6]

    n_total   = len(pol_sc_valid)
    n_success = pol_sc_valid['success'].sum()

    # 1. Success Rate (across scenarios 1-5)
    success_rate = n_success / n_total if n_total > 0 else 0.0

    # 2. Avg Travel Distance (successful runs only, in metres)
    succ_rows    = pol_sc_valid[pol_sc_valid['success'] == True]
    avg_steps    = succ_rows['steps'].mean()    if len(succ_rows) > 0 else 0.0
    avg_dist_m   = succ_rows['distance_m'].mean() if len(succ_rows) > 0 else 0.0

    # 3. Hazard Exposure (mean hazard cells over successful runs)
    avg_hazard   = succ_rows['hazard_exposure'].mean() if len(succ_rows) > 0 else 0.0

    # 4. Science Return (mean over successful runs)
    avg_science  = succ_rows['science_return'].mean() if len(succ_rows) > 0 else 0.0

    # 5. Energy Efficiency (mean energy as % of budget)
    avg_energy   = succ_rows['energy_proxy'].mean() if len(succ_rows) > 0 else 0.0
    energy_eff   = (1.0 - avg_energy / NOMINAL_BUDGET) * 100.0  # higher = more efficient

    # 6. Recovery After Failure
    #    = mean % of nominal science retained across ALL scenarios (incl. failures → 0)
    science_vals = pol_sc_valid.apply(
        lambda r: float(r['science_return']) if r['success'] else 0.0, axis=1)
    if nom_science and nom_science > 0:
        recovery = (science_vals.mean() / nom_science) * 100.0
    else:
        recovery = 0.0

    # 7. Policy Execution Time
    #    A* policies: mean runtime from scenario CSV
    #    Q-Learning: single lookup (negligible), report eval loop time
    if pol == 'Q-Learning':
        exec_time_ms = pol_sc_valid['runtime_sec'].mean() * 1000.0
    else:
        exec_time_ms = pol_sc_valid['runtime_sec'].mean() * 1000.0

    # Nominal planning time from baseline
    nom_runtime_ms = float(bl_row['runtime_sec']) * 1000.0 if not pd.isna(
        bl_row['runtime_sec']) else exec_time_ms

    # 8. Policy Memory (storage size)
    if pol == 'Q-Learning':
        policy_kb     = 40.0          # q_policy_map.npy: 200×200 uint8
        policy_type   = 'Lookup table'
        onboard       = 'YES — O(1) lookup, 40 KB'
        onboard_score = 5             # 1-5 scale
    else:
        policy_kb     = 0.0           # A* computes path on the fly, no stored policy
        policy_type   = 'Online A*'
        onboard_score = 2
        onboard       = 'PARTIAL — requires full grid in RAM + A* compute'

    # 9. Onboard suitability note
    if pol == 'Shortest Path':
        onboard = 'PARTIAL — fast A* but ignores hazards; unsafe onboard'
        onboard_score = 2
    elif pol == 'Safest Path':
        onboard = 'PARTIAL — safer but needs full risk map + heap; moderate cost'
        onboard_score = 3
    elif pol == 'Science Priority':
        onboard = 'PARTIAL — same as Safest; science map also needed'
        onboard_score = 3
    elif pol == 'Uncertainty Aware':
        onboard = 'PARTIAL — highest A* cost; confidence map also needed'
        onboard_score = 3

    # ── Step degradation vs nominal ─────────────────────────────
    step_delta = avg_steps - nom_steps if nom_steps else 0.0

    rec = {
        'policy'               : pol,
        # Core metrics
        'success_rate_pct'     : round(success_rate * 100, 1),
        'avg_steps'            : round(avg_steps, 1),
        'avg_distance_m'       : round(avg_dist_m, 1),
        'avg_hazard_cells'     : round(avg_hazard, 1),
        'avg_science_return'   : round(avg_science, 3),
        'avg_energy_used'      : round(avg_energy, 1),
        'energy_efficiency_pct': round(energy_eff, 1),
        'recovery_pct'         : round(recovery, 1),
        # Nominal baseline reference
        'nominal_steps'        : nom_steps,
        'nominal_energy'       : nom_energy,
        'nominal_science'      : nom_science,
        'nominal_hazard'       : nom_hazard,
        'step_delta_vs_nominal': round(step_delta, 1),
        # Compute
        'exec_time_ms'         : round(exec_time_ms, 3),
        'nominal_plan_time_ms' : round(nom_runtime_ms, 3),
        # Storage
        'policy_size_kb'       : policy_kb,
        'policy_type'          : policy_type,
        'onboard_suitability'  : onboard,
        'onboard_score'        : onboard_score,
        # Scenario counts
        'n_scenarios_tested'   : n_total,
        'n_scenarios_passed'   : int(n_success),
        'n_scenarios_failed'   : int(n_total - n_success),
    }
    records.append(rec)
    print(f"\n  {pol}:")
    print(f"    Success rate       : {rec['success_rate_pct']}%")
    print(f"    Avg steps          : {rec['avg_steps']}")
    print(f"    Avg energy         : {rec['avg_energy_used']} / {NOMINAL_BUDGET}")
    print(f"    Energy efficiency  : {rec['energy_efficiency_pct']}%")
    print(f"    Avg science return : {rec['avg_science_return']:.3f}")
    print(f"    Avg hazard cells   : {rec['avg_hazard_cells']}")
    print(f"    Recovery %         : {rec['recovery_pct']}%")
    print(f"    Exec time (ms)     : {rec['exec_time_ms']:.3f}")
    print(f"    Policy size        : {rec['policy_size_kb']:.0f} KB")
    print(f"    Onboard            : {rec['onboard_suitability']}")

metrics_df = pd.DataFrame(records)
metrics_path = os.path.join(OUT_DIR, 'resilience_metrics.csv')
metrics_df.to_csv(metrics_path, index=False)
print(f"\nSaved: {metrics_path}")


# ================================================================
# STEP 14 — POLICY COMPARISON
# ================================================================
print("\n=== STEP 14: Generating Comparison Plots ===")

# ── Normalise metrics for radar chart (0=worst, 1=best) ─────────
radar_metrics = {
    'Success\nRate'      : ('success_rate_pct',      True,  100.0),
    'Science\nReturn'    : ('avg_science_return',     True,  None),
    'Energy\nEfficiency' : ('energy_efficiency_pct',  True,  None),
    'Low\nHazard'        : ('avg_hazard_cells',       False, None),  # lower=better
    'Recovery\n%'        : ('recovery_pct',           True,  None),
    'Onboard\nScore'     : ('onboard_score',          True,  5.0),
}

def normalise(vals, higher_better, fixed_max=None):
    arr = np.array(vals, dtype=float)
    mn, mx = arr.min(), (fixed_max if fixed_max else arr.max())
    if mx == mn:
        return np.ones_like(arr) * 0.5
    norm = (arr - mn) / (mx - mn)
    return norm if higher_better else 1.0 - norm

radar_scores = {}
for label, (col, hb, fmax) in radar_metrics.items():
    vals = [metrics_df[metrics_df['policy']==p][col].values[0] for p in POLICIES]
    radar_scores[label] = normalise(vals, hb, fmax)


# ================================================================
# FIGURE 1: Main comparison (2×3 subplots)
# ================================================================
fig1, axes = plt.subplots(2, 3, figsize=(18, 11))
fig1.suptitle(
    'Step 14 — Policy Comparison\n'
    '200×200 Lunar Grid | 25 m/cell | 5 Baseline Policies | 6 Failure Scenarios',
    fontsize=14, fontweight='bold', y=1.01
)

x    = np.arange(len(POLICIES))
cols = [COLORS[p] for p in POLICIES]
xlbls = [p.replace(' ', '\n') for p in POLICIES]

# ── Plot A: Success Rate ─────────────────────────────────────────
ax = axes[0, 0]
bars = ax.bar(x, [metrics_df[metrics_df['policy']==p]['success_rate_pct'].values[0]
                  for p in POLICIES], color=cols, alpha=0.85, edgecolor='white')
for bar, val in zip(bars, [metrics_df[metrics_df['policy']==p]['success_rate_pct'].values[0]
                             for p in POLICIES]):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
            f"{val:.0f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(xlbls, fontsize=8)
ax.set_ylabel('Success Rate (%)', fontsize=10)
ax.set_title('A. Success Rate Across Scenarios', fontweight='bold')
ax.set_ylim(0, 115)
ax.axhline(100, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# ── Plot B: Energy Used ──────────────────────────────────────────
ax = axes[0, 1]
nom_e = [metrics_df[metrics_df['policy']==p]['nominal_energy'].values[0] for p in POLICIES]
avg_e = [metrics_df[metrics_df['policy']==p]['avg_energy_used'].values[0] for p in POLICIES]
w = 0.35
ax.bar(x - w/2, nom_e, w, color=cols, alpha=0.5, label='Nominal', edgecolor='white')
ax.bar(x + w/2, avg_e, w, color=cols, alpha=0.9, label='Scenario Avg', edgecolor='white')
ax.axhline(NOMINAL_BUDGET, color='black', linestyle='--', linewidth=1.2, label='Budget (650)')
ax.axhline(430, color='red', linestyle=':', linewidth=1.0, label='S3 Budget (430)')
ax.set_xticks(x); ax.set_xticklabels(xlbls, fontsize=8)
ax.set_ylabel('Energy Used (cost units)', fontsize=10)
ax.set_title('B. Energy Usage: Nominal vs Scenario Average', fontweight='bold')
ax.legend(fontsize=8, loc='upper right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# ── Plot C: Science Return ───────────────────────────────────────
ax = axes[0, 2]
nom_s = [metrics_df[metrics_df['policy']==p]['nominal_science'].values[0] for p in POLICIES]
avg_s = [metrics_df[metrics_df['policy']==p]['avg_science_return'].values[0] for p in POLICIES]
ax.bar(x - w/2, nom_s, w, color=cols, alpha=0.5, label='Nominal', edgecolor='white')
ax.bar(x + w/2, avg_s, w, color=cols, alpha=0.9, label='Scenario Avg', edgecolor='white')
ax.set_xticks(x); ax.set_xticklabels(xlbls, fontsize=8)
ax.set_ylabel('Science Return (cumulative)', fontsize=10)
ax.set_title('C. Science Return: Nominal vs Scenario Average', fontweight='bold')
ax.legend(fontsize=8)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# ── Plot D: Hazard Exposure ──────────────────────────────────────
ax = axes[1, 0]
nom_h = [metrics_df[metrics_df['policy']==p]['nominal_hazard'].values[0]
         if metrics_df[metrics_df['policy']==p]['nominal_hazard'].values[0] is not None
         else 0 for p in POLICIES]
avg_h = [metrics_df[metrics_df['policy']==p]['avg_hazard_cells'].values[0] for p in POLICIES]
ax.bar(x - w/2, nom_h, w, color=cols, alpha=0.5, label='Nominal', edgecolor='white')
ax.bar(x + w/2, avg_h, w, color=cols, alpha=0.9, label='Scenario Avg', edgecolor='white')
ax.set_xticks(x); ax.set_xticklabels(xlbls, fontsize=8)
ax.set_ylabel('Hazard Cells Visited', fontsize=10)
ax.set_title('D. Hazard Exposure (lower = safer)', fontweight='bold')
ax.legend(fontsize=8)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# ── Plot E: Recovery % ───────────────────────────────────────────
ax = axes[1, 1]
rec = [metrics_df[metrics_df['policy']==p]['recovery_pct'].values[0] for p in POLICIES]
bars = ax.bar(x, rec, color=cols, alpha=0.85, edgecolor='white')
for bar, val in zip(bars, rec):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
            f"{val:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.axhline(100, color='gray', linestyle='--', linewidth=1.0, label='100% = nominal')
ax.set_xticks(x); ax.set_xticklabels(xlbls, fontsize=8)
ax.set_ylabel('Recovery After Failure (%)', fontsize=10)
ax.set_title('E. Recovery: Science Retained vs Nominal', fontweight='bold')
ax.legend(fontsize=8)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# ── Plot F: Execution Time ───────────────────────────────────────
ax = axes[1, 2]
times = [metrics_df[metrics_df['policy']==p]['exec_time_ms'].values[0] for p in POLICIES]
bars = ax.bar(x, times, color=cols, alpha=0.85, edgecolor='white')
for bar, val in zip(bars, times):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
            f"{val:.1f}ms", ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(xlbls, fontsize=8)
ax.set_ylabel('Mean Execution Time (ms)', fontsize=10)
ax.set_title('F. Policy Execution Time', fontweight='bold')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.tight_layout()
p1 = os.path.join(OUT_DIR, 'policy_comparison_plots.png')
plt.savefig(p1, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {p1}")


# ================================================================
# FIGURE 2: Radar chart + scenario heatmap
# ================================================================
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 7),
                            gridspec_kw={'width_ratios': [1, 1.4]})
fig2.suptitle('Step 14 — Resilience Radar & Scenario Heatmap',
              fontsize=13, fontweight='bold')

# ── Radar chart ──────────────────────────────────────────────────
ax_r = axes2[0]
labels  = list(radar_scores.keys())
N       = len(labels)
angles  = [n / float(N) * 2 * math.pi for n in range(N)]
angles += angles[:1]

ax_r = plt.subplot(121, polar=True)
ax_r.set_theta_offset(math.pi / 2)
ax_r.set_theta_direction(-1)
plt.xticks(angles[:-1], labels, size=9)
ax_r.set_rlabel_position(0)
plt.yticks([0.25, 0.5, 0.75, 1.0], ['0.25','0.5','0.75','1.0'], size=7, color='grey')
plt.ylim(0, 1)

for pi, pol in enumerate(POLICIES):
    vals = [radar_scores[lbl][pi] for lbl in labels]
    vals += vals[:1]
    ax_r.plot(angles, vals, linewidth=2, linestyle='solid',
              color=COLORS[pol], label=pol)
    ax_r.fill(angles, vals, color=COLORS[pol], alpha=0.08)

ax_r.set_title('Resilience Radar\n(normalised, higher=better)',
               fontsize=11, fontweight='bold', pad=15)
ax_r.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=8)

# ── Scenario heatmap ─────────────────────────────────────────────
ax_h = axes2[1]

SC_NAMES = ['S1\nDropout', 'S2\nBlocked', 'S3\nEnergy',
            'S4\nScience', 'S5\nTerrain', 'S6\nDelay']
SC_IDS   = [1, 2, 3, 4, 5, 6]

mat = np.zeros((len(SC_IDS), len(POLICIES)))
for si, sc_id in enumerate(SC_IDS):
    for pi, pol in enumerate(POLICIES):
        row = sc[(sc['scenario_id']==sc_id) & (sc['policy']==pol)]
        mat[si, pi] = 1.0 if (len(row) > 0 and row['success'].values[0]) else 0.0

im = ax_h.imshow(mat, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
ax_h.set_xticks(range(len(POLICIES)))
ax_h.set_xticklabels([p.replace(' ','\n') for p in POLICIES], fontsize=9)
ax_h.set_yticks(range(len(SC_IDS)))
ax_h.set_yticklabels(SC_NAMES, fontsize=9)
ax_h.set_title('Scenario Pass/Fail Heatmap\n(green=pass, red=fail)',
               fontsize=11, fontweight='bold')

for i in range(len(SC_IDS)):
    for j in range(len(POLICIES)):
        sym = '✓' if mat[i, j] > 0.5 else '✗'
        ax_h.text(j, i, sym, ha='center', va='center',
                  fontsize=14, color='black', fontweight='bold')

plt.colorbar(im, ax=ax_h, shrink=0.6)
plt.tight_layout()
p2 = os.path.join(OUT_DIR, 'policy_comparison_radar.png')
plt.savefig(p2, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {p2}")


# ================================================================
# FIGURE 3: Q-Learning Learning Curve
# ================================================================
print("Generating learning curve ...")

fig3, axes3 = plt.subplots(1, 2, figsize=(14, 5))
fig3.suptitle('Q-Learning Training Convergence\n'
              '150,000 episodes | γ=0.99 | α=0.1 | ε-greedy decay',
              fontsize=12, fontweight='bold')

window = 500
ep['success_smooth'] = ep['success'].rolling(window, min_periods=1).mean() * 100
ep['reward_smooth']  = ep['total_reward'].rolling(window, min_periods=1).mean()
ep['steps_smooth']   = ep['steps'].rolling(window, min_periods=1).mean()

ax = axes3[0]
ax.plot(ep['episode'], ep['success_smooth'], color='#4CAF50', linewidth=1.5)
ax.axhline(100, color='gray', linestyle='--', linewidth=0.8)
ax.set_xlabel('Episode'); ax.set_ylabel('Win Rate (%, 500-ep rolling avg)')
ax.set_title('Win Rate Convergence')
ax.set_ylim(-5, 110)
# Mark convergence point (first time 5-ep avg hits 100%)
conv_ep = ep[ep['success_smooth'] >= 99.0]['episode'].min()
if not pd.isna(conv_ep):
    ax.axvline(conv_ep, color='red', linestyle=':', linewidth=1.2)
    ax.text(conv_ep, 50, f'  ≥99%\n  ep {conv_ep:,}',
            color='red', fontsize=8)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

ax = axes3[1]
ax.plot(ep['episode'], ep['reward_smooth'], color='#2196F3', linewidth=1.5)
ax.set_xlabel('Episode'); ax.set_ylabel('Total Reward (500-ep rolling avg)')
ax.set_title('Reward Convergence')
ax2 = ax.twinx()
ax2.plot(ep['episode'], ep['steps_smooth'], color='#FF9800',
         linewidth=1.0, alpha=0.7, linestyle='--')
ax2.set_ylabel('Steps (500-ep rolling avg)', color='#FF9800')
ax.spines['top'].set_visible(False)

plt.tight_layout()
p3 = os.path.join(OUT_DIR, 'learning_curve.png')
plt.savefig(p3, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {p3}")


# ================================================================
# POLICY COMPARISON TABLE (Step 14)
# ================================================================
print("\n=== STEP 14: Policy Comparison Table ===")

# Best policy per metric
best = {}
best['success_rate_pct']      = metrics_df.loc[metrics_df['success_rate_pct'].idxmax(), 'policy']
best['avg_science_return']    = metrics_df.loc[metrics_df['avg_science_return'].idxmax(), 'policy']
best['energy_efficiency_pct'] = metrics_df.loc[metrics_df['energy_efficiency_pct'].idxmax(), 'policy']
best['avg_hazard_cells']      = metrics_df.loc[metrics_df['avg_hazard_cells'].idxmin(), 'policy']
best['recovery_pct']          = metrics_df.loc[metrics_df['recovery_pct'].idxmax(), 'policy']
best['exec_time_ms']          = metrics_df.loc[metrics_df['exec_time_ms'].idxmin(), 'policy']
best['onboard_score']         = metrics_df.loc[metrics_df['onboard_score'].idxmax(), 'policy']

print("\nBest policy per metric:")
for metric, pol in best.items():
    print(f"  {metric:30s}: {pol}")

# Overall resilience score (normalised sum)
score_cols = ['success_rate_pct', 'avg_science_return',
              'energy_efficiency_pct', 'recovery_pct', 'onboard_score']
metrics_df['resilience_score'] = 0.0
for col in score_cols:
    col_vals = metrics_df[col].astype(float)
    mn, mx = col_vals.min(), col_vals.max()
    if mx > mn:
        metrics_df['resilience_score'] += (col_vals - mn) / (mx - mn)
# Subtract normalised hazard (lower is better)
hz = metrics_df['avg_hazard_cells'].astype(float)
mn, mx = hz.min(), hz.max()
if mx > mn:
    metrics_df['resilience_score'] -= (hz - mn) / (mx - mn)

metrics_df['resilience_score'] = metrics_df['resilience_score'].round(3)
metrics_df_sorted = metrics_df.sort_values('resilience_score', ascending=False)

print("\nOverall Resilience Ranking:")
for rank, (_, row) in enumerate(metrics_df_sorted.iterrows(), 1):
    print(f"  {rank}. {row['policy']:20s}  score={row['resilience_score']:.3f}  "
          f"success={row['success_rate_pct']}%  science={row['avg_science_return']:.1f}  "
          f"energy_eff={row['energy_efficiency_pct']:.1f}%")

# Save comparison table
comp_cols = [
    'policy', 'success_rate_pct', 'avg_steps', 'avg_distance_m',
    'avg_hazard_cells', 'avg_science_return', 'avg_energy_used',
    'energy_efficiency_pct', 'recovery_pct', 'exec_time_ms',
    'policy_size_kb', 'policy_type', 'onboard_score',
    'n_scenarios_passed', 'n_scenarios_failed', 'resilience_score'
]
comp_df = metrics_df_sorted[comp_cols]
comp_path = os.path.join(OUT_DIR, 'policy_comparison_table.csv')
comp_df.to_csv(comp_path, index=False)
print(f"\nSaved: {comp_path}")


# ================================================================
# BEST POLICY PER SCENARIO (qualitative summary)
# ================================================================
print("\n=== BEST POLICY PER SCENARIO ===")
scenario_names = {
    1: 'Sensor Dropout',
    2: 'Blocked Path',
    3: 'Limited Energy',
    4: 'Wrong Resource Est.',
    5: 'Terrain Uncertainty',
    6: 'Communication Delay',
}
for sc_id, sc_name in scenario_names.items():
    rows = sc[sc['scenario_id'] == sc_id]
    passing = rows[rows['success'] == True]
    if len(passing) == 0:
        print(f"  S{sc_id} {sc_name:25s}: ALL FAILED")
        continue
    # Best by science among passing
    best_sci = passing.loc[passing['science_return'].idxmax()]
    # Best by energy among passing
    best_eng = passing.loc[passing['energy_proxy'].idxmin()]
    print(f"  S{sc_id} {sc_name:25s}: "
          f"best_science={best_sci['policy']} ({best_sci['science_return']:.1f})  "
          f"best_energy={best_eng['policy']} ({best_eng['energy_proxy']:.1f})")

print("\nSteps 13 and 14 complete.")
print(f"Outputs saved to: {OUT_DIR}")