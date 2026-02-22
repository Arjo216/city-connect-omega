__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import chromadb
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from textwrap import dedent

# Load your secure API keys from the .env file
load_dotenv()

# Import your simulated physical layer and governance layer
from app.simulation.city_grid import CityConnectGrid
from app.core.veto_protocol import VetoProtocol

# Initialize the lab environment instances
iot_grid = CityConnectGrid(num_nodes=5)
governance_layer = VetoProtocol()

# Inject a test anomaly so the Oracle has something to detect
iot_grid.inject_anomaly(target_node=2, anomaly_type="DDoS_ATTACK")

# ==========================================
# 1. INITIALIZE VECTOR MEMORY (CHROMADB)
# ==========================================
print("[SYSTEM] Booting Episodic Vector Memory Cortex...")

# PersistentClient ensures the AI remembers past runs even if you restart the server
chroma_client = chromadb.PersistentClient(path="./omega_memory")
memory_collection = chroma_client.get_or_create_collection(name="threat_signatures")

# Pre-seed the memory so the AI has "experience" to draw from on its first run
if memory_collection.count() == 0:
    print("[SYSTEM] First boot detected. Seeding Vector DB with historical defense logs...")
    memory_collection.add(
        documents=[
            "Node status COMPROMISED. High network latency > 500ms. Resource capacity dropped below 20%.",
            "Node status COMPROMISED. Zero network latency. Resource capacity at 0%."
        ],
        metadatas=[
            {"anomaly": "DDoS_ATTACK", "proven_countermeasure": "Isolate node from swarm routing and reboot firewall."},
            {"anomaly": "POWER_FAILURE", "proven_countermeasure": "Reroute power from adjacent grid and dispatch physical maintenance drone."}
        ],
        ids=["incident_alpha", "incident_beta"]
    )

# ==========================================
# 2. DEFINE THE SENSORY & COGNITIVE TOOLS
# ==========================================

@tool("Fetch IoT Telemetry")
def fetch_iot_telemetry(query: str = "all") -> str:
    """
    Fetches the live telemetry data from all smart city/defense grid IoT nodes.
    The agent uses this to monitor network latency, resource capacity, and threat levels.
    """
    data = iot_grid.fetch_live_telemetry()
    return f"Live Grid Data: {data}"

@tool("Search Historical Threats")
def search_historical_threats(anomaly_description: str) -> str:
    """
    Searches the Vector Database (Long-Term Memory) for historical telemetry signatures
    that match the current anomaly. Returns proven countermeasures if a match is found.
    """
    results = memory_collection.query(
        query_texts=[anomaly_description],
        n_results=1
    )
    
    if results and results['documents'] and results['documents'][0]:
        historical_match = results['documents'][0][0]
        metadata = results['metadatas'][0][0]
        distance = results['distances'][0][0] # Lower distance = closer semantic match
        
        return f"HISTORICAL MATCH FOUND (Semantic Distance: {round(distance, 2)}).\nPast Signature: {historical_match}\nVerified Anomaly: {metadata['anomaly']}\nRecommended Countermeasure: {metadata['proven_countermeasure']}"
            
    return "No historical matches found. This is a Zero-Day anomaly."

# ==========================================
# 3. DEFINE THE AGENT (THE PERSONA & LOGIC)
# ==========================================

def create_oracle_agent() -> Agent:
    """Instantiates the Oracle Agent using CrewAI's native Groq integration."""
    
    groq_llm = LLM(
        model="groq/llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0 # Zero temperature for absolute precision in memory retrieval
    )

    return Agent(
        role="Lead Threat Intelligence Oracle",
        goal="Monitor IoT telemetry, query the Vector Memory for historical matches, and formulate a precise, data-backed diagnostic report.",
        backstory=dedent("""
            You are a highly advanced AI diagnostic node operating within the City Connect Omega defense grid. 
            You possess Long-Term Vector Memory. You do not guess. When you spot an anomaly, you immediately 
            query your historical database to see if this attack vector has been defeated before.
        """),
        verbose=True,
        allow_delegation=False,
        tools=[fetch_iot_telemetry, search_historical_threats],
        llm=groq_llm 
    )

# ==========================================
# 4. DEFINE THE TASK & EXECUTION LOOP
# ==========================================

def run_oracle_diagnosis():
    oracle = create_oracle_agent()
    
    diagnostic_task = Task(
        description=dedent("""
            1. Use the 'Fetch IoT Telemetry' tool to pull the current state of the grid.
            2. Identify any specific node showing anomalous behavior (e.g., COMPROMISED status, high latency).
            3. Extract the exact telemetry values of the compromised node and pass them into the 'Search Historical Threats' tool.
            4. Output a structured Threat Report detailing the compromised Node ID, the suspected anomaly, and the recommended action specifically drawn from your Vector Memory.
        """),
        expected_output="A structured Threat Report identifying the node, the exact telemetry, the historical match, and the proven countermeasure.",
        agent=oracle
    )

    diagnostic_crew = Crew(
        agents=[oracle],
        tasks=[diagnostic_task],
        process=Process.sequential,
        verbose=True
    )

    print("\n[SYSTEM] Booting City Connect Omega Oracle Agent (Powered by Groq + ChromaDB)...\n")
    result = diagnostic_crew.kickoff()
    
    print("\n==============================================")
    print("FINAL ORACLE THREAT REPORT (RAG-ENHANCED)")
    print("==============================================")
    print(result)

if __name__ == "__main__":
    run_oracle_diagnosis()