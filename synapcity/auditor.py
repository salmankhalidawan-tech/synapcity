import logging
import os

REASON_TEXT = {
    "SOC_LOW": ("Battery SOC is below the safe minimum.",
                "Continuing to discharge risks an empty battery and forced grid import."),
    "SOC_HIGH": ("Battery SOC is above the safe maximum.",
                 "Continuing to charge risks overcharge and battery degradation."),
    "DEMAND_SPIKE": ("Building demand exceeded the allowed multiple of its recent average.",
                     "Charging now would add to a demand spike and raise peak-demand cost."),
}


class ComplianceAuditorAgent:
    """Rule-based audit log: records every gate rejection with the gate's real
    reason, the measured SOC, and a plain-language justification."""

    def __init__(self, log_dir="results", log_name="compliance_audit.log"):
        os.makedirs(log_dir, exist_ok=True)
        self.filepath = os.path.join(log_dir, log_name)
        self.approved_count = 0
        self.rejected_count = 0

        self.logger = logging.getLogger("ComplianceAuditor")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            fh = logging.FileHandler(self.filepath, mode="w")   # fresh log every run
            fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
            self.logger.addHandler(fh)

    def log_decision(self, step, zone_id, proposed_action, applied_action, current_soc, reason=None):
        if reason is None:
            self.approved_count += 1   # approvals are counted, not written
            return
        self.rejected_count += 1
        why, consequence = REASON_TEXT.get(reason, (reason, ""))
        self.logger.warning(
            f"Step {step} | Zone {zone_id} | REJECTED [{reason}] | SOC {current_soc:.3f} | "
            f"Proposed {proposed_action:.3f} -> Applied {applied_action:.3f} | {why} {consequence}"
        )