import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ==========================================
# 1. SYSTEM INITIALIZATION & STATE
# ==========================================
st.set_page_config(page_title="Unified Business Tracker", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .report-box { padding: 20px; border-radius: 10px; background: rgba(0, 150, 255, 0.1); border-left: 5px solid #0096ff; margin-bottom: 20px;}
    .stMetric { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏢 Unified Business OS")
st.write("Excel-level Data. Power BI-level Dashboards. PowerPoint-level Reporting.")

# Initialize a default business dataset if none exists in memory
if "business_data" not in st.session_state:
    st.session_state.business_data = pd.DataFrame({
        "Date": pd.date_range(start="2026-01-01", periods=5),
        "Department": ["Sales", "Marketing", "Sales", "Operations", "Marketing"],
        "Revenue": [15000, 8000, 22000, 0, 12000],
        "Expenses": [4000, 3000, 5000, 6000, 4500],
        "Status": ["Completed", "Active", "Completed", "Pending", "Active"]
    })

# ==========================================
# 2. THE 3-PILLAR TAB ARCHITECTURE
# ==========================================
tab1, tab2, tab3 = st.tabs(["📊 1. Data Engine (Excel)", "📈 2. Interactive Canvas (Power BI)", "📑 3. Exec Report (PowerPoint)"])

# ------------------------------------------
# TAB 1: THE DATA ENGINE (EXCEL REPLACEMENT)
# ------------------------------------------
with tab1:
    st.header("Data Engine")
    st.write("Add, edit, or delete rows. The math updates instantly.")
    
    # The Interactive Grid
    edited_df = st.data_editor(
        st.session_state.business_data,
        num_rows="dynamic", # Allows adding/deleting rows like Excel
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", required=True),
            "Revenue": st.column_config.NumberColumn("Revenue ($)", format="$%d"),
            "Expenses": st.column_config.NumberColumn("Expenses ($)", format="$%d"),
            "Status": st.column_config.SelectboxColumn("Status", options=["Active", "Pending", "Completed", "Cancelled"])
        }
    )
    
    # Save edits to session state instantly
    st.session_state.business_data = edited_df
    
    # The Math / Stats Engine
    st.markdown("---")
    st.subheader("Instant Statistics")
    
    # Calculate Profit automatically
    edited_df["Profit"] = edited_df["Revenue"] - edited_df["Expenses"]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${edited_df['Revenue'].sum():,.2f}")
    col2.metric("Total Expenses", f"${edited_df['Expenses'].sum():,.2f}")
    col3.metric("Net Profit", f"${edited_df['Profit'].sum():,.2f}")
    
    # Advanced Math: Profit Margin
    margin = (edited_df['Profit'].sum() / edited_df['Revenue'].sum() * 100) if edited_df['Revenue'].sum() > 0 else 0
    col4.metric("Profit Margin", f"{margin:.1f}%")

# ------------------------------------------
# TAB 2: INTERACTIVE CANVAS (POWER BI REPLACEMENT)
# ------------------------------------------
with tab2:
    st.header("Interactive Dashboard")
    st.write("Visualizations generated live from the Data Engine.")
    
    if not edited_df.empty:
        dash_col1, dash_col2 = st.columns(2)
        
        with dash_col1:
            # Chart 1: Revenue vs Expenses by Department
            dept_group = edited_df.groupby("Department")[["Revenue", "Expenses"]].sum().reset_index()
            fig1 = px.bar(dept_group, x="Department", y=["Revenue", "Expenses"], 
                          title="Financials by Department", barmode="group",
                          color_discrete_map={"Revenue": "#00ffcc", "Expenses": "#ff007f"})
            fig1.update_layout(template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)
            
        with dash_col2:
            # Chart 2: Project Status Distribution
            fig2 = px.pie(edited_df, names="Status", title="Project Status Distribution", hole=0.4)
            fig2.update_layout(template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)
            
        # Time Series Chart
        st.markdown("---")
        time_df = edited_df.groupby("Date")[["Revenue", "Profit"]].sum().reset_index()
        fig3 = px.line(time_df, x="Date", y=["Revenue", "Profit"], title="Financial Trajectory Over Time", markers=True)
        fig3.update_layout(template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Add data in the Data Engine tab to generate visualizations.")

# ------------------------------------------
# TAB 3: EXEC REPORT (POWERPOINT REPLACEMENT)
# ------------------------------------------
with tab3:
    st.header("Executive Summary")
    st.write("Dynamic presentation ready for print or PDF export. Press `Ctrl + P` (or `Cmd + P`) to save as PDF.")
    
    total_rev = edited_df['Revenue'].sum()
    total_prof = edited_df['Profit'].sum()
    best_dept = dept_group.sort_values(by="Profit", ascending=False).iloc[0]["Department"] if not dept_group.empty and "Profit" in dept_group.columns else "N/A"
    
    # Auto-Generated Narrative (Dynamic Text)
    st.markdown(f"""
    <div class="report-box">
        <h3>Month-End Business Review</h3>
        <p>The business generated <b>${total_rev:,.2f}</b> in total revenue, resulting in a net profit of <b>${total_prof:,.2f}</b>. 
        Our current profit margin stands at <b>{margin:.1f}%</b>.</p>
        <p>The highest performing sector this period was the <b>{best_dept}</b> department.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Static snapshot of the charts for the report
    rep_col1, rep_col2 = st.columns(2)
    with rep_col1:
        st.plotly_chart(fig1, use_container_width=True, key="rep_fig1")
    with rep_col2:
        st.plotly_chart(fig3, use_container_width=True, key="rep_fig3")
