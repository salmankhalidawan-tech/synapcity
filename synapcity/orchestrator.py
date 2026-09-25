"""
Orchestrator Agent — Decomposes high-level city/grid goals into zone-level subgoals.
Monitors macro-indicators (carbon intensity, pricing) to calculate a Grid Stress Index (GSI),
which can be used to dynamically adjust zone constraints or reward weights.
"""

import numpy as np


class OrchestratorAgent:
    def __init__(self, high_level_goal="minimize_carbon_and_cost"):
        from . import config

        self.high_level_goal = high_level_goal
        self.baseline_carbon = config.GRID_STRESS_BASELINE_CARBON
        self.baseline_price = config.GRID_STRESS_BASELINE_PRICE

    def calculate_grid_stress(self, current_carbon, current_price):
        """
        Calculates a normalized Grid Stress Index (GSI)
        from 0.0 (calm) to 1.0+ (critical).
        """
        carbon_factor = max(
            0,
            current_carbon / self.baseline_carbon
        )

        price_factor = max(
            0,
            current_price / self.baseline_price
        )

        # Simple weighted average for macro stress
        gsi = (0.6 * carbon_factor) + (0.4 * price_factor)

        return gsi

    def decompose_subgoals(self, observations, carbon_idx, price_idx):
        """
        Reads the macro state from the shared observation and
        generates zone-level subgoals.

        Returns a dictionary of dynamic constraints/targets
        for the Zone Agents.
        """

        # Extract macro variables from the first building's
        # observation (shared grid state)
        if not observations or len(observations) == 0:
            return {
                "gsi": 0.0,
                "mode": "normal"
            }

        try:
            current_carbon = (
                float(observations[0][carbon_idx])
                if carbon_idx is not None
                else self.baseline_carbon
            )

            current_price = (
                float(observations[0][price_idx])
                if price_idx is not None
                else self.baseline_price
            )

        except (IndexError, TypeError):
            current_carbon = self.baseline_carbon
            current_price = self.baseline_price

        gsi = self.calculate_grid_stress(
            current_carbon,
            current_price
        )

        # Decompose into zone-level operating modes
        if gsi > 1.5:
            mode = "crisis_conservation"
            # High stress: prioritize discharging,
            # relax lower SOC bounds

        elif gsi < 0.5:
            mode = "aggressive_storage"
            # Low stress/cheap energy: prioritize charging

        else:
            mode = "balanced_operation"

        return {
            "grid_stress_index": gsi,
            "operating_mode": mode,
            "target_carbon": current_carbon,
            "target_price": current_price
        }


# Example usage
if __name__ == "__main__":
    orchestrator = OrchestratorAgent()

    # Mock observation: high carbon, high price
    mock_subgoals = orchestrator.decompose_subgoals(
        [[0.9, 0.8]],
        carbon_idx=0,
        price_idx=1
    )

    print(f"Issued Subgoals: {mock_subgoals}")