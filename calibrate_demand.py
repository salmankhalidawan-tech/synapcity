from citylearn.citylearn import CityLearnEnv
from synapcity import config

env = CityLearnEnv(
    schema=config.DATASET_NAME,
    random_seed=config.RANDOM_SEED,
    simulation_end_time_step=(config.DEBUG_SIMULATION_END_TIME_STEP if config.DEBUG_MODE else None),
)
names = env.observation_names
dem_idx = [n.index("net_electricity_consumption") for n in names]
n_b = len(names)
obs, _ = env.reset()
hist = [[float(obs[b][dem_idx[b]])] for b in range(n_b)]
zero = [[0.0] * sp.shape[0] for sp in env.action_space]
done = False
while not done:
    obs, _, term, trunc, _ = env.step(zero)
    for b in range(n_b):
        hist[b].append(float(obs[b][dem_idx[b]]))
    done = term or trunc

W, WARM, MINREF = config.DEMAND_ROLLING_WINDOW, 12, 0.1
print("steps per building:", len(hist[0]))
for m in [1.0, 1.25, 1.5, 2.0]:
    flagged = total = 0
    for h in hist:
        for t in range(len(h)):
            prev = h[max(0, t - (W - 1)):t]
            total += 1
            if len(prev) >= WARM:
                ref = max(prev)
                if ref > MINREF and h[t] > m * ref:
                    flagged += 1
    print(f"peak-multiplier {m}: {flagged / total:.1%} of building-steps flagged with NO control")