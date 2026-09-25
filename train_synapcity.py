"""
The full 6-agent framework: Zone Agent (SAC) + SafetyGateWrapper (with Auditor)
+ Negotiator + Orchestrator + Federated Coordinator.
"""

import os
import numpy as np
import pandas as pd

from citylearn.citylearn import CityLearnEnv
from citylearn.agents.sac import SAC

from synapcity import config
from synapcity.reward import SynapCityRewardFunction
from synapcity.safety_gate import SafetyGateWrapper, ShieldAwareUpdateMixin
from synapcity.negotiator import ProspectTheoryNegotiator
from synapcity.orchestrator import OrchestratorAgent
from synapcity.federated_coordinator import FederatedCoordinatorAgent


class NegotiatedSAC(ShieldAwareUpdateMixin, SAC):
    def __init__(
        self,
        env,
        negotiator: ProspectTheoryNegotiator,
        orchestrator: OrchestratorAgent,
        **kwargs
    ):
        super().__init__(env, **kwargs)

        self.negotiator = negotiator
        self.orchestrator = orchestrator
        self._last_demand = 0.0

        # GSI logging
        self.gsi_log = []

        obs_names = env.observation_names

        # Track indices for demand, carbon, and pricing
        self._demand_idx = [
            names.index("net_electricity_consumption")
            if "net_electricity_consumption" in names else None
            for names in obs_names
        ]

        self._carbon_idx = [
            names.index("carbon_intensity")
            if "carbon_intensity" in names else None
            for names in obs_names
        ]

        self._price_idx = [
            names.index("electricity_pricing")
            if "electricity_pricing" in names else None
            for names in obs_names
        ]

    def _update_last_demand(self, observations):
        vals = [
            float(b_obs[idx])
            for b_obs, idx in zip(observations, self._demand_idx)
            if idx is not None
        ]

        if vals:
            self._last_demand = float(np.mean(vals))

    def predict(self, observations, deterministic=None):
        self._update_last_demand(observations)

        actions = super().predict(
            observations,
            deterministic=deterministic
        )

        # Use Orchestrator to decompose macro grid stress
        # into zone subgoals
        carbon_i = self._carbon_idx[0] if self._carbon_idx else None
        price_i = self._price_idx[0] if self._price_idx else None

        subgoals = self.orchestrator.decompose_subgoals(
            observations,
            carbon_idx=carbon_i,
            price_idx=price_i
        )

        gsi = subgoals.get(
            "grid_stress_index",
            0.0
        )

        # Log GSI
        self.gsi_log.append(gsi)

        # Dynamically shift Negotiator parameters
        # based on Orchestrator's GSI
        incentive_value = 0.5 * (
            1.0 + (gsi * 0.5)
        )

        perceived_discomfort = 0.3 * max(
            0.1,
            (1.0 - gsi)
        )

        return [
            self.negotiator.scale_action(
                np.asarray(a),
                self._last_demand,
                incentive_value,
                perceived_discomfort
            )
            for a in actions
        ]


def main():
    os.makedirs(
        config.RESULTS_DIR,
        exist_ok=True
    )

    base_env = CityLearnEnv(
        schema=config.DATASET_NAME,
        reward_function=SynapCityRewardFunction,
        random_seed=config.RANDOM_SEED,
        simulation_end_time_step=(
            config.DEBUG_SIMULATION_END_TIME_STEP
            if config.DEBUG_MODE
            else None
        ),
    )

    # SafetyGateWrapper internally initializes
    # the Compliance/Auditor Agent
    env = SafetyGateWrapper(
        base_env,
        verbose=True
    )

    # Initialize the remaining agents
    negotiator = ProspectTheoryNegotiator()
    orchestrator = OrchestratorAgent()
    coordinator = FederatedCoordinatorAgent()

    agent = NegotiatedSAC(
        env,
        negotiator=negotiator,
        orchestrator=orchestrator,
        end_exploration_time_step=(
            config.SAC_END_EXPLORATION_TIME_STEP
        ),
        standardize_start_time_step=(
            config.SAC_STANDARDIZE_START_TIME_STEP
        ),
    )

    print(
        f"[synapcity] Training for {config.EPISODES} episodes "
        f"on dataset '{config.DATASET_NAME}'..."
    )

    # Manual episode loop to trigger Federated Coordinator
    # at the end of each episode
    for ep in range(
        1,
        config.EPISODES + 1
    ):
        is_deterministic = (
            config.EPISODES > 1
            and ep == config.EPISODES
        )

        agent.learn(
            episodes=1,
            deterministic_finish=is_deterministic
        )

        # Broadcast the local zone's shield failures
        # to the global ledger
        coordinator.broadcast_shield_updates(
            zone_id="Zone_1",
            episode=ep,
            safety_gate=env
        )

    # Evaluate the base environment
    kpis = base_env.evaluate()

    out_path = os.path.join(
        config.RESULTS_DIR,
        "synapcity_kpis.csv"
    )

    kpis.to_csv(
        out_path,
        index=False
    )

    # ---------------------------------------------------------
    # GSI LOGGING
    # ---------------------------------------------------------

    gsi_path = os.path.join(
        config.RESULTS_DIR,
        "synapcity_gsi_log.csv"
    )

    pd.DataFrame(
        {
            "gsi": agent.gsi_log
        }
    ).to_csv(
        gsi_path,
        index=False
    )

    print(
        f"[synapcity] GSI log: n={len(agent.gsi_log)}, "
        f"min={min(agent.gsi_log):.3f}, "
        f"max={max(agent.gsi_log):.3f}, "
        f"mean={sum(agent.gsi_log) / len(agent.gsi_log):.3f}"
    )

    print(
        f"[synapcity] GSI log saved to {gsi_path}"
    )

    print(
        f"[synapcity] Done. KPIs saved to {out_path}"
    )

    # ---------------------------------------------------------
    # SAFETY GATE METRICS
    # ---------------------------------------------------------

    print(
        "[synapcity] Steps with at least one building "
        f"intervened: {env.rejection_rate():.2%} "
        f"({env.rejection_count}/{env.total_steps})"
    )

    print(kpis.head(20))

    print(
        "[synapcity] Per-episode rejection rates: "
        f"{[f'{r:.1%}' for r in env.episode_rejection_rates()]}"
    )

    print(
        "[synapcity] Rejection reasons (building-steps): "
        f"{dict(env.reason_counts)}"
    )

    print(
        "[synapcity] Per-building intervention rate: "
        f"{sum(env.reason_counts.values()) / (env.total_steps * env.n_buildings):.1%}"
    )


if __name__ == "__main__":
    main()