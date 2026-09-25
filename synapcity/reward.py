"""
SynapCityRewardFunction: the single shared reward used by the Zone Agent.
Storage health is penalized softly BEFORE the hard safety bounds, so the agent
learns to stay away from empty/full instead of relying on the Safety Gate.
"""
from typing import Any, List, Mapping, Union

from citylearn.reward_function import RewardFunction

from . import config


class SynapCityRewardFunction(RewardFunction):
    SOFT_MARGIN = 0.15   # start penalizing this far inside the hard bounds

    def __init__(self, env_metadata: Mapping[str, Any], **kwargs):
        super().__init__(env_metadata, **kwargs)

    def _storage_health_score(self, soc: float) -> float:
        safe_lo = config.STORAGE_SOC_MIN + self.SOFT_MARGIN   # 0.20 with bounds 0.05/0.95
        safe_hi = config.STORAGE_SOC_MAX - self.SOFT_MARGIN   # 0.80
        if soc < safe_lo:
            return max(0.0, soc / safe_lo)
        if soc > safe_hi:
            return max(0.0, (1.0 - soc) / (1.0 - safe_hi))
        return 1.0

    def calculate(self, observations: List[Mapping[str, Union[int, float]]]) -> List[float]:
        rewards = []
        for o in observations:
            net_demand = float(o.get("net_electricity_consumption", 0.0))
            price = float(o.get("electricity_pricing", 0.0))
            cost = net_demand * price

            soc = float(o.get("electrical_storage_soc", 0.5))
            storage_health = self._storage_health_score(soc)

            peak_penalty = max(net_demand, 0.0)

            r = (
                config.W_COST * (-cost)
                + config.W_PEAK * (-peak_penalty)
                + config.W_STORAGE_HEALTH * storage_health
            )
            rewards.append(r)

        if self.central_agent:
            return [sum(rewards)]
        return rewards