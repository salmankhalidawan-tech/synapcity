# RQ4 — Ablation safety violation rate, 3-seed debug result

Debug scale: 5 episodes x 400 steps, seeds 1/2/3. SafetyMonitor counts
SOC-out-of-band and demand-spike events passively, in every config
(gate on or off), without correcting anything.

| Config | Violation rate (mean) | Seed range |
|---|---|---|
| full (gate + negotiator) | 13.8% | 12.9-15.4% |
| no_negotiator (gate only) | 17.9% | 19.1-20.1% |
| no_safety_gate (negotiator only) | 25.0% | 21.7-26.8% |
| neither (plain SAC) | 39.3% | 37.2-40.5% |

Monotonic ordering full < no_negotiator < no_safety_gate < neither, no
overlap across seeds. Gate roughly halves violations on its own
(full vs no_safety_gate, no_negotiator vs neither); Negotiator adds a
further, independent reduction (full vs no_negotiator, no_safety_gate
vs neither).

Per-seed detail (SOC_LOW / SOC_HIGH / DEMAND_SPIKE):
full seed1: 916/252/149 (13.17%) | seed2: 1058/327/155 (15.40%) | seed3: 887/245/160 (12.92%)
no_negotiator seed1: 1353/447/147 (19.47%) | seed2: 1286/470/151 (19.07%) | seed3: 1403/455/156 (20.14%)
no_safety_gate seed1: 1953/561/167 (26.81%) | seed2: 1620/395/158 (21.73%) | seed3: 1962/518/169 (26.49%)
neither seed1: 2955/931/159 (40.45%) | seed2: 2942/917/170 (40.29%) | seed3: 2776/787/161 (37.24%)

Source: results\ablation_run_log.txt (12 runs, run_ablations.py)
Caveat: debug scale only (400 steps, one stretch of the year), n=3 seeds.
