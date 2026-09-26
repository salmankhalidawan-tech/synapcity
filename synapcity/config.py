"""
SynapCity MVB — central configuration.
"""
import os
# ---------------------------------------------------------------------------
# 0. Dataset
# ---------------------------------------------------------------------------
DATASET_NAME = "citylearn_challenge_2022_phase_1"

# ---------------------------------------------------------------------------
# 1. Shared reward weights  (Section 6, R_total formula)
# ---------------------------------------------------------------------------
W_COST = 1.0 / 3.0
W_PEAK = 1.0 / 3.0
W_STORAGE_HEALTH = 1.0 / 3.0

# ---------------------------------------------------------------------------
# 2. Safety Gate bounds  (the Digital Twin Sandbox's hard constraints)
# ---------------------------------------------------------------------------
STORAGE_SOC_MIN = 0.05
STORAGE_SOC_MAX = 0.95

MAX_DEMAND_SPIKE_MULTIPLIER = 1.25
DEMAND_ROLLING_WINDOW = 24

# Lightweight analytical surrogate used by the Safety Gate instead of a full
# environment clone: assumes an action of magnitude 1.0 can shift SOC by up
# to this much in one step. Conservative placeholder -- recalibrate once you
# can compare a few predicted vs. actual SOC deltas from a real run.
ASSUMED_MAX_SOC_DELTA_PER_STEP = 0.41

# ---------------------------------------------------------------------------
# 3. Negotiator Agent — dynamic Prospect Theory parameterization
# ---------------------------------------------------------------------------
GRID_STRESS_THRESHOLDS = {
    "low": 1.05,
    "medium": 1.25,
}

NEGOTIATOR_PARAMS = {
    "low":    {"loss_aversion_lambda": 1.5, "risk_weighting_alpha": 0.7},
    "medium": {"loss_aversion_lambda": 2.0, "risk_weighting_alpha": 0.8},
    "high":   {"loss_aversion_lambda": 2.5, "risk_weighting_alpha": 0.9},
}
# SAC exploration schedule -- explicitly overridden because CityLearn's
# default (based on a single episode's length) does not account for
# multi-episode training: its internal step counter never resets between
# episodes, so with the library default, exploration silently "ends" only
# once across the whole run, right at episode 1's boundary -- too late for
# normalization statistics to be reliably ready before episode 2 starts.
# Fixed, small values here guarantee exploration completes safely inside
# episode 1 regardless of DEBUG_MODE or real (full-year) episode length.
SAC_END_EXPLORATION_TIME_STEP = 310
SAC_STANDARDIZE_START_TIME_STEP = 260

GRID_STRESS_BASELINE_CARBON = 0.154   # full-year median (8760-step no-control calibration)  # debug-scale median carbon_intensity; recheck at full year
GRID_STRESS_BASELINE_PRICE = 0.220    # debug-scale median electricity_pricing; recheck at full year
# ---------------------------------------------------------------------------
# 4. Training
# ---------------------------------------------------------------------------
EPISODES = 10
RANDOM_SEED = int(os.environ.get("SYNAPCITY_SEED", "42"))
RESULTS_DIR = "results"

# ---------------------------------------------------------------------------
# 5. Debug mode
# ---------------------------------------------------------------------------
# When True, caps each episode at a small number of timesteps instead of the
# full dataset (often a full year / 8760 hourly steps) so you can verify a
# script runs end-to-end in under a minute. Flip to False for real runs.
DEBUG_MODE = False
DEBUG_SIMULATION_END_TIME_STEP = 400