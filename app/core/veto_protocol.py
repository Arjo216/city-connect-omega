from datetime import datetime
from typing import Dict, Any

class VetoProtocol:
    def __init__(self):
        """
        The deterministic governance layer for City Connect Omega.
        Prevents Agentic AI from executing catastrophic real-world commands.
        """
        # Define strict thresholds. If an agent exceeds these, execution is frozen.
        self.MAX_AUTONOMOUS_SPEND = 5000.00
        self.CRITICAL_NODES = [0, 1] # e.g., command centers that cannot be autonomously shut down
        self.RESTRICTED_ACTIONS = ['SHUTDOWN_GRID', 'DEPLOY_COUNTERMEASURES', 'REROUTE_ALL']

    def evaluate_agent_action(self, agent_name: str, proposed_action: str, parameters: Dict[str, Any]) -> bool:
        """
        Interrogates the agent's proposed action against the safety matrix.
        Returns True if safe to auto-execute, False if it requires a Human Veto.
        """
        print(f"\n[GOVERNANCE] Analyzing proposed action from {agent_name}...")
        
        requires_veto = False
        trigger_reason = ""

        # 1. Check Financial/Resource Limits
        if parameters.get('estimated_cost', 0) > self.MAX_AUTONOMOUS_SPEND:
            requires_veto = True
            trigger_reason = f"Exceeds max autonomous spend limit (${self.MAX_AUTONOMOUS_SPEND})"

        # 2. Check Restricted Actions
        if proposed_action in self.RESTRICTED_ACTIONS:
            requires_veto = True
            trigger_reason = f"Action '{proposed_action}' is strictly restricted."

        # 3. Check Critical Infrastructure Impact
        if parameters.get('target_node') in self.CRITICAL_NODES:
            requires_veto = True
            trigger_reason = f"Interferes with Tier-1 Critical Node {parameters.get('target_node')}."

        if requires_veto:
            return self._trigger_human_override(agent_name, proposed_action, parameters, trigger_reason)
        
        print("[GOVERNANCE] Action cleared for autonomous execution.")
        return True

    def _trigger_human_override(self, agent_name: str, action: str, params: Dict, reason: str) -> bool:
        """Pauses the system thread and requests explicit terminal input."""
        print(f"\n!!! SAFE-STOP TRIGGERED !!!")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Agent: {agent_name}")
        print(f"Action: {action}")
        print(f"Parameters: {params}")
        print(f"Flagged Reason: {reason}")
        print("--------------------------------------------------")
        
        while True:
            decision = input("AUTHORIZE EXECUTION? (Y/N): ").strip().upper()
            if decision == 'Y':
                print("[GOVERNANCE] Human override confirmed. Executing...")
                return True
            elif decision == 'N':
                print("[GOVERNANCE] Veto applied. Action blocked. Instructing Swarm to hold.")
                return False
            else:
                print("Invalid input. Please enter Y or N.")

# --- Quick Lab Test ---
if __name__ == "__main__":
    governance = VetoProtocol()
    
    # Safe action (Will auto-execute)
    safe_params = {'target_node': 5, 'estimated_cost': 1200}
    governance.evaluate_agent_action("Logistics_Agent", "REROUTE_SUPPLIES", safe_params)
    
    # Dangerous action (Will trigger the prompt)
    dangerous_params = {'target_node': 0, 'estimated_cost': 8000}
    governance.evaluate_agent_action("Executive_Agent", "DEPLOY_COUNTERMEASURES", dangerous_params)