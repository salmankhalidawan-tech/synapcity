import re, random, glob
paths = glob.glob("**/compliance_audit.log", recursive=True)
print("found:", paths)
lines = open(paths[0], encoding="utf-8", errors="ignore").read().splitlines()
print("total lines:", len(lines))
print("\n--- first 5 ---"); print("\n".join(lines[:5]))
print("\n--- last 5 ---"); print("\n".join(lines[-5:]))
print("\n--- 5 random ---"); print("\n".join(random.sample(lines, min(5, len(lines)))))
gsi = [float(x) for x in re.findall(r"GSI\D{0,10}(-?\d+\.?\d*)", "\n".join(lines))]
if gsi:
    print("\nGSI count/min/max/unique:", len(gsi), min(gsi), max(gsi), len(set(gsi)))