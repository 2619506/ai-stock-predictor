import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 1. INITIALIZATION & NEON UI STYLING
# ==========================================
st.set_page_config(page_title="NeonVest - Learn to Invest", page_icon="✨", layout="wide")

# Injecting Custom CSS for Glassmorphism, Neon Gradients, and Tooltips
st.markdown("""
    <style>
    /* Neon Dark Background */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); 
        color: #e2e8f0; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }
    
    /* Hide Streamlit Branding for a cleaner look */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; 
        padding: 24px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Custom Hover Tooltip Engine */
    .hover-tooltip {
        position: relative; 
        display: inline-block;
        border-bottom: 2px dotted #22d3ee; 
        color: #22d3ee; 
        cursor: help; 
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .hover-tooltip .tooltiptext {
        visibility: hidden; 
        width: 240px; 
        background-color: rgba(15, 23, 42, 0.95);
        color: #fff; 
        text-align: center; 
        border-radius: 8px; 
        padding: 12px;
        position: absolute; 
        z-index: 50; 
        bottom: 130%; 
        left: 50%;
        margin-left: -120px; 
        opacity: 0; 
        transition: opacity 0.3s;
        border: 1px solid #334155; 
        font-size: 0.9rem; 
        font-weight: normal; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .hover-tooltip:hover .tooltiptext { 
        visibility: visible; 
        opacity: 1; 
    }
    .hover-tooltip:hover {
        color: #67e8f9;
    }
    
    /* Transparent AI Insight Box */
    .ai-insight {
        background: rgba(147, 51, 234, 0.15); 
        border-left: 4px solid #c084fc;
        padding: 16px; 
        border-radius: 0 8px 8px 0; 
        margin-top: 15px;
    }
    
    /* Tiny Data Credit */
    .data-credit { 
        text-align: right; 
        font-size: 10px; 
        color: rgba(255,255,255,0.4); 
        margin-top: -10px; 
        margin-bottom: 20px;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #cbd5e1;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(34, 211, 238, 0.1);
        color: #22d3ee !important;
        border-bottom: 2px solid #22d3ee;
    }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("<h1 style='color: #22d3ee; display: flex; align-items: center; gap: 10px;'>✨ NeonVest <span style='font-size: 1.2rem; color: #cbd5e1; font-weight: normal;'>| The friendly way to learn stocks</span></h1>", unsafe_allow_html=True)
st.write("Welcome to your personal, beginner-friendly gateway to the stock market.")

# ==========================================
# 2. SIDEBAR CONFIGURATION
# ==========================================
st.sidebar.markdown("### 🔍 Find a Company")
ticker_input = st.sidebar.text_input("Type a ticker (e.g., AAPL, TSLA)", "AAPL").upper().strip()
st.sidebar.caption("💡 Not sure what to type? Try **MSFT** for Microsoft or **AMZN** for Amazon.")

@st.cache_data(ttl=3600)
def fetch_basic_data(ticker):
    """Fetches exactly 90 days of data to keep charts clean and digestible for beginners."""
    end = datetime.today()
    start = end - timedelta(days=90)
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if not df.empty:
            df.reset_index(inplace=True)
            # Flatten multi-index columns if they exist (yfinance quirk)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
        return df
    except Exception:
        return pd.DataFrame()

with st.spinner("Fetching data in a beginner-friendly way..."):
    df = fetch_basic_data(ticker_input)

if df.empty or 'Close' not in df.columns:
    st.error(f"Oops! We couldn't find data for '{ticker_input}'. Try typing 'AAPL' instead.")
    st.stop()

# Extract simple metrics
try:
    current_price = float(df['Close'].iloc[-1])
    start_price = float(df['Close'].iloc[0])
    is_healthy = current_price > start_price
except Exception:
    current_price, start_price, is_healthy = 0.0, 0.0, True

# ==========================================
# 3. BEGINNER-FRIENDLY TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🍕 Learn", "📈 Simple Charts", "🧠 AI Explanations"])

# ------------------------------------------
# TAB 1: LEARN (Analogies & Tooltips)
# ------------------------------------------
with tab1:
    st.markdown("""
    <div class="glass-card">
        <h2 style='margin-top:0; color: #f8fafc;'>What exactly is a Stock?</h2>
        <p style='font-size: 1.1rem; line-height: 1.7; color: #cbd5e1;'>
            Imagine a massive, highly successful pizza shop. The owners want to open 10 more shops across the country, but they need money to do it. <br><br>
            So, they divide the company into millions of tiny "slices" and sell them to people like you. 
            When you buy a stock, you literally own a <span class="hover-tooltip">Share<span class="tooltiptext">A single piece of ownership in a company. You are part-owner!</span></span> of that business. 
            If the company sells lots of pizza and becomes more popular, your slice becomes more valuable. If you want, you can sell your slice to someone else later for a profit!
        </p>
    </div>
    
    <div class="glass-card">
        <h2 style='margin-top:0; color: #f8fafc;'>Hover to Learn: Market Vocabulary</h2>
        <ul style='color: #cbd5e1;'>
            <li style='margin-bottom: 15px; font-size: 1.1rem;'>
                <span class="hover-tooltip">Volatility<span class="tooltiptext">How 'jumpy' a stock price is. Think of it like a wild roller coaster vs. a calm, steady train.</span></span>: 
                Some stocks jump up and down a lot every day. Others move very slowly.
            </li>
            <li style='margin-bottom: 15px; font-size: 1.1rem;'>
                <span class="hover-tooltip">Dividend<span class="tooltiptext">A cash 'thank you' gift the company deposits directly into your account just for holding their stock.</span></span>: 
                Some mature companies pay you a little bit of cash every few months just to say thank you for being an owner.
            </li>
            <li style='margin-bottom: 15px; font-size: 1.1rem;'>
                <span class="hover-tooltip">Volume<span class="tooltiptext">The number of shares traded in a single day. High volume means lots of people are interested today!</span></span>: 
                How many people are buying and selling slices of the pizza today.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: SIMPLE CHARTS
# ------------------------------------------
with tab2:
    st.markdown(f"<h3 style='color: #f8fafc;'>Let's look at {ticker_input} over the last 90 days</h3>", unsafe_allow_html=True)
    st.write("We kept this chart simple. No confusing numbers or overwhelming grids, just the general direction of the company so you can see how it is feeling.")
    
    view_mode = st.radio("Choose your visual style:", ["Simple Line (Beginner)", "Candlestick (Advanced)"], horizontal=True)
    
    fig = go.Figure()
    
    if "Simple Line" in view_mode:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'], 
            mode='lines', 
            line=dict(color='#22d3ee', width=4), 
            name='Price',
            fill='tozeroy',
            fillcolor='rgba(34, 211, 238, 0.1)'
        ))
        # Hide complex axes for beginners
        fig.update_layout(xaxis=dict(showgrid=False, showticklabels=True), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
    else:
        fig.add_trace(go.Candlestick(
            x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
            name='Price',
            increasing_line_color='#4ade80', decreasing_line_color='#f472b6'
        ))
        st.info("💡 **Candlestick Tip:** A green block means the price went up that day. A pink block means it went down. The thin lines sticking out (wicks) show the highest and lowest points the price reached during that day.")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        height=400, # Compact height so it isn't overwhelming
        margin=dict(l=0, r=0, t=20, b=0),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='data-credit'>Verified Market Data provided by: Yahoo Finance API</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: TRANSPARENT AI EXPLANATION
# ------------------------------------------
with tab3:
    st.markdown(f"<h3 style='color: #f8fafc;'>How is {ticker_input} doing right now?</h3>", unsafe_allow_html=True)
    
    status = "Growing smoothly! 📈" if is_healthy else "Taking a breather 📉"
    color = "#4ade80" if is_healthy else "#f472b6"
    trend_word = "higher" if is_healthy else "lower"
    action_word = "more people are buying than selling" if is_healthy else "some people are taking a break and selling their slices"
    
    st.markdown(f"""
    <div class="glass-card">
        <h2 style='color: {color}; margin-top:0;'>Current Vibe: {status}</h2>
        <p style='font-size: 1.2rem; color: #cbd5e1;'>The current price of one share (slice) is <b>${current_price:.2f}</b>.</p>
        
        <div class="ai-insight">
            <h4 style='color: #c084fc; margin-top:0; display: flex; align-items: center; gap: 8px;'>
                🧠 Transparent AI Insight
            </h4>
            <p style='margin-bottom: 10px; color: #e2e8f0;'>I don't use magic or confusing math. Here is exactly how I looked at {ticker_input} today, step-by-step:</p>
            <ul style='margin-bottom: 0; color: #e2e8f0; line-height: 1.8;'>
                <li><b>Step 1:</b> I looked at what the price was 90 days ago, which was <b>${start_price:.2f}</b>.</li>
                <li><b>Step 2:</b> I compared that past price to today's current price of <b>${current_price:.2f}</b>.</li>
                <li><b>Step 3:</b> Because today's price is {trend_word} than it was 3 months ago, the general trend tells us that {action_word}.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='data-credit'>Calculations processed safely and locally based on Yahoo Finance historical pricing.</div>", unsafe_allow_html=True)
