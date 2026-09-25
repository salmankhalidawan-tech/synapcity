"""
Ablation study for RQ4: full / no_negotiator / no_safety_gate / neither.
Reuses the real NegotiatedSAC (Orchestrator-driven GSI) and the real
FederatedCoordinatorAgent from train_synapcity.py, and the same
per-episode training loop as train_baseline.py / train_synapcity.py,
so ablation runs are directly comparable to the main runs.
Run one config at a time: python ablation.py <config_name>
"""
import os
import sys

from citylearn.citylearn import CityLearnEnv
from citylearn.agents.sac import SAC

from synapcity import config
from synapcity.reward import SynapCityRewardFunction
from synapcity.safety_gate import SafetyGateWrapper, ShieldAwareUpdateMixin
from synapcity.negotiator import ProspectTheoryNegotiator
from synapcity.orchestrator import OrchestratorAgent
from synapcity.federated_coordinator import FederatedCoordinatorAgent
from train_synapcity import NegotiatedSAC   # reuse the real, GSI-driven agent

CONFIGS = {
    "full":           dict(use_gate=True,  use_negotiator=True),
    "no_negotiator":  dict(use_gate=True,  use_negotiator=False),
    "no_safety_gate": dict(use_gate=False, use_negotiator=True),
    "neither":        dict(use_gate=False, use_negotiator=False),
}


class PlainShieldedSAC(ShieldAwareUpdateMixin, SAC):
    pass


def run_configuration(name):
    use_gate = CONFIGS[name]["use_gate"]
    use_negotiator = CONFIGS[name]["use_negotiator"]
    print(f"=== {name} (gate={use_gate}, negotiator={use_negotiator}), seed={config.RANDOM_SEED} ===")

    base_env = CityLearnEnv(
        schema=config.DATASET_NAME,
        reward_function=SynapCityRewardFunction,
        random_seed=config.RANDOM_SEED,
        simulation_end_time_step=(config.DEBUG_SIMULATION_END_TIME_STEP if config.DEBUG_MODE else None),
    )
    env = SafetyGateWrapper(base_env, verbose=False) if use_gate else base_env

    common_kwargs = dict(
        end_exploration_time_step=config.SAC_END_EXPLORATION_TIME_STEP,
        standardize_start_time_step=config.SAC_STANDARDIZE_START_TIME_STEP,
    )

    if use_negotiator:
        agent = NegotiatedSAC(env, negotiator=ProspectTheoryNegotiator(),
                              orchestrator=OrchestratorAgent(), **common_kwargs)
    else:
        agent = PlainShieldedSAC(env, **common_kwargs)

    coordinator = FederatedCoordinatorAgent() if use_gate else None

    for ep in range(1, config.EPISODES + 1):
        is_deterministic = (config.EPISODES > 1 and ep == config.EPISODES)
        agent.learn(episodes=1, deterministic_finish=is_deterministic)
        if coordinator is not None:
            coordinator.broadcast_shield_updates(zone_id="Zone_1", episode=ep, safety_gate=env)

    kpis = base_env.evaluate()
    out_path = os.path.join(config.RESULTS_DIR, f"ablation_{name}_seed{config.RANDOM_SEED}_kpis.csv")
    kpis.to_csv(out_path, index=False)

    if use_gate:
        rate = sum(env.reason_counts.values()) / (env.total_steps * env.n_buildings)
        print(f"[{name}] Per-building intervention rate: {rate:.1%}")
        print(f"[{name}] Rejection reasons: {dict(env.reason_counts)}")
    print(f"[{name}] KPIs saved to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CONFIGS:
        print(f"Usage: python ablation.py <{'|'.join(CONFIGS)}>")
        sys.exit(1)
    run_configuration(sys.argv[1])