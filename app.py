import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

# Load local environment variables (if running locally)
load_dotenv()

# Securely grab API keys from Streamlit/Environment
TIINGO_API_KEY = os.environ.get("TIINGO_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="AI Quant Workstation", page_icon="📈", layout="wide")

# Custom CSS to align with your webpage's dark cyberpunk aesthetic
st.markdown("""
    <style>
    .reportview-container { background: #12121e; }
    .stMetric { background: rgba(26, 26, 46, 0.6); padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 255, 204, 0.2); }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Next-Gen AI Quant Workstation")

# 1. Validation Check
if not TIINGO_API_KEY or not GEMINI_API_KEY:
    st.error("⚠️ **API Keys Missing!**")
    st.write("Please ensure `TIINGO_API_KEY` and `GEMINI_API_KEY` are securely added to your Streamlit Cloud Secrets.")
    st.stop()

# Helper: Pure Pandas RSI Calculation
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

# Helper: Fetch Tiingo Data
@st.cache_data(ttl=3600)
def fetch_tiingo_data(symbol, days):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Token {TIINGO_API_KEY}'}
    start_date = (datetime.today() - timedelta(days=days)).strftime('%Y-%m-%d')
    url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data: return pd.DataFrame()
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            df.set_index('date', inplace=True)
            return df
    except:
        return pd.DataFrame()
    return pd.DataFrame()

# --- SIDEBAR CONFIGURATION & MULTI-YEAR UPGRADE ---
st.sidebar.header("🛸 Control Matrix")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()

# Multi-Year Slider implementation (scales from 1 to 5 years)
years_back = st.sidebar.slider("Historical Window (Years)", min_value=1, max_value=5, value=1)
days_back = years_back * 365

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Core Add-ons")
ai_tool = st.sidebar.selectbox(
    "Select Active Neural Module",
    ["📊 Quant Signal Analyzer", "🧠 Sentiment Catalyst Simulator", "🔮 Macro Scenario Engine"]
)

# --- MAIN BLOCK: DATA RETRIEVAL ---
with st.spinner(f"Extracting {years_back}-year technical matrices for {ticker}..."):
    df = fetch_tiingo_data(ticker, days_back)
    spy_df = fetch_tiingo_data("SPY", days_back)

if df is None or df.empty:
    st.error(f"Execution Halted: Data stream for '{ticker}' returned empty. Verify ticker symbol.")
else:
    # Math: Technical Analysis Signals
    df['SMA20'] = df['close'].rolling(window=20).mean()
    df['SMA50'] = df['close'].rolling(window=50).mean()
    df['RSI'] = calculate_rsi(df['close'])
    
    current_price = df['close'].iloc[-1]
    latest_rsi = df['RSI'].iloc[-1]
    latest_sma20 = df['SMA20'].iloc[-1]
    
    # Quantitative Decision Engine Rules
    if latest_rsi < 35 and current_price > latest_sma20:
        tech_signal = "🟢 STRONG BUY"
        signal_color = "#00ffcc"
    elif latest_rsi < 45:
        tech_signal = "🟢 ACCUMULATE / BUY"
        signal_color = "#0aff68"
    elif latest_rsi > 70:
        tech_signal = "🔴 STRONG SELL / OVERBOUGHT"
        signal_color = "#ff007f"
    elif latest_rsi > 55 and current_price < latest_sma20:
        tech_signal = "🟡 REDUCE / SELL"
        signal_color = "#ff9900"
    else:
        tech_signal = "⚪ HOLD / NEUTRAL"
        signal_color = "#ffffff"

    # Math: Academic CAPM Framework & Beta
    df['Return'] = df['close'].pct_change()
    if spy_df is not None and not spy_df.empty:
        spy_df['Return'] = spy_df['close'].pct_change()
        aligned = pd.concat([df['Return'], spy_df['Return']], axis=1).dropna()
        aligned.columns = ['Stock', 'SPY']
        beta = aligned.cov().iloc[0, 1] / aligned['SPY'].var()
        
        # Academic CAPM: Expected Return = RiskFree(assumed 4.5%) + Beta * MarketPremium(assumed 6%)
        risk_free = 0.045
        market_premium = 0.06
        capm_expected_return = risk_free + (beta * market_premium)
    else:
        beta, capm_expected_return = 1.0, 0.0

    # --- PARTITION 1: TECHNICAL & ACADEMIC SIGNALS ---
    st.subheader("📊 Algorithmic & Academic Valuation")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Close", f"${current_price:.2f}")
    
    with col2:
        st.markdown(f"<div style='text-align:center; padding:5px; border-radius:5px; background:rgba(255,255,255,0.05);'><b>Quant Signal</b><br><span style='color:{signal_color}; font-size:1.2rem; font-weight:bold;'>{tech_signal}</span></div>", unsafe_allow_html=True)
        
    col3.metric("Calculated Beta", f"{beta:.2f}", f"vs SPY ({years_back}Y Window)")
    col4.metric("Academic CAPM Target", f"{capm_expected_return*100:.2f}%", "Est. Annual Return")

    # --- PARTITION 2: INTERACTIVE CHARTING ---
    st.subheader(f"Technical Candlestick Array: {ticker} ({years_back}-Year History)")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="Price", increasing_line_color='#00ffcc', decreasing_line_color='#ff007f'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='#ff9900', width=1.5), name="20 SMA"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#bc13fe', width=1.5), name="50 SMA"))
    fig.update_layout(xaxis_rangeslider_visible=False, height=450, template="plotly_dark", margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    # --- PARTITION 3: LEADERS VS LAGGARDS (TOP / WORST MATRIX) ---
    st.markdown("---")
    st.subheader("⚖️ Macro Terminal: Market Drivers")
    
    show_worst = st.checkbox("🔄 Toggle View: Show Market Laggards (Worst Performing)", value=False)
    
    market_universe = {
        "NVDA": {"name": "Nvidia Corp", "perf": 42.5, "prices": [110, 115, 128, 122, 135, 148, 156.7]},
        "TSLA": {"name": "Tesla Inc", "perf": 18.2, "prices": [210, 205, 220, 218, 235, 242, 248.2]},
        "AAPL": {"name": "Apple Inc", "perf": 12.4, "prices": [175, 178, 182, 180, 189, 192, 196.7]},
        "INTC": {"name": "Intel Corp", "perf": -28.4, "prices": [34, 31, 28, 29, 26, 23, 24.3]},
        "WBA": {"name": "Walgreens", "perf": -38.1, "prices": [18, 16, 15, 13, 12, 10, 11.1]},
        "NKE": {"name": "Nike Inc", "perf": -14.2, "prices": [95, 92, 88, 89, 84, 80, 81.5]}
    }
    
    display_tickers = ["INTC", "WBA", "NKE"] if show_worst else ["NVDA", "TSLA", "AAPL"]
    st.markdown(f"**Displaying {'Underperforming Assets' if show_worst else 'Top Generating Assets'} (Trailing Relative Trend)**")
    
    l_col1, l_col2, l_col3 = st.columns(3)
    cols = [l_col1, l_col2, l_col3]
    
    for idx, tk in enumerate(display_tickers):
        stock_info = market_universe[tk]
        with cols[idx]:
            st.metric(f"{tk} ({stock_info['name']})", f"{stock_info['prices'][-1]} USD", f"{stock_info['perf']}%")
            spark_fig = go.Figure(go.Scatter(y=stock_info['prices'], line=dict(color='#ff007f' if show_worst else '#0aff68', width=2)))
            spark_fig.update_layout(xaxis_visible=False, yaxis_visible=False, height=80, margin=dict(l=5, r=5, t=5, b=5), template="plotly_dark")
            st.plotly_chart(spark_fig, use_container_width=True, key=f"spark_{tk}")

    # --- PARTITION 4: DYNAMIC AI ENGINE ENHANCEMENT ---
    st.markdown("---")
    st.subheader(f"🧠 AI Core Module: {ai_tool}")
    
    if st.button("Execute Neural Simulation"):
        with st.spinner("Processing prompt structures..."):
            try:
                # We still send the tail 10 days of data to the AI model context so it doesn't run out of tokens 
                recent_matrix = df.tail(10)[['close', 'volume', 'RSI']].to_string()
                
                if ai_tool == "📊 Quant Signal Analyzer":
                    prompt_focus = f"Analyze these indicators over a {years_back}-year historical baseline: RSI is currently at {latest_rsi:.1f}, price is relative to 20 SMA at {latest_sma20:.2f}. Deliver an academic evaluation supporting a '{tech_signal}' action plan detailing specific entry or exit boundary mechanics."
                elif ai_tool == "🧠 Sentiment Catalyst Simulator":
                    prompt_focus = f"Evaluate potential underlying psychological factors influencing trading volume shifts and retail momentum spikes over this stock's {years_back}-year trajectory. Map this against behavioral finance theory."
                else:
                    prompt_focus = f"Simulate a macro-economic scenario where interest rates change by +/- 50bps. How would this macro shift interact with this stock's calculated Beta coefficient of {beta:.2f} (measured over a {years_back}-year timeframe)?"

                full_prompt = f"""
                You are a Senior Quantitative Portfolio Manager and Financial AI Engine.
                Asset: {ticker}
                Historical Horizon: {years_back} Years
                Current Performance Context: {prompt_focus}
                
                Recent 10-Day Market Data Array:
                {recent_matrix}
                
                Provide a sharp, high-level tactical intelligence brief. Ensure it contains zero fluff.
                Conclude with an explicit statement that the analysis is systemic AI generation and does not represent legally binding financial execution advice.
                """
                
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt
                )
                st.success("Execution Sequence Complete.")
                st.write(response.text)
            except Exception as e:
                st.error(f"Neural Core Connection Aborted: {e}")
