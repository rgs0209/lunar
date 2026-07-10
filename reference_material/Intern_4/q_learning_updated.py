"""
Q-Learning — Lunar Rover Mission Resilience Simulation
Step 10: Train Q-learning offline on 200×200 grid
=======================================================
v5 — FINAL FIX (science farming diagnosis)

ROOT CAUSE of 0% win rate (all previous versions):
  Science reward during training = ~+5,985/ep (74 new cells × avg +81)
  Goal reward                    = ~+1,165/ep  (shaping + goal bonus)
  Farming is 5.1× more profitable → agent never navigates to goal.
  Q-values for "go to goal" never receive a positive signal.
  Epsilon locks at 0.05 by ep 30k → science farming policy is frozen in.

THE FIX:
  Remove science reward from TRAINING entirely.
  Q-learning optimises navigation only:
      training reward = shaping + movement penalties + goal reward
  Science return is measured in POST-TRAINING EVALUATION only.
  This is correct RL practice: train on a clean navigation signal,
  evaluate on the full mission reward function.

  With science removed:
    Go to goal  (230 steps): +995 shaping - 330 movement + 500 goal = +1165
    Wander 600 steps:          ~0 shaping - 862 movement + 0 goal   =  -862
    Goal is optimal by +2027 — agent will learn to reach it.
"""

import numpy as np
import pandas as pd
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time, os

os.makedirs('outputs', exist_ok=True)

# ================================================================
# HYPERPARAMETERS
# ================================================================
ALPHA         = 0.1
GAMMA         = 0.99
EPSILON_START = 1.0
EPSILON_END   = 0.05
EPSILON_DECAY = 0.9999     # hits 0.05 around ep ~60,000
EPISODES      = 150_000
MAX_STEPS     = 600        # ~2.6× BFS optimal path (230 steps)

# ================================================================
# ENVIRONMENT CONSTANTS
# ================================================================
GRID_ROWS    = 200
GRID_COLS    = 200
START        = (0, 199)
GOAL         = (199, 0)

TRAIN_ENERGY_BUDGET = 99_999   # unlimited during training
EVAL_ENERGY_BUDGET  = 650      # real deployment constraint

# Training reward components (navigation signal only)
R_GOAL          =  500.0
P_TERRAIN_SCALE =   -5.0
P_SHADOW_SCALE  =   -3.0
P_CONF_SCALE    =   -2.0
P_MOVE_SCALE    =   -1.0
P_ENERGY        =  -50.0
P_BOUNDARY      =   -1.0
P_BLOCK         =   -5.0
SHAPING_SCALE   =   -5.0   # net toward goal = +5 - 1.44 avg_mc = +3.56/step

# Evaluation reward components (full mission reward)
R_SCIENCE_SCALE = 150.0
SCIENCE_THRESH  =   0.5

ACTIONS = [
    (-1,  0), ( 1,  0), ( 0, -1), ( 0,  1),
    (-1, -1), (-1,  1), ( 1, -1), ( 1,  1),
]
NUM_ACTIONS  = 8
ACTION_NAMES = ['Up','Down','Left','Right',
                'Up-Left','Up-Right','Down-Left','Down-Right']

# ================================================================
# LOAD ENVIRONMENT
# ================================================================
print("Loading grid world...")
df = pd.read_csv(
    r"C:\Users\Amartiya\OneDrive\Desktop\amarthya sujai\NIT_Intern"
    r"\Intern_4_policy_rl_resilience\outputs\grid_world.csv"
)

TERRAIN_RISK   = df['terrain_risk'].values.reshape(GRID_ROWS, GRID_COLS).astype(np.float32)
SHADOW_RISK    = df['shadow_risk'].values.reshape(GRID_ROWS, GRID_COLS).astype(np.float32)
CONFIDENCE     = df['confidence'].values.reshape(GRID_ROWS, GRID_COLS).astype(np.float32)
SCIENCE_REWARD = df['science_reward'].values.reshape(GRID_ROWS, GRID_COLS).astype(np.float32)
MOVEMENT_COST  = df['movement_cost'].values.reshape(GRID_ROWS, GRID_COLS).astype(np.float32)
IS_PASSABLE    = df['is_passable'].values.reshape(GRID_ROWS, GRID_COLS).astype(bool)

NUM_STATES = GRID_ROWS * GRID_COLS

# Chebyshev distance to goal (for reward shaping)
rows_idx = np.arange(GRID_ROWS).reshape(-1, 1) * np.ones((1, GRID_COLS))
cols_idx = np.ones((GRID_ROWS, 1)) * np.arange(GRID_COLS).reshape(1, -1)
DIST_TO_GOAL = np.maximum(
    np.abs(rows_idx - GOAL[0]),
    np.abs(cols_idx - GOAL[1])
).astype(np.float32)

avg_mc = float(df[df['is_passable']==1]['movement_cost'].mean())
print(f"Grid: {GRID_ROWS}×{GRID_COLS} | States: {NUM_STATES:,} | Actions: {NUM_ACTIONS}")
print(f"Avg movement cost   : {avg_mc:.3f}")
print(f"Shaping scale       : {SHAPING_SCALE}  "
      f"(net per step toward goal: {-SHAPING_SCALE - avg_mc:+.2f})")
print(f"Science reward      : DISABLED during training | ENABLED in evaluation")
print(f"Training budget     : {TRAIN_ENERGY_BUDGET} (unlimited)")
print(f"Evaluation budget   : {EVAL_ENERGY_BUDGET}")
print(f"Expected: goal (+1165) >> wander (-862)  →  agent will learn goal navigation")


# ================================================================
# HELPERS
# ================================================================
def state_idx(r, c):
    return r * GRID_COLS + c


def train_step(row, col, action, energy_used):
    """
    Training step — NO science reward.
    Reward = shaping + movement penalties + goal reward only.
    """
    dr, dc  = ACTIONS[action]
    nr, nc  = row + dr, col + dc
    is_diag = (dr != 0 and dc != 0)
    dmul    = 1.4142 if is_diag else 1.0

    # Boundary
    if not (0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS):
        return row, col, P_BOUNDARY, False, energy_used

    # Impassable
    if not IS_PASSABLE[nr, nc]:
        return row, col, P_BLOCK, False, energy_used

    mc = float(MOVEMENT_COST[nr, nc])
    tr = float(TERRAIN_RISK[nr, nc])
    sh = float(SHADOW_RISK[nr, nc])
    cf = float(CONFIDENCE[nr, nc])

    # Navigation reward (NO science component)
    reward  = P_TERRAIN_SCALE * tr
    reward += P_SHADOW_SCALE  * sh
    reward += P_CONF_SCALE    * (1.0 - cf)
    reward += P_MOVE_SCALE    * mc * dmul

    # Potential-based shaping
    reward += SHAPING_SCALE * (
        float(DIST_TO_GOAL[nr, nc]) - float(DIST_TO_GOAL[row, col])
    )

    # Energy (unlimited during training — won't trigger)
    new_energy = energy_used + mc * dmul
    if new_energy > TRAIN_ENERGY_BUDGET:
        reward += P_ENERGY
        return nr, nc, reward, True, new_energy

    # Goal
    if nr == GOAL[0] and nc == GOAL[1]:
        reward += R_GOAL
        return nr, nc, reward, True, new_energy

    return nr, nc, reward, False, new_energy


def eval_step(row, col, action, energy_used, visited_science):
    """
    Evaluation step — FULL reward including science (first visit per episode).
    Uses real energy budget (650).
    """
    dr, dc  = ACTIONS[action]
    nr, nc  = row + dr, col + dc
    is_diag = (dr != 0 and dc != 0)
    dmul    = 1.4142 if is_diag else 1.0

    if not (0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS):
        return row, col, P_BOUNDARY, False, energy_used

    if not IS_PASSABLE[nr, nc]:
        return row, col, P_BLOCK, False, energy_used

    mc = float(MOVEMENT_COST[nr, nc])
    tr = float(TERRAIN_RISK[nr, nc])
    sh = float(SHADOW_RISK[nr, nc])
    cf = float(CONFIDENCE[nr, nc])
    sc = float(SCIENCE_REWARD[nr, nc])

    reward  = P_TERRAIN_SCALE * tr
    reward += P_SHADOW_SCALE  * sh
    reward += P_CONF_SCALE    * (1.0 - cf)
    reward += P_MOVE_SCALE    * mc * dmul

    # Science: first visit only
    if sc > SCIENCE_THRESH and (nr, nc) not in visited_science:
        reward += R_SCIENCE_SCALE * sc
        visited_science.add((nr, nc))

    new_energy = energy_used + mc * dmul
    if new_energy > EVAL_ENERGY_BUDGET:
        reward += P_ENERGY
        return nr, nc, reward, True, new_energy

    if nr == GOAL[0] and nc == GOAL[1]:
        reward += R_GOAL
        return nr, nc, reward, True, new_energy

    return nr, nc, reward, False, new_energy


# ================================================================
# TRAIN
# ================================================================
Q = np.zeros((NUM_STATES, NUM_ACTIONS), dtype=np.float32)

print(f"\nTraining: {EPISODES:,} episodes | max {MAX_STEPS} steps | "
      f"ε-decay={EPSILON_DECAY} | γ={GAMMA}")
t0 = time.time()

rewards_ep = []
success_ep = []
energy_ep  = []
steps_ep   = []
epsilon    = EPSILON_START

for ep in range(EPISODES):
    row, col     = START
    energy       = 0.0
    total_reward = 0.0
    success      = False

    for stp in range(MAX_STEPS):
        s = state_idx(row, col)

        action = (random.randint(0, NUM_ACTIONS - 1)
                  if random.random() < epsilon
                  else int(np.argmax(Q[s])))

        nr, nc, reward, done, energy = train_step(row, col, action, energy)
        ns = state_idx(nr, nc)

        Q[s, action] += ALPHA * (reward + GAMMA * np.max(Q[ns]) - Q[s, action])

        row, col      = nr, nc
        total_reward += reward

        if done:
            if (row, col) == GOAL:
                success = True
            break

    epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)
    rewards_ep.append(total_reward)
    success_ep.append(int(success))
    energy_ep.append(energy)
    steps_ep.append(stp + 1)

    if (ep + 1) % 5000 == 0:
        recent = success_ep[-1000:]
        wr     = sum(recent) / len(recent) * 100
        avg_r  = np.mean(rewards_ep[-1000:])
        print(f"  Ep {ep+1:>7,} | ε={epsilon:.4f} | "
              f"win_rate(1k)={wr:.1f}% | avg_reward={avg_r:.1f} | "
              f"elapsed={time.time()-t0:.0f}s")

train_time = time.time() - t0
train_wr   = sum(success_ep[-5000:]) / 5000 * 100
print(f"\nTraining done in {train_time:.1f}s  |  Train win rate (last 5k): {train_wr:.1f}%")


# ================================================================
# POST-TRAINING EVALUATION  (full reward, real energy budget)
# ================================================================
print(f"\nEvaluating with full reward function | budget={EVAL_ENERGY_BUDGET} ...")
EVAL_EPISODES = 1000
eval_success, eval_energy_used = [], []
eval_steps, eval_science       = [], []
eval_rewards                   = []

for _ in range(EVAL_EPISODES):
    row, col        = START
    energy          = 0.0
    success         = False
    visited_science = set()
    total_reward    = 0.0

    for stp in range(MAX_STEPS):
        s      = state_idx(row, col)
        action = int(np.argmax(Q[s]))     # greedy

        nr, nc, reward, done, energy = eval_step(
            row, col, action, energy, visited_science
        )
        row, col      = nr, nc
        total_reward += reward

        if done:
            if (row, col) == GOAL:
                success = True
            break

    eval_success.append(int(success))
    eval_energy_used.append(energy)
    eval_steps.append(stp + 1)
    eval_science.append(sum(
        float(SCIENCE_REWARD[r, c])
        for (r, c) in visited_science
    ))
    eval_rewards.append(total_reward)

eval_wr       = sum(eval_success) / EVAL_EPISODES * 100
success_steps = [s for s,ok in zip(eval_steps, eval_success) if ok]
print(f"Evaluation win rate      : {eval_wr:.1f}%")
print(f"Avg steps  (all)         : {np.mean(eval_steps):.1f}")
print(f"Avg steps  (successes)   : {np.mean(success_steps) if success_steps else 0:.1f}")
print(f"Avg energy used          : {np.mean(eval_energy_used):.1f} / {EVAL_ENERGY_BUDGET}")
print(f"Avg science collected    : {np.mean(eval_science):.3f}")
print(f"Avg total reward (eval)  : {np.mean(eval_rewards):.1f}")


# ================================================================
# SAVE OUTPUTS
# ================================================================
policy_map = np.argmax(Q, axis=1).reshape(GRID_ROWS, GRID_COLS).astype(np.uint8)

pd.DataFrame(Q, columns=ACTION_NAMES).to_csv(
    'outputs/q_learning_results.csv', index_label='state_id')
print("Saved: outputs/q_learning_results.csv")

pd.DataFrame({
    'episode'      : range(EPISODES),
    'total_reward' : rewards_ep,
    'success'      : success_ep,
    'steps'        : steps_ep,
    'energy_used'  : energy_ep,
}).to_csv('outputs/q_learning_episode_metrics.csv', index=False)

pd.DataFrame([{
    'policy'              : 'Q-Learning',
    'train_win_rate'      : f"{train_wr:.1f}%",
    'eval_win_rate'       : f"{eval_wr:.1f}%",
    'eval_avg_steps'      : f"{np.mean(eval_steps):.1f}",
    'eval_avg_energy'     : f"{np.mean(eval_energy_used):.1f}",
    'eval_avg_science'    : f"{np.mean(eval_science):.3f}",
    'eval_avg_reward'     : f"{np.mean(eval_rewards):.1f}",
    'q_table_entries'     : NUM_STATES * NUM_ACTIONS,
    'q_table_kb'          : round(NUM_STATES * NUM_ACTIONS * 4 / 1024, 1),
    'train_time_s'        : round(train_time, 1),
    'episodes'            : EPISODES,
    'gamma'               : GAMMA,
    'alpha'               : ALPHA,
    'shaping_scale'       : SHAPING_SCALE,
    'science_in_training' : False,
    'train_energy_budget' : TRAIN_ENERGY_BUDGET,
    'eval_energy_budget'  : EVAL_ENERGY_BUDGET,
}]).to_csv('outputs/q_learning_summary.csv', index=False)

np.save('outputs/q_policy_map.npy', policy_map)
print("Saved: outputs/q_policy_map.npy, q_learning_episode_metrics.csv, q_learning_summary.csv")


# ================================================================
# PLOTS
# ================================================================
W     = 500
r_arr = np.array(rewards_ep)
s_arr = np.array(success_ep, dtype=float)
e_arr = np.array(energy_ep)

fig, axes = plt.subplots(3, 1, figsize=(12, 10))
fig.suptitle('Q-Learning Training — 200×200 Lunar Rover (v5, navigation only)',
             fontsize=13)

axes[0].plot(r_arr, alpha=0.15, color='steelblue', linewidth=0.4)
axes[0].plot(range(W-1, EPISODES),
             np.convolve(r_arr, np.ones(W)/W, 'valid'),
             color='steelblue', linewidth=1.5, label=f'Rolling mean ({W} ep)')
axes[0].set_ylabel('Total Reward (training)')
axes[0].set_xlabel('Episode')
axes[0].set_title('Episode Reward — no science reward during training')
axes[0].legend()

axes[1].plot(range(W-1, EPISODES),
             np.convolve(s_arr, np.ones(W)/W, 'valid') * 100,
             color='green', linewidth=1.5)
axes[1].set_ylabel('Win Rate (%)')
axes[1].set_xlabel('Episode')
axes[1].set_ylim(0, 105)
axes[1].set_title(f'Success Rate (rolling {W}-ep window)')

axes[2].plot(range(W-1, EPISODES),
             np.convolve(e_arr, np.ones(W)/W, 'valid'),
             color='orange', linewidth=1.5, label='Training energy used')
axes[2].axhline(EVAL_ENERGY_BUDGET, color='red', linestyle='--',
                linewidth=1, label=f'Eval budget = {EVAL_ENERGY_BUDGET}')
axes[2].set_ylabel('Energy Used (cost units)')
axes[2].set_xlabel('Episode')
axes[2].set_title('Energy Used per Episode')
axes[2].legend()

plt.tight_layout()
plt.savefig('outputs/learning_curve.png', dpi=150, bbox_inches='tight')
plt.close()

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(policy_map, cmap='tab10', vmin=0, vmax=7, origin='upper')
ax.plot(START[1], START[0], 'g^', markersize=10, label='Start (0,199)')
ax.plot(GOAL[1],  GOAL[0],  'r*', markersize=12, label='Goal (199,0)')
cbar = plt.colorbar(im, ax=ax, ticks=range(8))
cbar.ax.set_yticklabels(ACTION_NAMES)
ax.set_title('Learned Policy Map — Q-Learning v5\n(greedy action per cell)')
ax.set_xlabel('col (25m steps)')
ax.set_ylabel('row (25m steps)')
ax.legend(loc='upper left')
plt.tight_layout()
plt.savefig('outputs/q_policy_map.png', dpi=150, bbox_inches='tight')
plt.close()

print("Saved: outputs/learning_curve.png, outputs/q_policy_map.png")
print("\nAll outputs saved.")