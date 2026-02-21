import streamlit as st
import pydeck as pdk
import pandas as pd
import httpx
import asyncio
import time
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

async def api_call(path, method="GET"):
    async with httpx.AsyncClient(timeout=60) as client:
        if method == "GET": return (await client.get(f"{API_URL}{path}")).json()
        return (await client.post(f"{API_URL}{path}")).json()

st.set_page_config(page_title="OMEGA STRATEGIC COMMAND", layout="wide")

# Custom Styling for the "Cyberpunk Defense" Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ City Connect Omega | Ultra Strategic Command")

# Data Synchronization
try:
    data = asyncio.run(api_call("/telemetry"))
    telemetry, alerts, system = data['telemetry'], data['alerts'], data['system']
except:
    st.error("🚨 BACKEND OFFLINE: Run `uvicorn api_server:app --reload` in a separate terminal.")
    st.stop()

# --- TOP ROW: GLOBAL METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("System Integrity", "SECURE" if not alerts else "BREACHED", delta="ACTIVE ATTACK" if alerts else None)
m2.metric("Asset Velocity", "5.0 m/s")
m3.metric("AI State", system["ai_status"])
m4.metric("Active Anomalies", len(alerts))

# --- MAIN INTERFACE ---
col_map, col_tac = st.columns([2, 1])

with col_map:
    st.subheader("🌐 3D Digital Twin | Spatial Asset Mapping")
    nodes_df = []
    for n, d in telemetry.items():
        t = d['telemetry']
        # COLOR LOGIC: Red for compromised [255, 0, 80], Cyan for safe [0, 255, 204]
        color = [255, 0, 80, 200] if t['status'] == 'COMPROMISED' else [0, 255, 204, 160]
        # We project the x,y coordinates so they appear on a 3D globe (near West Africa for map styling)
        nodes_df.append({
            "name": f"Node {n}",
            "lon": 5.0 + (t['x'] / 1000), 
            "lat": 6.5 + (t['y'] / 1000), 
            "color": color,
            "status": t['status']
        })
    
    view_state = pdk.ViewState(latitude=6.5, longitude=5.5, zoom=6, pitch=45, bearing=0)
    
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/navigation-night-v1",
        initial_view_state=view_state,
        layers=[pdk.Layer("ScatterplotLayer", pd.DataFrame(nodes_df), get_position="[lon, lat]", 
                          get_color="color", get_radius=3000, pickable=True)],
        tooltip={"text": "{name}\nStatus: {status}"}
    ))

with col_tac:
    st.subheader("🎮 Operational Command")
    if st.button("🚀 INJECT ADVERSARIAL ATTACK", use_container_width=True):
        asyncio.run(api_call("/trigger-random-attack", "POST"))
        st.rerun()

    st.divider()

    # --- HUMAN-IN-THE-LOOP INTERFACE ---
    if alerts:
        st.error(f"⚠️ ML CORTEX: {len(alerts)} Node Anomaly Detected")
        if system["ai_status"] == "IDLE":
            if st.button("🧠 ACTIVATE AGENTIC DIAGNOSIS", type="primary", use_container_width=True):
                asyncio.run(api_call("/process-intelligence", "POST"))
                st.rerun()

    if system["ai_status"] == "THINKING":
        st.info("Llama-3.3 Processing Intelligence...")
        st.spinner(); time.sleep(2); st.rerun()

    if system["ai_status"] == "AWAITING_AUTHORIZATION":
        st.success("✅ INTELLIGENCE REPORT READY")
        with st.expander("VIEW FULL SCIENTIFIC ANALYSIS", expanded=True):
            st.markdown(system["ai_report"])
        
        st.warning(f"**PROPOSED COMMAND:** {system['pending_action']}")
        
        v1, v2 = st.columns(2)
        if v1.button("✅ APPROVE (YES)", use_container_width=True):
            asyncio.run(api_call("/decide/YES", "POST"))
            st.rerun()
        if v2.button("❌ VETO (NO)", use_container_width=True):
            asyncio.run(api_call("/decide/NO", "POST"))
            st.rerun()

# --- BOTTOM ROW: DATA LAKE & ANALYTICS ---
st.divider()
tab1, tab2, tab3 = st.tabs(["📊 Telemetry Data Lake", "📈 Anomaly Distributions", "📜 Mission Logs"])

with tab1:
    df_tele = []
    for n, d in telemetry.items():
        t = d['telemetry']
        df_tele.append({"ID": n, "State": t['status'], "Latency (ms)": round(t['network_latency_ms'], 2), 
                        "Capacity (%)": round(t['resource_capacity_pct'], 1), "Threat": t['threat_level']})
    st.dataframe(pd.DataFrame(df_tele), use_container_width=True)

with tab2:
    # Scientific Plotting of the Anomaly Scores
    latencies = [d['telemetry']['network_latency_ms'] for d in telemetry.values()]
    fig = px.bar(x=list(telemetry.keys()), y=latencies, labels={'x':'Node ID', 'y':'Latency (ms)'}, 
                 title="Real-time Network Latency Profiling", color_discrete_sequence=['#00ffcc'])
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    for log in reversed(system["logs"]):
        st.text(log)