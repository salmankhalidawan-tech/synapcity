"""
Federated Coordinator Agent — Shares learned policy parameters and safety 
shield edge-cases across zones/cities to build 'herd immunity' against grid anomalies.
"""
import os
import json

class FederatedCoordinatorAgent:
    def __init__(self, sync_dir="results/federation"):
        self.sync_dir = sync_dir
        os.makedirs(self.sync_dir, exist_ok=True)
        self.global_shield_ledger = []
        self.ledger_path = os.path.join(self.sync_dir, "shield_ledger.json")

    def broadcast_shield_updates(self, zone_id, episode, safety_gate):
        """
        Extracts rejection metrics from the local Safety Gate and broadcasts 
        them to the federated ledger.
        """
        # Extract the latest episode's rejection data
        if safety_gate._episode_rejections:
            latest_rejections = safety_gate._episode_rejections[-1]
            latest_steps = safety_gate._episode_steps[-1]
        else:
            latest_rejections = safety_gate._current_episode_rejections
            latest_steps = safety_gate._current_episode_steps

        update_payload = {
            "zone_id": zone_id,
            "episode": episode,
            "unsafe_states_encountered": latest_rejections,
            "total_steps": latest_steps,
            "rejection_rate": round(latest_rejections / max(latest_steps, 1), 4)
        }
        
        self.global_shield_ledger.append(update_payload)
        
        with open(self.ledger_path, "w") as f:
            json.dump(self.global_shield_ledger, f, indent=4)
            
        print(f"[Federated Coordinator] Zone {zone_id} broadcasted {latest_rejections} unsafe state events to the global ledger.")

# Example usage
if __name__ == "__main__":
    # Mocking a safety gate for standalone testing
    class MockGate:
        def __init__(self):
            self._episode_rejections = [45]
            self._episode_steps = [400]
    
    coordinator = FederatedCoordinatorAgent()
    coordinator.broadcast_shield_updates("Zone_1", 1, MockGate())