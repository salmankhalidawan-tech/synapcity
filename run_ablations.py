import os, sys, subprocess

SEEDS = [1, 2, 3]
CONFIGS = ["full", "no_negotiator", "no_safety_gate", "neither"]

for seed in SEEDS:
    for cfg in CONFIGS:
        env = dict(os.environ, SYNAPCITY_SEED=str(seed))
        print(f"=== seed {seed}: ablation {cfg} ===", flush=True)
        subprocess.run([sys.executable, "ablation.py", cfg], env=env, check=True)
print("All ablations done.")