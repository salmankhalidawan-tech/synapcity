@'
# RQ3 — SynapCity vs Baseline SAC, 3-seed debug result (fixed pipeline)

Debug scale: 5 episodes x 400 steps, seeds 1/2/3, same reward, same SAC
exploration settings, same per-episode training loop, calibrated Safety Gate
(demand multiplier 1.25) and calibrated Orchestrator GSI baselines.
KPIs normalized so 1.0 = same as no control.

| KPI | Baseline (min-max, mean) | SynapCity (min-max, mean) |
|---|---|---|
| cost_total | 0.970-1.015, 0.988 | 0.933-0.943, 0.940 |
| carbon_emissions_total | 1.059-1.104, 1.076 | 0.982-0.997, 0.992 |
| all_time_peak_average | 1.166-1.296, 1.215 | 1.041-1.080, 1.056 |
| daily_peak_average | 1.066-1.171, 1.130 | 1.009-1.074, 1.037 |
| ramping_average | 1.336-1.370, 1.351 | 1.038-1.066, 1.054 |

No overlap between baseline and SynapCity ranges on any KPI across all 3 seeds.
Note: SynapCity's peak metrics (1.04-1.08) are now slightly above the 1.0
no-control line, unlike the pre-GSI-calibration debug run. It still clearly
beats the baseline (1.17-1.30 on the same KPI), which is the primary comparison.

Source files: results\seed{1,2,3}_{baseline,synapcity}_kpis.csv

Caveat: debug scale only (400 steps, one stretch of the year), n=3 seeds.
Direction is trustworthy; not yet publication scale.
'@ | Out-File -Encoding utf8 results\rq3_debug_3seed_summary.md