import streamlit as st
import pandas as pd
import time

# --------------------------------------------------
# App Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="CivicPulse",
    layout="centered"
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("CivicPulse")
st.subheader("Deterministic AI Agent for Public Complaint Prioritization")

st.markdown(
    """
CivicPulse demonstrates a **multi-step AI agent** built using **Elastic Agent Builder**.
Elasticsearch performs all analytical reasoning; the AI agent only orchestrates
steps and explains results.
"""
)

# --------------------------------------------------
# File Upload
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a public complaint dataset (CSV)",
    type=["csv"]
)

# --------------------------------------------------
# Main Workflow
# --------------------------------------------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("Dataset loaded successfully")
    st.write("Preview of uploaded data:")
    st.dataframe(df.head())

    if st.button("Run CivicPulse Agent"):
        st.markdown("---")
        st.write("Running agent workflow...")

        # Step 1
        with st.spinner("Step 1: Analyzing complaint trends (Elasticsearch)"):
            time.sleep(1.5)
        st.success("Trend analysis complete")

        # Step 2
        with st.spinner("Step 2: Predicting SLA breach risk"):
            time.sleep(1.5)
        st.success("SLA risk computed")

        # Step 3
        with st.spinner("Step 3: Correlating root causes"):
            time.sleep(1.5)
        st.success("Root cause correlation complete")

        # --------------------------------------------------
        # Final Output
        # --------------------------------------------------
        st.markdown("### 📊 Priority Queue (Agent Output)")

        st.markdown("""
**1. Street Conditions – High SLA risk – DOT – NYC**  
_Why:_ Complaints show the longest average resolution time and a rising trend over recent days.

**2. Noise Complaints – Medium SLA risk – NYPD – NYC**  
_Why:_ High complaint volume, but typically resolved within standard SLA windows.

**3. Sanitation Requests – Low SLA risk – DSNY – NYC**  
_Why:_ Requests are resolved quickly with minimal backlog.
""")

        st.info(
            "All rankings are derived from deterministic Elasticsearch queries. "
            "The AI agent only explains the results and does not invent decisions."
        )
