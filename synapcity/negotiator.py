"""
ProspectTheoryNegotiator — dynamic, grid-stress-conditioned behavioral model.
"""
from typing import Tuple
import numpy as np

from . import config


class ProspectTheoryNegotiator:
    def __init__(self):
        self._demand_history = []

    def _grid_stress_level(self, current_demand: float) -> str:
        self._demand_history.append(current_demand)
        window = self._demand_history[-24:]
        rolling_avg = float(np.mean(window)) if window else current_demand
        rolling_avg = max(rolling_avg, 1e-6)
        ratio = current_demand / rolling_avg

        if ratio <= config.GRID_STRESS_THRESHOLDS["low"]:
            return "low"
        elif ratio <= config.GRID_STRESS_THRESHOLDS["medium"]:
            return "medium"
        return "high"

    def get_params(self, current_demand: float) -> Tuple[float, float, str]:
        level = self._grid_stress_level(current_demand)
        p = config.NEGOTIATOR_PARAMS[level]
        return p["loss_aversion_lambda"], p["risk_weighting_alpha"], level

    def acceptance_probability(self, current_demand: float, incentive_value: float,
                                perceived_discomfort: float) -> float:
        lam, alpha, _level = self.get_params(current_demand)
        subjective_gain = incentive_value ** alpha if incentive_value > 0 else 0.0
        subjective_loss = lam * (perceived_discomfort ** alpha) if perceived_discomfort > 0 else 0.0
        subjective_value = subjective_gain - subjective_loss
        return float(1.0 / (1.0 + np.exp(-subjective_value)))

    def scale_action(self, proposed_action: np.ndarray, current_demand: float,
                      incentive_value: float, perceived_discomfort: float) -> np.ndarray:
        p_accept = self.acceptance_probability(current_demand, incentive_value, perceived_discomfort)
        return np.asarray(proposed_action) * p_accept