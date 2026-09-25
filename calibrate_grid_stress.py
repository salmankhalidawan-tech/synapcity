from citylearn.citylearn import CityLearnEnv
from synapcity import config
import numpy as np

env = CityLearnEnv(
    schema=config.DATASET_NAME,
    random_seed=config.RANDOM_SEED,
    simulation_end_time_step=(config.DEBUG_SIMULATION_END_TIME_STEP if config.DEBUG_MODE else None),
)
names = env.observation_names[0]
carbon_i = names.index("carbon_intensity") if "carbon_intensity" in names else None
price_i = names.index("electricity_pricing") if "electricity_pricing" in names else None
obs, _ = env.reset()
carbons, prices = [], []
zero = [[0.0] * sp.shape[0] for sp in env.action_space]
if carbon_i is not None: carbons.append(float(obs[0][carbon_i]))
if price_i is not None: prices.append(float(obs[0][price_i]))
done = False
while not done:
    obs, _, term, trunc, _ = env.step(zero)
    if carbon_i is not None: carbons.append(float(obs[0][carbon_i]))
    if price_i is not None: prices.append(float(obs[0][price_i]))
    done = term or trunc
print("steps:", len(carbons))
if carbons:
    print(f"carbon_intensity: min {min(carbons):.3f} max {max(carbons):.3f} mean {np.mean(carbons):.3f} median {np.median(carbons):.3f}")
if prices:
    print(f"electricity_pricing: min {min(prices):.3f} max {max(prices):.3f} mean {np.mean(prices):.3f} median {np.median(prices):.3f}")