"""
SafetyGateWrapper: per-building, state-based pre-execution safety gate.
Each building is checked on its own; only unsafe buildings get a corrective
action. The gate passes its real rejection reason to the auditor.

Demand rule: a building is flagged when its current net demand exceeds
MAX_DEMAND_SPIKE_MULTIPLIER times the highest demand it saw in the trailing
window (config.DEMAND_ROLLING_WINDOW steps). The multiplier is calibrated on a
no-control run so that normal daily load cycles are not flagged.
"""
from typing import Any, List, Tuple, Optional
from collections import deque, Counter

import gymnasium as gym
import numpy as np

from . import config
from synapcity.auditor import ComplianceAuditorAgent


class SafetyGateWrapper(gym.Wrapper):
    CORRECTIVE_ACTION_MAGNITUDE = 0.3
    MIN_RECOVERY_ACTION = 0.1   # gentle push back into the safe SOC band
    DEMAND_WARMUP_STEPS = 12    # no spike check until this many prior readings exist
    DEMAND_MIN_REF = 0.1        # no spike check if the recent peak demand is below this

    def __init__(self, env: gym.Env, verbose: bool = False):
        super().__init__(env)
        self.verbose = verbose
        self.rejection_count = 0   # steps where at least one building was rejected
        self.total_steps = 0
        self.reason_counts = Counter()   # per-building rejection reasons
        self._current_obs: Optional[List[List[float]]] = None
        self.last_effective_action: Optional[Any] = None

        self._episode_rejections: List[int] = []
        self._episode_steps: List[int] = []
        self._current_episode_rejections = 0
        self._current_episode_steps = 0

        self.auditor = ComplianceAuditorAgent()

        obs_names: List[List[str]] = self.env.observation_names
        self.n_buildings = len(obs_names)

        self._demand_history = [
            deque(maxlen=config.DEMAND_ROLLING_WINDOW)
            for _ in range(self.n_buildings)
        ]

        self._soc_idx: List[Optional[int]] = [
            names.index("electrical_storage_soc")
            if "electrical_storage_soc" in names else None
            for names in obs_names
        ]

        self._demand_idx: List[Optional[int]] = [
            names.index("net_electricity_consumption")
            if "net_electricity_consumption" in names else None
            for names in obs_names
        ]

    def extract(self, obs_list, idx_list, default):
        return [
            float(b_obs[idx]) if idx is not None else default
            for b_obs, idx in zip(obs_list, idx_list)
        ]

    def check_building(self, b_idx, obs_b) -> Optional[str]:
        """Returns None if safe, else 'SOC_LOW', 'SOC_HIGH' or 'DEMAND_SPIKE'."""
        soc_i = self._soc_idx[b_idx]

        if soc_i is not None:
            soc = float(obs_b[soc_i])

            if soc < config.STORAGE_SOC_MIN:
                return "SOC_LOW"

            if soc > config.STORAGE_SOC_MAX:
                return "SOC_HIGH"

        dem_i = self._demand_idx[b_idx]

        if dem_i is not None:
            prev = list(self._demand_history[b_idx])[:-1]  # exclude current reading

            if len(prev) >= self.DEMAND_WARMUP_STEPS:
                ref = max(prev)

                if (
                    ref > self.DEMAND_MIN_REF
                    and float(obs_b[dem_i])
                    > config.MAX_DEMAND_SPIKE_MULTIPLIER * ref
                ):
                    return "DEMAND_SPIKE"

        return None

    def is_safe(self, current_obs, action=None) -> bool:
        return all(
            self.check_building(i, o) is None
            for i, o in enumerate(current_obs)
        )

    def record_demand(self, observations):
        for b_idx, obs_b in enumerate(observations):
            dem_i = self._demand_idx[b_idx]

            if dem_i is not None:
                self._demand_history[b_idx].append(
                    float(obs_b[dem_i])
                )

    def corrective_fallback_action(self, proposed_action, reasons):
        corrected = []

        for a, reason in zip(proposed_action, reasons):
            a_arr = np.asarray(a, dtype=float)

            if reason == "SOC_LOW":
                # Never discharge, and charge at least a little
                # so SOC leaves the empty state.
                corrected.append(
                    np.maximum(
                        a_arr,
                        self.MIN_RECOVERY_ACTION
                    )
                )

            elif reason == "SOC_HIGH":
                corrected.append(
                    np.minimum(
                        a_arr,
                        -self.MIN_RECOVERY_ACTION
                    )
                )

            elif reason == "DEMAND_SPIKE":
                corrected.append(
                    np.minimum(a_arr, 0.0)
                )   # never charge during a spike

            else:
                corrected.append(a_arr)

        return corrected

    def reset(self, **kwargs):
        if self._current_episode_steps > 0:
            self._episode_rejections.append(
                self._current_episode_rejections
            )
            self._episode_steps.append(
                self._current_episode_steps
            )

        self._current_episode_rejections = 0
        self._current_episode_steps = 0

        obs, info = self.env.reset(**kwargs)
        self._current_obs = obs

        for h in self._demand_history:
            h.clear()

        self.record_demand(obs)

        return obs, info

    def step(self, action: Any) -> Tuple[Any, Any, bool, bool, dict]:
        self.total_steps += 1
        self._current_episode_steps += 1
        obs_now = self._current_obs

        if obs_now is not None:
            reasons = [
                self.check_building(i, o)
                for i, o in enumerate(obs_now)
            ]
        else:
            reasons = [None] * len(action)

        fallback = self.corrective_fallback_action(
            action,
            reasons
        )

        # A rejection counts only if the gate actually changed
        # the proposed action.
        reasons = [
            r if (
                r is not None
                and not np.allclose(
                    np.asarray(a, dtype=float),
                    np.asarray(f, dtype=float)
                )
            ) else None
            for a, f, r in zip(action, fallback, reasons)
        ]

        if any(r is not None for r in reasons):
            self.rejection_count += 1
            self._current_episode_rejections += 1

            for r in reasons:
                if r is not None:
                    self.reason_counts[r] += 1

            applied_action = fallback
        else:
            applied_action = action

        result = self.env.step(applied_action)

        socs = (
            self.extract(
                obs_now,
                self._soc_idx,
                default=0.5
            )
            if obs_now is not None
            else [0.5] * len(action)
        )

        for b_idx, (prop_a, app_a, soc, reason) in enumerate(
            zip(action, applied_action, socs, reasons)
        ):
            prop_val = float(np.mean(prop_a))
            app_val = float(np.mean(app_a))

            self.auditor.log_decision(
                step=self.total_steps,
                zone_id=b_idx,
                proposed_action=prop_val,
                applied_action=app_val,
                current_soc=soc,
                reason=reason
            )

        self.last_effective_action = applied_action
        self._current_obs = result[0]
        self.record_demand(result[0])

        return result

    def rejection_rate(self) -> float:
        return self.rejection_count / max(self.total_steps, 1)

    def episode_rejection_rates(self) -> List[float]:
        rates = [
            r / s if s > 0 else 0.0
            for r, s in zip(
                self._episode_rejections,
                self._episode_steps
            )
        ]

        if self._current_episode_steps > 0:
            rates.append(
                self._current_episode_rejections
                / self._current_episode_steps
            )

        return rates


class ShieldAwareUpdateMixin:
    def update(
        self,
        observations,
        actions,
        rewards,
        next_observations,
        terminated=False,
        truncated=False
    ):
        effective = getattr(
            self.env,
            "last_effective_action",
            None
        )

        if effective is not None:
            actions = effective

        super().update(
            observations,
            actions,
            rewards,
            next_observations,
            terminated=terminated,
            truncated=truncated
        )