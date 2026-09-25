from citylearn.citylearn import CityLearnEnv
from synapcity import config
from synapcity.reward import SynapCityRewardFunction
from synapcity.safety_gate import SafetyGateWrapper

base_env = CityLearnEnv(
    schema=config.DATASET_NAME,
    reward_function=SynapCityRewardFunction,
    random_seed=config.RANDOM_SEED,
    simulation_end_time_step=200,
)
env = SafetyGateWrapper(base_env, verbose=False)

obs, _ = env.reset()

for step in range(30):
    action = [space.sample() for space in base_env.action_space]

    socs_before = env.extract(obs, env._soc_idx, default=None)
    safe = env.is_safe(obs, action)

    a_vals = [float(a[0]) if hasattr(a, "__len__") else float(a) for a in action]

    print(f"step {step:2d} | soc_before={[round(s,3) if s is not None else None for s in socs_before]} "
          f"| action={[round(a,3) for a in a_vals]} "
          f"| SAFE={safe}")

    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, _ = env.reset()

print(f"\nSTORAGE_SOC_MIN={config.STORAGE_SOC_MIN}, STORAGE_SOC_MAX={config.STORAGE_SOC_MAX}")