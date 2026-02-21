__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from textwrap import dedent

# Import the Governance Layer and the Oracle Agent we already built
from app.core.veto_protocol import VetoProtocol
from app.agents.oracle_agent import create_oracle_agent

load_dotenv()
governance_layer = VetoProtocol()

# ==========================================
# 1. DEFINE THE EXECUTIVE'S ACTION TOOL
# ==========================================

@tool("Execute Tactical Action")
def execute_tactical_action(action_name: str, target_node: int, estimated_cost: float) -> str:
    """
    Executes a defensive or logistical action on the grid.
    You must provide the exact action_name (e.g., 'DEPLOY_COUNTERMEASURES', 'ISOLATE_NODE'), 
    the target_node (int), and the estimated_cost (float).
    """
    params = {'target_node': target_node, 'estimated_cost': estimated_cost}
    
    # This routes the AI's requested action through your Python security rules
    is_authorized = governance_layer.evaluate_agent_action("Executive_Agent", action_name, params)

    if is_authorized:
        return f"SUCCESS: Action '{action_name}' executed on Node {target_node}."
    else:
        return f"BLOCKED: Action '{action_name}' was vetoed by the Human Commander."

# ==========================================
# 2. DEFINE THE EXECUTIVE AGENT
# ==========================================

def create_executive_agent() -> Agent:
    groq_llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1
    )

    return Agent(
        role="Lead Executive Commander",
        goal="Review threat intelligence reports, formulate a defensive strategy, and execute tactical actions to secure the grid.",
        backstory=dedent("""
            You are the ultimate decision-maker for the City Connect Omega grid.
            You read reports from the Oracle Agent. If a node is under attack (like a DDoS),
            you immediately use your 'Execute Tactical Action' tool to deploy countermeasures.
            Deploying heavy countermeasures usually costs around $8,000.
        """),
        verbose=True,
        allow_delegation=False,
        tools=[execute_tactical_action],
        llm=groq_llm
    )

# ==========================================
# 3. THE MULTI-AGENT SWARM EXECUTION
# ==========================================

def run_full_incident_response():
    # Instantiate Both Agents
    oracle = create_oracle_agent()
    executive = create_executive_agent()

    # Task 1: Oracle diagnoses the grid
    diagnostic_task = Task(
        description="Use 'Fetch IoT Telemetry' to check the grid. Output a structured Threat Report identifying any compromised nodes.",
        expected_output="A Threat Report identifying the compromised Node ID and anomaly type.",
        agent=oracle
    )

    # Task 2: Executive takes action based on Task 1
    response_task = Task(
        description=dedent("""
            1. Read the Threat Report provided by the Oracle Agent.
            2. Identify the compromised Node ID.
            3. Use the 'Execute Tactical Action' tool to run the 'DEPLOY_COUNTERMEASURES' action on that specific node. Set the estimated_cost to 8000.0.
        """),
        expected_output="A final summary of the action taken and whether it was successfully executed or blocked by the human commander.",
        agent=executive,
        context=[diagnostic_task] # <-- THE MAGIC: Passes Oracle's output to the Executive
    )

    # Boot up the multi-agent system
    incident_response_crew = Crew(
        agents=[oracle, executive],
        tasks=[diagnostic_task, response_task],
        process=Process.sequential,
        verbose=True
    )

    print("\n[SYSTEM] Initiating Multi-Agent Swarm Response...\n")
    incident_response_crew.kickoff()

if __name__ == "__main__":
    run_full_incident_response()