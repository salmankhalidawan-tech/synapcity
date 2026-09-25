"""
Reads every KPI CSV in results/ and prints a compact side-by-side comparison
of the metrics that matter most for RQ3/RQ4.
"""
import pandas as pd
import glob
import os

METRICS = ["cost_total", "carbon_emissions_total", "ramping_average",
           "daily_peak_average", "all_time_peak_average"]

files = sorted(glob.glob("results/*_kpis.csv"))
rows = {}

for f in files:
    name = os.path.basename(f).replace("_kpis.csv", "")
    df = pd.read_csv(f)
    rows[name] = {}
    for m in METRICS:
        match = df[df["cost_function"] == m]
        rows[name][m] = float(match["value"].iloc[0]) if len(match) else None

summary = pd.DataFrame(rows).T
summary = summary[METRICS]
pd.set_option("display.width", 120)
pd.set_option("display.float_format", lambda x: f"{x:.4f}")
print(summary)
summary.to_csv("results/comparison_summary.csv")
print("\nSaved to results/comparison_summary.csv")