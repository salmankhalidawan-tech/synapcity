# SynapCity — Minimum Viable Build (MVB)

Starter codebase for the 3-agent MVB defined in the SynapCity research proposal:
**Zone Agent (CityLearn SAC) + Digital Twin Sandbox (safety gate) + Negotiator Agent (Prospect-Theory heuristic)**.

## 1. Setup

This project depends on `citylearn`, which pulls in `torch` and other heavy packages.
Installing from scratch can take a long time if pip has to *build* packages (e.g. scikit-learn)
from source instead of using prebuilt wheels. Recommended environments where this installs cleanly
and fast, using free compute (per the project's no-budget constraint):

- **Google Colab** (free tier) — recommended, prebuilt wheels available, no local setup needed.
- **Kaggle Notebooks** (free GPU/CPU hours).
- Local machine with Python 3.9–3.12.

```bash
pip install -r requirements.txt
```

## 2. Find an available dataset

CityLearn ships several pre-built datasets. Run this first to see what's available in your
installed version, and pick one (the code defaults to the first CityLearn Challenge dataset found):

```bash
python -c "from citylearn.data import DataSet; print(DataSet().get_names())"
```

Set your chosen dataset name in `synapcity/config.py` -> `DATASET_NAME`.

## 3. Project structure

```
synapcity/
  config.py       # reward weights, safety bounds, negotiator heuristic table — all in one place
  reward.py        # SynapCityRewardFunction — the shared weighted reward (Section 6 of proposal)
  safety_gate.py    # SafetyGateWrapper — the discrete pre-execution "test -> approve/reject" gate
  negotiator.py     # ProspectTheoryNegotiator — dynamic loss-aversion/risk heuristic by grid-stress level
train_baseline.py   # Trains a plain SAC agent, NO safety gate, NO negotiator — this is your baseline/RQ3 comparison
train_synapcity.py  # Trains SAC wrapped with the Safety Gate + Negotiator — this is the MVB
ablation.py          # Runs the 4 configurations needed for RQ4 (full / no-negotiator / no-gate / neither)
```

## 4. Run order

1. `python train_baseline.py` — establishes your comparison point (RQ3).
2. `python train_synapcity.py` — trains the full MVB.
3. `python ablation.py` — produces the with/without comparisons for RQ4.

Each script saves episode-level KPIs (cost, peak demand, comfort, safety-gate rejection count)
to `results/` as CSV so you can plot them directly for the paper.

## 5. What's already decided vs. what you still need to tune

Already fixed (from the proposal, Section 6):
- Reward weights start equal (w1 = w2 = w3 = 1/3) — documented in `config.py`, change and log any retuning.
- Safety bounds default to a simple indoor-temperature comfort band; adjust to match your chosen
  building's actual comfort range once you inspect the dataset.
- Negotiator's grid-stress thresholds (low/medium/high) are placeholders — recalibrate them to the
  actual demand distribution of your chosen dataset before training (see the note in `config.py`).

## 6. Honesty note for your write-up

This code was scaffolded and its API verified directly against the installed `citylearn==3.0.2`
package source. Full multi-episode training was not run end-to-end before hand-off — run the
scripts yourself, inspect the first few printed timesteps for sanity, and adjust `config.py`
bounds/weights to your specific dataset before trusting any results.
