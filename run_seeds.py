import os, sys, shutil, subprocess

SEEDS = [1, 2, 3]
RUNS = [("train_baseline.py", "baseline_kpis.csv"),
        ("train_synapcity.py", "synapcity_kpis.csv")]

for seed in SEEDS:
    for script, out in RUNS:
        env = dict(os.environ, SYNAPCITY_SEED=str(seed))
        print(f"=== seed {seed}: {script} ===", flush=True)
        subprocess.run([sys.executable, script], env=env, check=True)
        shutil.copy(os.path.join("results", out), os.path.join("results", f"seed{seed}_{out}"))
print("All seeds done.")