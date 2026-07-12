import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

# ==========================================
# 1. INITIALIZE SESSION STATE (CRITICAL)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 2. CONFIGURATION & STYLING
# ==========================================
load_dotenv()

TIINGO_API_KEY = os.environ.get("TIINGO_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="AI Quant Workstation", page_icon="📈", layout="wide")

# CSS Styling - Use unsafe_allow_html=True for custom styles
st.markdown("""
    <style>
    .reportview-container { background: #12121e; }
    .stMetric { background: rgba(26, 26, 46, 0.6); padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 255, 204, 0.2); }
    .guardrail { padding: 15px; border-radius: 8px; border-left: 5px solid #ff007f; background: rgba(255,0,127,0.1); margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Holistic AI Quant Workstation")

if not TIINGO_API_KEY or not GEMINI_API_KEY:
    st.error("⚠️ **API Keys Missing!** Ensure TIINGO_API_KEY and GEMINI_API_KEY are set.")
    st.stop()

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
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

# ==========================================
# 4. SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("🛸 Control Matrix")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
years_back = st.sidebar.slider("Historical Window (Years)", min_value=1, max_value=5, value=1)
days_back = years_back * 365

# ==========================================
# 5. DATA RETRIEVAL
# ==========================================
with st.spinner(f"Loading data for {ticker}..."):
    df = fetch_tiingo_data(ticker, days_back)

if df.empty:
    st.error(f"Could not fetch data for '{ticker}'.")
    st.stop()

# Calculations
df['SMA20'] = df['close'].rolling(window=20).mean()
df['RSI'] = calculate_rsi(df['close'])
current_price = df['close'].iloc[-1]
latest_rsi = df['RSI'].iloc[-1]

# ==========================================
# 6. MAIN DASHBOARD (FLAT LAYOUT)
# ==========================================
st.subheader("📊 Algorithmic Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Current Price", f"${current_price:.2f}")
col2.metric("RSI", f"{latest_rsi:.2f}")
col3.metric("Trend", "Bullish" if latest_rsi < 70 else "Overbought")

# --- CHART ---
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close']))
fig.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- MARKET SCREENER (2026 TOP/BOTTOM) ---
st.markdown("---")
st.subheader("🌐 2026 Scientific Market Screener")
s_col1, s_col2 = st.columns(2)
with s_col1:
    st.markdown("🏆 **Top 10 Leaders**")
    top_10 = pd.DataFrame({"Ticker": ["SNDK", "DELL", "MU", "WDC", "STX", "INTC", "MRVL", "AMD", "AMAT", "MRNA"]})
    st.table(top_10)
with s_col2:
    st.markdown("📉 **Bottom 10 Laggards**")
    bot_10 = pd.DataFrame({"Ticker": ["INTU", "ZTS", "ACN", "CTSH", "INSM", "BP", "SHEL", "CNA", "MNDI", "BAB"]})
    st.table(bot_10)

# --- NEWS & SENTIMENT ---
st.markdown("---")
colA, colB = st.columns([1, 1])
news_data = fetch_tiingo_news(ticker)

with colA:
    st.subheader(f"📰 News: {ticker}")
    if news_data:
        for article in news_data:
            st.markdown(f"• {article.get('title', 'Headline Unavailable')}")
    else:
        st.write("No news found.")

with colB:
    st.subheader("🧠 Sentiment Analysis")
    if st.button("Generate Sentiment Score"):
        with st.spinner("Analyzing semantics..."):
            try:
                headlines = "\n".join([a.get('title', '') for a in news_data])
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=f"Analyze sentiment for {ticker} based on these headlines: {headlines}"
                )
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# 7. CHAT ASSISTANT (MUST BE FLAT)
# ==========================================
st.markdown("---")
st.subheader("💬 Neural AI Chat Assistant")

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input - FLAT STRUCTURE
user_input = st.chat_input("Ask about technicals or strategy...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=f"Analyze {ticker} with RSI={latest_rsi:.1f}. User query: {user_input}"
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"AI Assistant Error: {e}")
