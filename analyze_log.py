import re, collections
status, zones, reasons, cfs, fb = (collections.Counter() for _ in range(5))
gsi_hits = 0
with open("results/compliance_audit.log", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "GSI" in line.upper() or "STRESS" in line.upper():
            gsi_hits += 1
        if "| REJECTED" in line:
            status["REJECTED"] += 1
            zones[re.search(r"Zone (\d+)", line).group(1)] += 1
        elif "| APPROVED" in line:
            status["APPROVED"] += 1
        elif "Causal State:" in line:
            reasons[line.split("Causal State:")[1].strip()] += 1
        elif "Counterfactual:" in line:
            cfs[line.split("Counterfactual:")[1].strip()] += 1
        elif "Fallback Applied:" in line:
            fb[line.split("Fallback Applied:")[1].strip()] += 1
print(status); print(zones); print("GSI lines:", gsi_hits)
print(reasons.most_common(5)); print(cfs.most_common(5)); print(fb.most_common(5))