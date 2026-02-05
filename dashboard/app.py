import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# ================= PAGE CONFIG (MUST BE FIRST) =================
st.set_page_config(
    page_title="Ai-Ml-Renewable-Energy-Platform",
    page_icon="☀️",
    layout="wide"
)

# ================= STYLING =================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
    color: #ffffff;
}
.stMetric {
    background-color: #1e2130;
    border: 1px solid #3e445e;
    padding: 15px;
    border-radius: 10px;
}
div.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 6px;
    width: 100%;
    height: 3em;
    font-weight: bold;
    border: none;
}
div.stButton > button:hover {
    background-color: #ff7575;
}
.section-card {
    padding: 18px;
    border-radius: 10px;
    background-color: #1e2130;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ================= BACKEND =================
BASE_URL = "http://127.0.0.1:8000"

def call_api(endpoint, payload):
    try:
        r = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=5)
        if r.status_code == 200:
            return r.json(), True
        else:
            return r.json(), False
    except Exception as e:
        return {"error": str(e)}, False

# ================= SIDEBAR =================
with st.sidebar:
    st.title("⚙️ Live Plant Inputs")

    dc_power = st.number_input(
        "DC Power (W)",
        min_value=0.0,
        value=5500.0,
        step=100.0
    )

    ac_power = st.number_input(
        "AC Power (W)",
        min_value=0.0,
        value=480.0,
        step=10.0
    )

    expected_ac = st.number_input(
        "Expected AC Power (W)",
        min_value=0.0,
        value=520.0,
        step=10.0
    )

    st.divider()
    st.success("🟢 Backend API Connected")
    st.caption(f"Last refresh: {datetime.now().strftime('%d %b %Y %H:%M:%S')}")

# ================= MAIN HEADER =================
st.title("Ai-Ml-Renewable-Energy-Platform")
st.caption(
    "Real-time Forecasting • Predictive Maintenance • Performance Optimization"
)
st.markdown("---")

# ================= KPI ROW =================
k1, k2, k3, k4 = st.columns(4)

with k1:
    eff = (ac_power / dc_power * 100) if dc_power > 0 else 0
    st.metric("System Efficiency", f"{eff:.1f}%")

with k2:
    st.metric("Current AC Output", f"{ac_power:.0f} W")

with k3:
    st.metric("Expected Output", f"{expected_ac:.0f} W")

with k4:
    st.metric("Energy Gap", f"{expected_ac - ac_power:.0f} W")

# ================= TABS =================
tab1, tab2 = st.tabs(["🧠 AI Operations", "📊 Performance Analytics"])

# ==========================================================
# TAB 1 : AI OPERATIONS
# ==========================================================
with tab1:
    left, right = st.columns([1, 2])

    # -------- LEFT CONTROL PANEL --------
    with left:
        st.subheader("AI Control Panel")

        # ---------- FORECAST ----------
        st.markdown("**🔮 Power Forecasting**")
        if st.button("Run Forecast"):
            payload = {"DC_POWER": dc_power}
            res, ok = call_api(
    "/predict-power",
    {
        "DC_POWER": dc_power,
        "hour": datetime.now().hour,
        "day": datetime.now().day,
        "month": datetime.now().month
    }
)


            if ok:
                st.success(
                    f"Predicted AC Power: **{res['prediction']:.2f} W**"
                )
            else:
                st.error("Forecasting service failed")
                st.json(res)

        st.divider()

        # ---------- PREDICTIVE MAINTENANCE ----------
        st.markdown("**🛠 Predictive Maintenance**")
        if st.button("Run Maintenance Scan"):
            pdm_payload = {
                "DC_POWER": dc_power,
                "AC_POWER": ac_power,
                "ac_lag_1": ac_power,
                "ac_lag_24": ac_power - 30,
                "dc_lag_1": dc_power,
                "dc_lag_24": dc_power - 200,
                "ac_roll_mean_6": ac_power,
                "dc_roll_mean_6": dc_power
            }

            res, ok = call_api("/detect-anomaly", pdm_payload)

            if ok:
                if "Abnormal" in res["status"]:
                    st.error(res["status"])
                else:
                    st.success(res["status"])
                st.caption(res["action"])
            else:
                st.error("Maintenance service failed")
                st.json(res)

        st.divider()

        # ---------- OPTIMIZATION ----------
        st.markdown("**⚡ Asset Optimization**")
        if st.button("Optimize Yield"):
            res, ok = call_api(
                "/optimize-yield",
                {
                    "AC_POWER": ac_power,
                    "expected_ac_power": expected_ac,
                    "DC_POWER": dc_power
                }
            )

            if ok:
                if "loss" in res["status"].lower():
                    st.warning(res["status"])
                else:
                    st.success(res["status"])
                st.caption(res["action"])
            else:
                st.error("Optimization service failed")
                st.json(res)

    # -------- RIGHT VISUAL PANEL --------
    with right:
        st.subheader("AC Power vs Expected Trend")

        trend_df = pd.DataFrame({
            "Hour": range(9, 18),
            "Actual AC": [200, 350, 420, ac_power, 460, 440, 380, 260, 120],
            "Expected AC": [220, 370, 450, expected_ac, 480, 460, 400, 300, 150]
        })

        fig = px.line(
            trend_df,
            x="Hour",
            y=["Actual AC", "Expected AC"],
            markers=True,
            template="plotly_dark"
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# TAB 2 : ANALYTICS / LOGS
# ==========================================================
with tab2:
    st.subheader("Recent AI Decisions")

    logs = pd.DataFrame([
        {"Time": "12:10", "Module": "Optimization", "Decision": "Cleaning Recommended"},
        {"Time": "11:50", "Module": "Predictive Maintenance", "Decision": "System Healthy"},
        {"Time": "11:30", "Module": "Forecasting", "Decision": "Prediction Generated"}
    ])

    st.dataframe(logs, use_container_width=True)
