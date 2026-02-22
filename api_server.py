__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio
import random
import json
import uuid
import chromadb
from datetime import datetime

from app.core.orchestrator import OmegaOrchestrator
from app.agents.oracle_agent import create_oracle_agent
from crewai import Task, Crew

app = FastAPI(title="City Connect Omega: Prime Command Center")
orch = OmegaOrchestrator()

# ==========================================
# 🧠 VECTOR MEMORY CORTEX (AUTO-LEARNING)
# ==========================================
try:
    chroma_client = chromadb.PersistentClient(path="./omega_memory")
    memory_collection = chroma_client.get_or_create_collection(name="threat_signatures")
    print("[SYSTEM] Vector Memory Cortex successfully linked to API API Backend.")
except Exception as e:
    print(f"[ERROR] Failed to link Vector Memory: {e}")

# ==========================================
# 🌐 CENTRAL SYSTEM STATE
# ==========================================
system_state = {
    "ai_status": "IDLE",
    "ai_report": "",
    "pending_action": None,
    "logs": ["SYSTEM: Core initialized. ML Predictive Cortex online."],
    "last_anomaly_signature": "", # Stores the exact telemetry math of the active attack
    "last_recommended_action": "" # Stores the approved countermeasure for learning
}

def log_event(event_type: str, details: dict | str):
    """Saves a timestamped scientific audit log."""
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
    log_event("ATTACK_INJECTED", {"target_node": target, "type": "DDoS_ATTACK"})
    return {"target": target}

def run_agentic_brain():
    """Background task to run the AI reasoning loop without blocking the UI."""
    try:
        oracle = create_oracle_agent()
        telemetry = orch.grid.fetch_live_telemetry()
        
        # Isolate the exact signature of the compromised node for the AI to memorize
        signature = "Unknown Anomaly"
        for node_id, data in telemetry.items():
            if data['telemetry']['status'] != 'OPERATIONAL':
                t = data['telemetry']
                signature = f"Node {node_id}: status={t['status']}, network_latency_ms={t['network_latency_ms']}, resource_capacity_pct={t['resource_capacity_pct']}, threat_level={t['threat_level']}"
                break
        
        system_state["last_anomaly_signature"] = signature

        task = Task(
            description=f"Analyze current grid telemetry: {telemetry}. Use 'Search Historical Threats' tool to find matches. Provide deep tactical brief.", 
            expected_output="Professional tactical intelligence brief including the recommended countermeasure.", 
            agent=oracle
        )
        
        result = str(Crew(agents=[oracle], tasks=[task]).kickoff())
        
        system_state["ai_report"] = result
        system_state["last_recommended_action"] = "Reroute power and isolate network perimeter." # Defaulting for learning
        system_state["pending_action"] = "ISOLATE_AND_NEUTRALIZE"
        system_state["ai_status"] = "AWAITING_AUTHORIZATION"
        log_event("AI_ANALYSIS_COMPLETE", {"report_snippet": result[:100]})
    except Exception as e:
        system_state["ai_status"] = "IDLE"
        system_state["logs"].append(f"ERROR: AI Brain failure - {str(e)}")

@app.post("/process-intelligence")
async def process_ai(background_tasks: BackgroundTasks):
    """Triggers the Agentic AI using FastAPI Background Tasks."""
    system_state["ai_status"] = "THINKING"
    system_state["logs"].append("SYSTEM: Waking Oracle Agent for RAG memory diagnosis...")
    background_tasks.add_task(run_agentic_brain)
    return {"status": "AI processing initiated"}

@app.post("/decide/{choice}")
async def human_decision(choice: str):
    if choice == "YES":
        # 1. Execute Countermeasure (Restore Grid)
        for n in orch.grid.graph.nodes:
            orch.grid.graph.nodes[n]['telemetry']['status'] = 'OPERATIONAL'
            orch.grid.graph.nodes[n]['telemetry']['threat_level'] = 0.0
        
        msg = "CMD: User APPROVED action. Grid integrity restored."
        
        # 2. AUTO-LEARNING: Burn the signature into Vector Memory
        signature = system_state.get("last_anomaly_signature", "")
        action = system_state.get("last_recommended_action", "Standard Isolation Protocol")
        
        if signature and "OPERATIONAL" not in signature:
            memory_id = f"incident_{uuid.uuid4().hex[:8]}"
            memory_collection.add(
                documents=[signature],
                metadatas=[{
                    "anomaly": "ZERO_DAY_RESOLVED", 
                    "proven_countermeasure": action
                }],
                ids=[memory_id]
            )
            learn_msg = f"🧠 AI LEARNED: Saved tactical footprint {memory_id} to Vector Database."
            system_state["logs"].append(learn_msg)
            log_event("AUTO_LEARNING_TRIGGERED", {"id": memory_id, "signature": signature})

    else:
        msg = "CMD: User VETOED action. Node remains compromised."
    
    system_state["logs"].append(msg)
    log_event("HUMAN_DECISION", {"choice": choice, "result": msg})
    
    # 3. Reset State for the next attack
    system_state["pending_action"] = None
    system_state["ai_status"] = "IDLE"
    system_state["ai_report"] = ""
    system_state["last_anomaly_signature"] = ""
    
    return {"status": "Decision processed"}