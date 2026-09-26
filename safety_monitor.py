"""
SafetyMonitor: passive, read-only version of the Safety Gate's checks.
Counts SOC-out-of-band and demand-spike events every step, WITHOUT
correcting anything. Used in every ablation config (gate on or off) so
'no_safety_gate' and 'neither' get a real violation count to compare
against 'full' and 'no_negotiator'.
"""
from collections import Counter
import numpy as np
from . import config


class SafetyMonitor:
    def __init__(self, env):
        obs_names = env.observation_names
        self.n_buildings = len(obs_names)
        self._soc_idx = [names.index("electrical_storage_soc") if "electrical_storage_soc" in names else None
                         for names in obs_names]
        self._demand_idx = [names.index("net_electricity_consumption") if "net_electricity_consumption" in names else None
                            for names in obs_names]
        self._demand_history = [[] for _ in range(self.n_buildings)]
        self.violation_counts = Counter()
        self.total_steps = 0

    def observe(self, obs):
        self.total_steps += 1
        for b in range(self.n_buildings):
            if self._soc_idx[b] is not None:
                soc = float(obs[b][self._soc_idx[b]])
                if soc < config.STORAGE_SOC_MIN:
                    self.violation_counts["SOC_LOW"] += 1
                elif soc > config.STORAGE_SOC_MAX:
                    self.violation_counts["SOC_HIGH"] += 1
            if self._demand_idx[b] is not None:
                d = float(obs[b][self._demand_idx[b]])
                hist = self._demand_history[b][-config.DEMAND_ROLLING_WINDOW:]
                if len(hist) >= 12:
                    ref = max(hist)
                    if ref > 0.1 and d > config.MAX_DEMAND_SPIKE_MULTIPLIER * ref:
                        self.violation_counts["DEMAND_SPIKE"] += 1
                self._demand_history[b].append(d)

    def violation_rate(self):
        return sum(self.violation_counts.values()) / max(self.total_steps * self.n_buildings, 1)