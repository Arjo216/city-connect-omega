import time
from app.simulation.city_grid import CityConnectGrid
from app.agents.oracle_agent import run_oracle_diagnosis, create_oracle_agent
from app.agents.executive_agent import create_executive_agent
from app.swarm.aco_router import SwarmRouter
from crewai import Task, Crew, Process
from textwrap import dedent

def boot_city_connect_omega():
    print("==================================================")
    print("🚀 INITIALIZING CITY CONNECT OMEGA MASTER CONTROL")
    print("==================================================")
    
    # 1. Boot up the physical IoT grid
    grid_env = CityConnectGrid(num_nodes=5)
    print("[SYSTEM] IoT Grid Online. 5 Critical Nodes Connected.")
    time.sleep(1)

    # 2. Simulate standard operations
    print("[SYSTEM] Monitoring grid telemetry...")
    time.sleep(2)
    
    # 3. ADVERSARIAL INJECTION (The Event Trigger)
    print("\n[ALERT] Adversarial interference detected on the physical layer!")
    grid_env.inject_anomaly(target_node=2, anomaly_type="DDoS_ATTACK")
    time.sleep(1)

    # 4. WAKING THE AI BRAIN
    print("\n[SYSTEM] Anomaly threshold breached. Waking Agentic AI Swarm...")
    oracle = create_oracle_agent()
    executive = create_executive_agent()

    diagnostic_task = Task(
        description="Use 'Fetch IoT Telemetry' to check the grid. Output a structured Threat Report identifying any compromised nodes.",
        expected_output="A Threat Report identifying the compromised Node ID and anomaly type.",
        agent=oracle
    )

    response_task = Task(
        description=dedent("""
            1. Read the Threat Report provided by the Oracle Agent.
            2. Identify the compromised Node ID.
            3. Use the 'Execute Tactical Action' tool to run 'DEPLOY_COUNTERMEASURES' on that node. Set estimated_cost to 8000.0.
        """),
        expected_output="Summary of action taken and authorization status.",
        agent=executive,
        context=[diagnostic_task]
    )

    incident_response_crew = Crew(
        agents=[oracle, executive],
        tasks=[diagnostic_task, response_task],
        process=Process.sequential,
        verbose=False # Turning off verbose so we just see the final system output
    )
    
    # Execute the AI thought process (This will trigger your Veto Protocol!)
    incident_response_crew.kickoff()

    # 5. ENGAGING THE PHYSICAL SWARM
    print("\n[SYSTEM] AI decision loop complete. Engaging Swarm Logistics to reroute critical data/supplies...")
    router = SwarmRouter(graph=grid_env.graph)
    
    # We need to send supplies from Command Node 0 to Outpost Node 4, bypassing the attack.
    optimal_path = router.optimize_route(start_node=0, target_node=4)
    
    print("\n==================================================")
    print("🟢 INCIDENT RESOLVED: CITY CONNECT OMEGA SECURE")
    print("==================================================")
    print(f"Final Swarm Reroute Execution: {optimal_path}")

if __name__ == "__main__":
    boot_city_connect_omega()