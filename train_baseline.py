"""
Baseline for RQ3: a plain SAC agent, no safety gate, no negotiator.
"""
import os

from citylearn.citylearn import CityLearnEnv
from citylearn.agents.sac import SAC

from synapcity import config
from synapcity.reward import SynapCityRewardFunction


def main():
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    env = CityLearnEnv(
        schema=config.DATASET_NAME,
        reward_function=SynapCityRewardFunction,
        random_seed=config.RANDOM_SEED,
        simulation_end_time_step=(config.DEBUG_SIMULATION_END_TIME_STEP if config.DEBUG_MODE else None),
    )

    agent = SAC(
    env,
    end_exploration_time_step=config.SAC_END_EXPLORATION_TIME_STEP,
    standardize_start_time_step=config.SAC_STANDARDIZE_START_TIME_STEP,
)
    print(f"[baseline] Training for {config.EPISODES} episodes on dataset '{config.DATASET_NAME}'...")
    for ep in range(1, config.EPISODES + 1):
        agent.learn(episodes=1,
                    deterministic_finish=(config.EPISODES > 1 and ep == config.EPISODES))

    kpis = env.evaluate()
    out_path = os.path.join(config.RESULTS_DIR, "baseline_kpis.csv")
    kpis.to_csv(out_path, index=False)
    print(f"[baseline] Done. KPIs saved to {out_path}")
    print(kpis.head(20))


if __name__ == "__main__":
    main()