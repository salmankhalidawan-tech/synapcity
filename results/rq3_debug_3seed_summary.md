# RQ3 — SynapCity vs Baseline SAC, 3-seed debug result

Debug scale: 5 episodes x 400 steps, seeds 1/2/3, same reward, same SAC
exploration settings, same per-episode training loop. KPIs normalized so
1.0 = same as no control.

| KPI | Baseline (min-max, mean) | SynapCity (min-max, mean) |
|---|---|---|
| cost_total | 0.955-1.017, 0.989 | 0.915-0.939, 0.926 |
| carbon_emissions_total | 1.033-1.094, 1.068 | 0.965-0.974, 0.969 |
| all_time_peak_average | 1.112-1.354, 1.201 | 0.911-0.998, 0.958 |
| daily_peak_average | 1.034-1.164, 1.088 | 0.949-0.993, 0.973 |
| ramping_average | 1.207-1.382, 1.319 | 0.883-0.946, 0.914 |

No overlap between baseline and SynapCity ranges on any KPI across all 3 seeds.

Source files: results\seed1_baseline_kpis.csv, results\seed1_synapcity_kpis.csv,
results\seed2_baseline_kpis.csv, results\seed2_synapcity_kpis.csv,
results\seed3_baseline_kpis.csv, results\seed3_synapcity_kpis.csv

Caveat: debug scale only (400 steps, one stretch of the year), n=3 seeds.
Direction is trustworthy; not yet publication scale.
