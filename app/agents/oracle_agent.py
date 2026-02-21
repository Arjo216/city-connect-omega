__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
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
# 1. DEFINE THE CUSTOM SENSORY TOOLS
# ==========================================

@tool("Fetch IoT Telemetry")
def fetch_iot_telemetry(query: str = "all") -> str:
    """
    Fetches the live telemetry data from all smart city/defense grid IoT nodes.
    The agent uses this to monitor network latency, resource capacity, and threat levels.
    """
    data = iot_grid.fetch_live_telemetry()
    return f"Live Grid Data: {data}"

# ==========================================
# 2. DEFINE THE AGENT (THE PERSONA & LOGIC)
# ==========================================

def create_oracle_agent() -> Agent:
    """Instantiates the Oracle Agent using CrewAI's native Groq integration (bypassing LangChain)."""
    
    # Initialize the Groq inference engine natively
    groq_llm = LLM(
        model="groq/llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1 # Keep it highly deterministic for strict threat analysis
    )

    return Agent(
        role="Lead Threat Intelligence Oracle",
        goal="Continuously monitor IoT network telemetry, detect adversarial anomalies (like DDoS or Power Failures), and formulate a precise diagnostic report.",
        backstory=dedent("""
            You are a highly advanced AI diagnostic node operating within the City Connect Omega defense grid. 
            Your primary objective is zero-latency threat detection. You do not panic; you analyze raw telemetry, 
            identify compromised nodes, and prepare structured intelligence for the Executive Agent to review.
        """),
        verbose=True,
        allow_delegation=False,
        tools=[fetch_iot_telemetry],
        llm=groq_llm # Bind the native Groq engine
    )

# ==========================================
# 3. DEFINE THE TASK & EXECUTION LOOP
# ==========================================

def run_oracle_diagnosis():
    oracle = create_oracle_agent()
    
    diagnostic_task = Task(
        description=dedent("""
            1. Use the 'Fetch IoT Telemetry' tool to pull the current state of the grid.
            2. Analyze the data for any nodes showing a status other than 'OPERATIONAL', high threat levels, or anomalous latency.
            3. Output a structured Threat Report detailing the compromised Node ID, the suspected anomaly, and a recommended preliminary action.
        """),
        expected_output="A structured 3-bullet point Threat Report identifying the compromised node and the anomaly type.",
        agent=oracle
    )

    diagnostic_crew = Crew(
        agents=[oracle],
        tasks=[diagnostic_task],
        process=Process.sequential,
        verbose=True
    )

    print("\n[SYSTEM] Booting City Connect Omega Oracle Agent (Powered by Native Groq)...\n")
    result = diagnostic_crew.kickoff()
    
    print("\n==============================================")
    print("FINAL ORACLE THREAT REPORT")
    print("==============================================")
    print(result)

if __name__ == "__main__":
    run_oracle_diagnosis()