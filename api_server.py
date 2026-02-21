from fastapi import FastAPI
import asyncio
import random
import json
import threading
from datetime import datetime
from app.core.orchestrator import OmegaOrchestrator
from app.agents.oracle_agent import create_oracle_agent
from crewai import Task, Crew

app = FastAPI(title="City Connect Omega: Ultra Command")
orch = OmegaOrchestrator()

# Central System Intelligence State
system_state = {
    "ai_status": "IDLE",
    "ai_report": "",
    "pending_action": None,
    "logs": ["SYSTEM: Core initialized. ML Predictive Cortex online."]
}

def log_event(event_type, details):
    """Saves a timestamped event to the local session log."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "details": details
    }
    with open("session_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.on_event("startup")
async def start_physics():
    log_event("SYSTEM_BOOT", "Physics engine and ML cortex started.")
    async def run_engine():
        while True:
            orch.run_cycle()
            await asyncio.sleep(0.5)
    asyncio.create_task(run_engine())

@app.get("/telemetry")
async def get_telemetry():
    telemetry = orch.grid.fetch_live_telemetry()
    alerts = [orch.ml_cortex.analyze_live_telemetry(n, d['telemetry']) 
              for n, d in telemetry.items() if orch.ml_cortex.analyze_live_telemetry(n, d['telemetry'])['is_anomaly']]
    return {"telemetry": telemetry, "alerts": alerts, "system": system_state}

@app.post("/trigger-random-attack")
async def random_attack():
    target = random.randint(0, orch.grid.num_nodes - 1)
    orch.grid.inject_anomaly(target, "DDoS_ATTACK")
    msg = f"ALARM: Adversarial vector detected at Node {target}"
    system_state["logs"].append(msg)
    log_event("ATTACK_INJECTED", {"target_node": target, "type": "DDoS"})
    return {"target": target}

@app.post("/process-intelligence")
async def process_ai():
    system_state["ai_status"] = "THINKING"
    def run_brain():
        oracle = create_oracle_agent()
        telemetry = orch.grid.fetch_live_telemetry()
        task = Task(description=f"Analyze: {telemetry}. Provide deep tactical brief.", 
                    expected_output="Professional tactical intelligence brief.", agent=oracle)
        result = str(Crew(agents=[oracle], tasks=[task]).kickoff())
        system_state["ai_report"] = result
        system_state["pending_action"] = "ISOLATE_AND_NEUTRALIZE"
        system_state["ai_status"] = "AWAITING_AUTHORIZATION"
        log_event("AI_ANALYSIS_COMPLETE", {"report_snippet": result[:100]})
    threading.Thread(target=run_brain).start()

@app.post("/decide/{choice}")
async def human_decision(choice: str):
    if choice == "YES":
        for n in orch.grid.graph.nodes:
            orch.grid.graph.nodes[n]['telemetry']['status'] = 'OPERATIONAL'
            orch.grid.graph.nodes[n]['telemetry']['threat_level'] = 0.0
        msg = "CMD: User APPROVED action. Grid integrity restored."
    else:
        msg = "CMD: User VETOED action. Node remains compromised."
    
    system_state["logs"].append(msg)
    log_event("HUMAN_DECISION", {"choice": choice, "result": msg})
    system_state["pending_action"] = None
    system_state["ai_status"] = "IDLE"
    system_state["ai_report"] = ""