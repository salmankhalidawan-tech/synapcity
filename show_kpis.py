import sys, pandas as pd
df = pd.read_csv(sys.argv[1])
keep = ["cost_total", "carbon_emissions_total", "all_time_peak_average",
        "daily_peak_average", "ramping_average", "electricity_consumption_total"]
d = df[df["cost_function"].isin(keep) & (df["level"] == "district")]
print(d[["cost_function", "value"]].to_string(index=False))