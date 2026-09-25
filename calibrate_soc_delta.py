"""
Improved calibration: fits delta_soc = slope * action via least-squares
regression, restricted to |action| > 0.3 to avoid small-denominator noise
that inflated the earlier ratio-based estimate to an unrealistic 0.85.
"""
import numpy as np
from citylearn.citylearn import CityLearnEnv
from synapcity import config
from synapcity.reward import SynapCityRewardFunction

env = CityLearnEnv(
    schema=config.DATASET_NAME,
    reward_function=SynapCityRewardFunction,
    random_seed=config.RANDOM_SEED,
    simulation_end_time_step=400,
)

obs_names = env.observation_names
soc_idx = [names.index("electrical_storage_soc") for names in obs_names]

obs, _ = env.reset()
a_vals, d_vals = [], []

for _ in range(350):
    action = [space.sample() for space in env.action_space]
    prev_soc = [float(obs[i][soc_idx[i]]) for i in range(len(obs))]
    obs, _, terminated, truncated, _ = env.step(action)
    next_soc = [float(obs[i][soc_idx[i]]) for i in range(len(obs))]

    for b in range(len(obs)):
        a_val = float(np.asarray(action[b]).flatten()[0])
        if abs(a_val) > 0.3:  # only trust well-separated, large actions
            a_vals.append(a_val)
            d_vals.append(next_soc[b] - prev_soc[b])

    if terminated or truncated:
        obs, _ = env.reset()

a_vals = np.array(a_vals)
d_vals = np.array(d_vals)
slope = float(np.sum(a_vals * d_vals) / np.sum(a_vals * a_vals))  # least-squares slope through origin

print(f"Samples used: {len(a_vals)}")
print(f"Regression slope (delta_soc per unit action): {slope:.4f}")
print(f"Max |delta_soc| observed in any single step: {np.max(np.abs(d_vals)):.4f}")
print(f"Suggested ASSUMED_MAX_SOC_DELTA_PER_STEP: {max(abs(slope), np.max(np.abs(d_vals))):.4f}")