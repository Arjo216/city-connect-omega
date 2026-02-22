import streamlit as st
import pydeck as pdk
import pandas as pd
import httpx
import asyncio
import time
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

async def api_call(path, method="GET"):
    """Handles asynchronous communication with the FastAPI Distributed Backend."""
    async with httpx.AsyncClient(timeout=60) as client:
        if method == "GET": return (await client.get(f"{API_URL}{path}")).json()
        return (await client.post(f"{API_URL}{path}")).json()

# ---------------------------------------------------------
# 1. PAGE CONFIG & ELITE TACTICAL CSS
# ---------------------------------------------------------
st.set_page_config(page_title="OMEGA STRATEGIC COMMAND", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Dark Cyberpunk Theme Background */
    .stApp { background-color: #0b0e14; }
    
    /* Glowing Metric Cards */
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-weight: bold; }
    [data-testid="stMetricDelta"] { color: #ff3366 !important; }
    div[data-testid="metric-container"] {
        background-color: #161a22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #00ffcc;
        box-shadow: 0px 0px 15px rgba(0, 255, 204, 0.1);
    }
    
    /* Sleek Button Styling */
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid #00ffcc;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        box-shadow: 0px 0px 20px rgba(0, 255, 204, 0.4);
        border: 1px solid #ffffff;
    }
    
    /* Section Headers */
    h1, h2, h3 { color: #e2e8f0; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ City Connect Omega | Prime Command Center")

# ---------------------------------------------------------
# 2. DATA SYNCHRONIZATION
# ---------------------------------------------------------
try:
    data = asyncio.run(api_call("/telemetry"))
    telemetry, alerts, system = data['telemetry'], data['alerts'], data['system']
except Exception as e:
    st.error("🚨 CRITICAL: Distributed Backend Offline. Run `uvicorn app.api_server:app --reload`")
    st.stop()

# ---------------------------------------------------------
# 3. GLOBAL METRICS HUD
# ---------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("System Integrity", "SECURE" if not alerts else "BREACHED", delta="ACTIVE ATTACK" if alerts else None)
m2.metric("Swarm Intelligence", "ACTIVE (ACO)")
m3.metric("AI Agent State", system["ai_status"])
m4.metric("Active Anomalies", len(alerts))

st.divider()

# ---------------------------------------------------------
# 4. MAIN TACTICAL INTERFACE
# ---------------------------------------------------------
col_map, col_tac = st.columns([2, 1])

with col_map:
    st.subheader("🌐 3D Digital Twin | Spatial Asset Mapping")
    nodes_df = []
    for n, d in telemetry.items():
        t = d['telemetry']
        # COLOR LOGIC: Crimson Red for compromised, Neon Cyan for safe
        color = [255, 51, 102, 220] if t['status'] == 'COMPROMISED' else [0, 255, 204, 180]
        
        nodes_df.append({
            "name": f"IoT Node [{n}]",
            "lon": 5.0 + (t['x'] / 1000), 
            "lat": 6.5 + (t['y'] / 1000), 
            "color": color,
            "status": t['status']
        })
    
    # 3D View Angle
    view_state = pdk.ViewState(latitude=6.5, longitude=5.5, zoom=6.5, pitch=50, bearing=15)
    
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=[pdk.Layer(
            "ScatterplotLayer", 
            pd.DataFrame(nodes_df), 
            get_position="[lon, lat]", 
            get_color="color", 
            get_radius=3500, 
            pickable=True,
            stroked=True,
            line_width_min_pixels=2
        )],
        tooltip={"text": "{name}\nStatus: {status}"}
    ))

with col_tac:
    st.subheader("🎮 Operational Command")
    
    # Attack Injection
    if st.button("🚀 INJECT ZERO-DAY ATTACK", use_container_width=True):
        asyncio.run(api_call("/trigger-random-attack", "POST"))
        st.toast("⚠️ ADVERSARIAL VECTOR INJECTED", icon="🚨")
        time.sleep(0.5)
        st.rerun()

    st.divider()

    # ---------------------------------------------------------
    # 5. HUMAN-IN-THE-LOOP (HOTL) VETO PROTOCOL
    # ---------------------------------------------------------
    if alerts:
        st.error(f"⚠️ ML CORTEX: {len(alerts)} Asset Compromised")
        
        if system["ai_status"] == "IDLE":
            if st.button("🧠 ACTIVATE Llama-3.3 ORACLE", type="primary", use_container_width=True):
                asyncio.run(api_call("/process-intelligence", "POST"))
                st.rerun()

    if system["ai_status"] == "THINKING":
        st.info("🧠 Interrogating Vector Memory Cortex...")
        st.spinner()
        time.sleep(2)
        st.rerun()

    if system["ai_status"] == "AWAITING_AUTHORIZATION":
        st.success("✅ RAG INTELLIGENCE REPORT READY")
        
        with st.expander("🔬 VIEW TACTICAL ANALYSIS", expanded=True):
            st.markdown(system["ai_report"])
        
        st.warning(f"**PROPOSED AI ACTION:** {system['pending_action']}")
        
        # --- THE POPUP APPROVAL LOGIC ---
        v1, v2 = st.columns(2)
        
        if v1.button("✅ APPROVE (YES)", use_container_width=True):
            # 1. Trigger the visual popup
            st.toast("🛡️ ACTION APPROVED: Grid Secured & Memory Learned.", icon="✅")
            st.balloons() # Adds a subtle visual confirmation layer
            # 2. Hit the API
            asyncio.run(api_call("/decide/YES", "POST"))
            # 3. Wait for human to see the popup before resetting the UI
            time.sleep(1.8)
            st.rerun()
            
        if v2.button("❌ VETO (NO)", use_container_width=True):
            # 1. Trigger the visual popup
            st.toast("🛑 ACTION VETOED: Status Quo Maintained.", icon="❌")
            # 2. Hit the API
            asyncio.run(api_call("/decide/NO", "POST"))
            # 3. Wait for human to see the popup before resetting the UI
            time.sleep(1.5)
            st.rerun()

# ---------------------------------------------------------
# 6. DATA LAKE & SCIENTIFIC ANALYTICS
# ---------------------------------------------------------
st.divider()
tab1, tab2, tab3 = st.tabs(["📊 Live Telemetry Stream", "📈 Mathematical Latency Profiling", "📜 Immutable Mission Logs"])

with tab1:
    df_tele = []
    for n, d in telemetry.items():
        t = d['telemetry']
        df_tele.append({"Node ID": n, "State": t['status'], "Latency (ms)": round(t['network_latency_ms'], 2), 
                        "Capacity (%)": round(t['resource_capacity_pct'], 1), "Threat Level": t['threat_level']})
    st.dataframe(pd.DataFrame(df_tele), use_container_width=True)

with tab2:
    latencies = [d['telemetry']['network_latency_ms'] for d in telemetry.values()]
    fig = px.area(x=list(telemetry.keys()), y=latencies, labels={'x':'Node Asset ID', 'y':'Latency (ms)'}, 
                  title="Real-time Network Kinematics", color_discrete_sequence=['#00ffcc'])
    fig.update_layout(plot_bgcolor='#0b0e14', paper_bgcolor='#0b0e14', font_color='#e2e8f0')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 📝 Core Architecture Logs")
    for log in reversed(system["logs"]):
        st.code(log, language="bash")