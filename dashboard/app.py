import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from streamlit_option_menu import option_menu

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="SolarOps AI | Enterprise",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= MODERN SAAS CSS (UPDATED FOR SIZE) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Global Reset */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #e0e0e0;
    }

    /* Remove Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }

    /* Card Container (Glassmorphism) */
    .metric-card {
        background: linear-gradient(145deg, #1f2937, #111827);
        border: 1px solid #374151;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-radius: 12px;
        padding: 20px;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        border-color: #6366f1; /* Indigo hover */
        transform: translateY(-2px);
    }

    /* Typography */
    .metric-label {
        color: #9ca3af;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #f3f4f6;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 5px;
    }
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 5px;
    }
    .delta-pos { color: #10b981; }
    .delta-neg { color: #ef4444; }

    /* --- UPDATED: LARGER BUTTONS --- */
    .stButton > button {
        width: 100%;
        background: linear-gradient(to right, #4f46e5, #6366f1);
        color: white;
        border: none;
        height: 60px; /* Increased height */
        font-size: 1.1rem; /* Increased font size */
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(to right, #4338ca, #4f46e5);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        transform: scale(1.02);
    }

    /* Alert Styling */
    .custom-alert {
        padding: 1.2rem;
        border-radius: 10px;
        margin-top: 1rem;
        border-left: 6px solid;
        font-size: 1.1rem;
    }
    .alert-success { background: rgba(16, 185, 129, 0.1); border-color: #10b981; color: #d1fae5; }
    .alert-danger { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; color: #fee2e2; }
    
    /* --- UPDATED: LARGER TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px; /* Taller tabs */
        padding-top: 10px;
        padding-bottom: 10px;
        background-color: transparent;
        border-radius: 5px;
        color: #9ca3af;
        font-weight: 600;
        font-size: 1.2rem; /* Larger Text */
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f2937;
        color: #6366f1;
        border-bottom: 3px solid #6366f1; /* Thicker border */
    }
    
    /* Custom Header for AI Ops */
    .ai-header {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 10px;
        background: -webkit-linear-gradient(left, #a78bfa, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .ai-desc {
        font-size: 1.1rem;
        color: #cbd5e1;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ================= API CONNECTION =================
API_URL = "http://127.0.0.1:8000"

def call_api(endpoint, payload):
    try:
        r = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

# ================= SIDEBAR NAVIGATION =================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3106/3106807.png", width=50)
    st.markdown("### SolarOps AI")
    st.markdown("<div style='font-size: 12px; color: #6b7280; margin-bottom: 20px;'>Enterprise Edition v2.4</div>", unsafe_allow_html=True)

    selected_nav = option_menu(
        menu_title=None,
        options=["Dashboard", "Inverter Health", "Settings"],
        icons=["speedometer2", "activity", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#6366f1", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"5px", "--hover-color": "#1f2937"},
            "nav-link-selected": {"background-color": "#1f2937", "color": "white", "border-left": "3px solid #6366f1"},
        }
    )
    
    st.divider()
    
    st.markdown("#### 🎛️ Simulation Controls")
    dc_power = st.slider("DC Input (W)", 0, 15000, 5500, 100)
    ac_power = st.slider("AC Output (W)", 0, 15000, 4800, 100)
    temp = st.slider("Module Temp (°C)", -10, 80, 42)
    irradiance = st.slider("Irradiance (W/m²)", 0, 1200, 850)

# ================= HELPER FOR METRIC CARDS =================
def display_metric(col, label, value, delta=None, delta_color="normal"):
    delta_html = ""
    if delta:
        color_class = "delta-pos" if delta_color == "pos" else "delta-neg"
        arrow = "↑" if delta_color == "pos" else "↓"
        delta_html = f"<div class='metric-delta {color_class}'>{arrow} {delta}</div>"
    
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# ================= MAIN DASHBOARD VIEW =================
if selected_nav == "Dashboard":

    # --- Header ---
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("Plant Performance Overview")
        st.markdown(f"Last sync: **{datetime.now().strftime('%H:%M:%S')}** • Location: **Nevada, USA (Site 04)**")
    with c2:
        st.markdown("""
        <div style="text-align: right; padding-top: 15px;">
            <span style="background-color: rgba(16, 185, 129, 0.2); color: #10b981; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: 600;">
                ● System Online
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- KPI Row ---
    efficiency = (ac_power / dc_power * 100) if dc_power else 0
    k1, k2, k3, k4 = st.columns(4)
    eff_delta_color = "pos" if efficiency > 85 else "neg"
    
    display_metric(k1, "Inverter Efficiency", f"{efficiency:.1f}%", "1.2% vs Avg", eff_delta_color)
    display_metric(k2, "Real-time DC Power", f"{dc_power:,} W", "Stable", "pos")
    display_metric(k3, "Real-time AC Power", f"{ac_power:,} W", "Grid Sync", "pos")
    display_metric(k4, "Capacity Factor", "72.4%", "High", "pos")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Split Layout (Operations vs Analytics) ---
    col_ops, col_charts = st.columns([1, 2], gap="large")

    with col_ops:
        # --- LARGE HEADER FOR AI OPS ---
        st.markdown('<div class="ai-header">🤖 AI Operations</div>', unsafe_allow_html=True)
        
        tab_forecast, tab_maint, tab_opt = st.tabs(["Forecast", "Health", "Optimize"])

        # --- Tab 1: Forecasting ---
        with tab_forecast:
            st.markdown('<p class="ai-desc">Execute XGBoost inference model for next-hour output.</p>', unsafe_allow_html=True)
            
            if st.button("Run Prediction Model", key="btn_forecast"):
                with st.spinner("Calculating..."):
                    now = datetime.now()
                    payload = {"DC_POWER": dc_power, "hour": now.hour, "day": now.day, "month": now.month}
                    result, error = call_api("/predict-power", payload)
                    
                    if result:
                        st.markdown(f"""
                        <div class="custom-alert alert-success">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">PREDICTED OUTPUT</div>
                            <div style="font-size: 32px; font-weight: bold;">{result['prediction']:.2f} W</div>
                            <div style="font-size: 12px; margin-top: 4px;">Confidence Interval: 98.4%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"API Error: {error}")

        # --- Tab 2: Predictive Maintenance ---
        with tab_maint:
            st.markdown('<p class="ai-desc">Scan sensors using Isolation Forest algorithm.</p>', unsafe_allow_html=True)
            if st.button("Scan for Anomalies", key="btn_pdm"):
                with st.spinner("Analyzing sensor patterns..."):
                    payload = {
                        "DC_POWER": dc_power, "AC_POWER": ac_power,
                        "ac_lag_1": ac_power*0.98, "ac_lag_24": ac_power*0.85,
                        "dc_lag_1": dc_power*0.99, "dc_lag_24": dc_power*0.88,
                        "ac_roll_mean_6": ac_power*0.95, "dc_roll_mean_6": dc_power*0.95
                    }
                    result, error = call_api("/detect-anomaly", payload)
                    
                    if result:
                        alert_type = "alert-danger" if "Abnormal" in result['status'] else "alert-success"
                        icon = "⚠️" if "Abnormal" in result['status'] else "✅"
                        st.markdown(f"""
                        <div class="custom-alert {alert_type}">
                            <div style="font-weight: bold; font-size: 20px;">{icon} {result['status']}</div>
                            <div style="margin-top: 5px;">Recommendation: {result['action']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(error)

        # --- Tab 3: Optimization ---
        with tab_opt:
            st.markdown('<p class="ai-desc">Compare actual vs. theoretical yield to optimize settings.</p>', unsafe_allow_html=True)
            exp_ac = st.number_input("Target AC (W)", value=5200.0, step=100.0)
            st.markdown("<br>", unsafe_allow_html=True) # Spacer
            if st.button("Run Optimizer", key="btn_opt"):
                payload = {"AC_POWER": ac_power, "expected_ac_power": exp_ac, "DC_POWER": dc_power}
                result, error = call_api("/optimize-yield", payload)
                if result:
                     st.markdown(f"""
                        <div class="custom-alert alert-success">
                            <b>Status:</b> {result['status']}<br>
                            <b>Action:</b> {result['action']}
                        </div>
                        """, unsafe_allow_html=True)

    with col_charts:
        st.markdown("### 📈 Telemetry & Forecast")
        
        hours = [f"{i}:00" for i in range(24)]
        actual = np.concatenate([np.sort(np.random.normal(0, 100, 6)), 
                                 np.sort(np.random.normal(4000, 500, 6)), 
                                 np.sort(np.random.normal(4000, 500, 6))[::-1], 
                                 np.sort(np.random.normal(0, 100, 6))])
        actual = [max(0, x) for x in actual]
        predicted = [x * 1.05 for x in actual]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hours, y=predicted, mode='lines', name='AI Forecast',
            line=dict(width=2, color='#6366f1', dash='dash'),
            fill='tozeroy', 
            fillcolor='rgba(99, 102, 241, 0.1)' 
        ))

        fig.add_trace(go.Scatter(
            x=hours, y=actual, mode='lines+markers', name='Actual Output',
            line=dict(width=3, color='#10b981'),
            marker=dict(size=6, color='#059669', line=dict(width=1, color='white'))
        ))

        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9ca3af', family="Inter"),
            xaxis=dict(showgrid=False, linecolor='#374151'),
            yaxis=dict(showgrid=True, gridcolor='rgba(55, 65, 81, 0.3)', zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### Recent Alerts Log")
        log_df = pd.DataFrame({
            "Timestamp": ["10:42 AM", "10:30 AM", "09:15 AM"],
            "Module": ["Inverter A", "Panel Array 4", "Grid Tie"],
            "Event": ["Efficiency Drop < 2%", "Temperature Spike", "Voltage Sag"],
            "Severity": ["Low", "Medium", "High"]
        })
        
        st.dataframe(
            log_df, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Severity": st.column_config.TextColumn(
                    "Severity",
                    help="Event criticality",
                    validate="^(Low|Medium|High)$"
                )
            }
        )

# ================= OTHER PAGES =================
elif selected_nav == "Inverter Health":
    st.title("Inverter Health Diagnostics")
    st.info("Detailed oscilloscope views and vibration analysis would go here.")

elif selected_nav == "Settings":
    st.title("System Configuration")
    st.text_input("API Endpoint", value=API_URL)
    st.button("Save Configuration")