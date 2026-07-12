import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

# Load local environment variables
load_dotenv()

TIINGO_API_KEY = os.environ.get("TIINGO_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="AI Quant Workstation", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #12121e; }
    .stMetric { background: rgba(26, 26, 46, 0.6); padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 255, 204, 0.2); }
    .guardrail { padding: 15px; border-radius: 8px; border-left: 5px solid #ff007f; background: rgba(255,0,127,0.1); margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Holistic AI Quant Workstation")

if not TIINGO_API_KEY or not GEMINI_API_KEY:
    st.error("⚠️ **API Keys Missing!**")
    st.stop()

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=3600)
def fetch_tiingo_data(symbol, days):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Token {TIINGO_API_KEY}'}
    start_date = (datetime.today() - timedelta(days=days)).strftime('%Y-%m-%d')
    url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json():
            df = pd.DataFrame(response.json())
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            df.set_index('date', inplace=True)
            return df
    except: pass
    return pd.DataFrame()

# NEW: Fetch Live News from Tiingo
@st.cache_data(ttl=1800)
def fetch_tiingo_news(symbol):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Token {TIINGO_API_KEY}'}
    url = f"https://api.tiingo.com/tiingo/news?tickers={symbol}&limit=5"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except: pass
    return []

# --- SIDEBAR ---
st.sidebar.header("🛸 Control Matrix")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
years_back = st.sidebar.slider("Historical Window (Years)", min_value=1, max_value=5, value=1)
days_back = years_back * 365

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Core Add-ons")
ai_tool = st.sidebar.selectbox("Select Active Neural Module", ["📊 Quant Signal Analyzer", "🧠 Sentiment Catalyst Simulator", "🔮 Macro Scenario Engine"])

# --- DATA RETRIEVAL ---
with st.spinner(f"Extracting multi-dimensional matrices for {ticker}..."):
    df = fetch_tiingo_data(ticker, days_back)
    spy_df = fetch_tiingo_data("SPY", days_back)
    news_data = fetch_tiingo_news(ticker)

if df is None or df.empty:
    st.error(f"Execution Halted: Data stream for '{ticker}' returned empty.")
else:
    df['SMA20'] = df['close'].rolling(window=20).mean()
    df['SMA50'] = df['close'].rolling(window=50).mean()
    df['RSI'] = calculate_rsi(df['close'])
    
    current_price = df['close'].iloc[-1]
    latest_rsi = df['RSI'].iloc[-1]
    latest_sma20 = df['SMA20'].iloc[-1]
    
    if latest_rsi < 35 and current_price > latest_sma20: tech_signal, signal_color = "🟢 STRONG BUY", "#00ffcc"
    elif latest_rsi < 45: tech_signal, signal_color = "🟢 ACCUMULATE", "#0aff68"
    elif latest_rsi > 70: tech_signal, signal_color = "🔴 OVERBOUGHT / SELL", "#ff007f"
    elif latest_rsi > 55 and current_price < latest_sma20: tech_signal, signal_color = "🟡 REDUCE", "#ff9900"
    else: tech_signal, signal_color = "⚪ HOLD / NEUTRAL", "#ffffff"

    df['Return'] = df['close'].pct_change()
    if spy_df is not None and not spy_df.empty:
        spy_df['Return'] = spy_df['close'].pct_change()
        aligned = pd.concat([df['Return'], spy_df['Return']], axis=1).dropna()
        aligned.columns = ['Stock', 'SPY']
        beta = aligned.cov().iloc[0, 1] / aligned['SPY'].var()
        capm_expected_return = 0.045 + (beta * 0.06)
    else:
        beta, capm_expected_return = 1.0, 0.0

    # --- THE DOCTOR: COGNITIVE GUARDRAIL ---
    if beta > 1.5 or latest_rsi > 75 or latest_rsi < 25:
        st.markdown(f"""
        <div class="guardrail">
            <h4 style="margin:0; color:#ff007f;">🩺 Behavioral Guardrail Activated</h4>
            <p style="margin:5px 0 0 0; font-size:0.9rem;">High volatility or extreme momentum detected. Ensure trades are executed based on systemic rules, not FOMO or panic. Guard your capital.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- PARTITION 1: TECHNICALS & THE PROFESSOR ---
    st.subheader("📊 Algorithmic & Academic Valuation")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Close", f"${current_price:.2f}")
    with col2: st.markdown(f"<div style='text-align:center; padding:5px; border-radius:5px; background:rgba(255,255,255,0.05);'><b>Quant Signal</b><br><span style='color:{signal_color}; font-size:1.2rem; font-weight:bold;'>{tech_signal}</span></div>", unsafe_allow_html=True)
    col3.metric("Calculated Beta", f"{beta:.2f}", f"vs SPY")
    col4.metric("CAPM Target", f"{capm_expected_return*100:.2f}%", "Est. Return")

    # The Professor: Expandable Learning
    with st.expander("🎓 The Professor's Desk: Learn the Math behind these Metrics"):
        st.write("**CAPM (Capital Asset Pricing Model):** Calculates expected return based on risk. Formula: `Expected Return = Risk Free Rate + Beta * (Market Return - Risk Free Rate)`")
        st.write("**Beta:** Measures how volatile the stock is compared to the S&P 500. A Beta of 1.5 means the stock moves 50% more violently than the broader market.")
        st.write("**RSI (Relative Strength Index):** A momentum oscillator from 0 to 100. Above 70 means the stock is overbought (too expensive too fast). Below 30 means oversold.")

    # --- PARTITION 2: CHARTING ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="Price", increasing_line_color='#00ffcc', decreasing_line_color='#ff007f'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='#ff9900', width=1.5), name="20 SMA"))
    fig.update_layout(xaxis_rangeslider_visible=False, height=400, template="plotly_dark", margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # --- PARTITION 3: THE PRO (LIVE NEWS & SENTIMENT) ---
    st.markdown("---")
    colA, colB = st.columns([1, 1])
    
    with colA:
        st.subheader("📰 Live Financial Headlines")
        headlines_text = ""
        if news_data:
            for article in news_data:
                title = article.get('title', 'Headline Unavailable')
                source = article.get('source', 'News Source')
                headlines_text += f"- {title}\n"
                st.markdown(f"<p style='font-size:0.85rem; margin-bottom:5px;'>• {title} <i>({source})</i></p>", unsafe_allow_html=True)
        else:
            st.write("No recent news found for this ticker.")
            headlines_text = "No recent news."

    with colB:
        st.subheader("🧠 Daily News Sentiment Engine")
        if st.button("Grade Today's News Sentiment"):
            with st.spinner("Analyzing semantics..."):
                try:
                    news_prompt = f"Act as a professional financial analyst. Read these recent headlines for {ticker}:\n{headlines_text}\n\nProvide a 3-sentence summary of the news sentiment. Grade the overall sentiment as BULLISH, BEARISH, or NEUTRAL."
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=news_prompt)
                    st.success("Sentiment Scored.")
                    st.write(response.text)
                except:
                    st.error("Failed to connect to Neural Engine.")

    # --- PARTITION 4: DYNAMIC AI ENGINE ---
    st.markdown("---")
    st.subheader(f"🔮 AI Core Module: {ai_tool}")
    if st.button("Execute Deep Neural Simulation"):
        with st.spinner("Processing prompt structures..."):
            try:
                recent_matrix = df.tail(10)[['close', 'volume', 'RSI']].to_string()
                full_prompt = f"""
                You are a Senior Quantitative Portfolio Manager.
                Asset: {ticker}
                Task: Focus your analysis exclusively on this framework: {ai_tool}.
                Current RSI: {latest_rsi:.1f}. Beta: {beta:.2f}.
                Recent Data:
                {recent_matrix}
                Provide a sharp, high-level tactical intelligence brief.
                """
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(model='gemini-2.5-flash', contents=full_prompt)
                st.write(response.text)
            except:
                st.error("Neural Core Connection Aborted.")
