import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import os
import gc
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

# ==========================================
# 1. SYSTEM INITIALIZATION & MEMORY MANAGEMENT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if len(st.session_state.messages) > 10:
    st.session_state.messages = st.session_state.messages[-10:]

load_dotenv()

TIINGO_API_KEY = os.environ.get("TIINGO_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="AI Quant Workstation", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #0b0f19; color: white; }
    .stMetric { background: rgba(0, 255, 204, 0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(0, 255, 204, 0.2); }
    .news-card { padding: 15px; border-radius: 8px; background: rgba(255, 255, 255, 0.05); margin-bottom: 10px; border-left: 4px solid #00ffcc; }
    .guardrail { padding: 15px; border-radius: 8px; border-left: 5px solid #ff007f; background: rgba(255,0,127,0.1); margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

if not TIINGO_API_KEY or not GEMINI_API_KEY:
    st.error("⚠️ **API Keys Missing!** Check your Streamlit Secrets.")
    st.stop()

# ==========================================
# 2. OPTIMIZED DATA ENGINES
# ==========================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=3600, max_entries=5)
def fetch_and_calculate_data(symbol, days):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Token {TIINGO_API_KEY}'}
    start_date = (datetime.today() - timedelta(days=days)).strftime('%Y-%m-%d')
    url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 and response.json():
            df = pd.DataFrame(response.json())
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            df.set_index('date', inplace=True)
            df['SMA20'] = df['close'].rolling(window=20).mean()
            df['RSI'] = calculate_rsi(df['close'])
            return df
    except requests.exceptions.RequestException:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1800, max_entries=5)
def fetch_tiingo_news(symbol):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Token {TIINGO_API_KEY}'}
    url = f"https://api.tiingo.com/tiingo/news?tickers={symbol}&limit=10"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

# ==========================================
# 3. SIDEBAR NAVIGATION & MATH LOGIC
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/182px-Python-logo-notext.svg.png", width=50)
st.sidebar.title("System Modules")

app_mode = st.sidebar.radio("Select View:", [
    "📈 1. Market Charting", 
    "🌐 2. Global Screener", 
    "📰 3. Live News Feed", 
    "💬 4. Neural AI Chat"
])

st.sidebar.markdown("---")
st.sidebar.subheader("Target Parameters")
ticker = st.sidebar.text_input("Target Ticker", value="AAPL").upper()
years_back = st.sidebar.slider("Time Horizon (Years)", min_value=1, max_value=5, value=1)
days_back = years_back * 365

with st.spinner("Synchronizing feeds and computing CAPM..."):
    df = fetch_and_calculate_data(ticker, days_back)
    spy_df = fetch_and_calculate_data("SPY", days_back)

if df.empty:
    st.error(f"Data stream offline or timed out for '{ticker}'. Please try again.")
    st.stop()

# ACADEMIC MATH: Beta and CAPM Calculation
if not spy_df.empty:
    aligned = pd.concat([df['close'].pct_change(), spy_df['close'].pct_change()], axis=1).dropna()
    aligned.columns = ['Stock', 'SPY']
    beta = aligned.cov().iloc[0, 1] / aligned['SPY'].var() if aligned['SPY'].var() != 0 else 1.0
    capm_expected_return = 0.045 + (beta * 0.06) # Risk Free: 4.5%, Market Premium: 6%
else:
    beta, capm_expected_return = 1.0, 0.105

current_price = df['close'].iloc[-1]
latest_rsi = df['RSI'].iloc[-1]
latest_sma = df['SMA20'].iloc[-1]

# ==========================================
# 4. MODULE RENDERING
# ==========================================

# ------------------------------------------
# SECTION 1: CHARTING & ACADEMICS
# ------------------------------------------
if app_mode == "📈 1. Market Charting":
    st.title(f"📈 Charting Terminal: {ticker}")
    
    # THE DOCTOR: COGNITIVE GUARDRAIL
    if beta > 1.5 or latest_rsi > 75 or latest_rsi < 25:
        st.markdown(f"""
        <div class="guardrail">
            <h4 style="margin:0; color:#ff007f;">🩺 Behavioral Guardrail Activated</h4>
            <p style="margin:5px 0 0 0; font-size:0.9rem;">Extreme momentum (RSI) or high volatility (Beta) detected. Execute trades systematically, not emotionally. Guard your capital.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Close", f"${current_price:.2f}")
    col2.metric("14-Day RSI", f"{latest_rsi:.2f}")
    col3.metric("Calculated Beta", f"{beta:.2f}", f"vs SPY")
    col4.metric("CAPM Target", f"{capm_expected_return*100:.2f}%", "Est. Return")

    # THE PROFESSOR'S DESK
    with st.expander("🎓 The Professor's Desk: Learn the Math behind these Metrics"):
        st.write("**CAPM (Capital Asset Pricing Model):** Calculates expected return based on risk. Formula: `Expected Return = Risk Free Rate + Beta * (Market Return - Risk Free Rate)`")
        st.write("**Beta:** Measures how volatile the stock is compared to the S&P 500. A Beta of 1.5 means the stock moves 50% more violently than the broader market.")
        st.write("**RSI (Relative Strength Index):** A momentum oscillator from 0 to 100. Above 70 means the stock is overbought (too expensive too fast). Below 30 means oversold.")

    st.markdown("<br>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='#ff9900', width=1.5), name="20 SMA"))
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, t=10, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    del fig
    gc.collect()

# ------------------------------------------
# SECTION 2: GLOBAL SCREENER
# ------------------------------------------
elif app_mode == "🌐 2. Global Screener":
    st.title("🌐 Market Screener (Top & Bottom)")
    st.write("Cross-market analysis of currently highly-searched tech assets.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color:#0aff68;'>🏆 Top 10 Leaders</h3>", unsafe_allow_html=True)
        top_10 = pd.DataFrame({
            "Ticker": ["NVDA", "DELL", "MU", "WDC", "STX", "INTC", "MRVL", "AMD", "AMAT", "MRNA"],
            "Sector": ["AI Chips", "Hardware", "Memory", "Storage", "Storage", "Semiconductors", "Semiconductors", "Processors", "Equipment", "Biotech"]
        })
        st.dataframe(top_10, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("<h3 style='color:#ff007f;'>📉 Bottom 10 Laggards</h3>", unsafe_allow_html=True)
        bot_10 = pd.DataFrame({
            "Ticker": ["INTU", "ZTS", "ACN", "CTSH", "INSM", "BP", "SHEL", "CNA", "MNDI", "BAB"],
            "Sector": ["Software", "Healthcare", "Consulting", "IT Services", "Biotech", "Energy", "Energy", "Utilities", "Materials", "Aerospace"]
        })
        st.dataframe(bot_10, hide_index=True, use_container_width=True)

# ------------------------------------------
# SECTION 3: LIVE NEWS
# ------------------------------------------
elif app_mode == "📰 3. Live News Feed":
    st.title(f"📰 Live News Feed: {ticker}")
    news_data = fetch_tiingo_news(ticker)
    
    if st.button("🧠 Generate AI Sentiment Report"):
        with st.spinner("Compiling semantic analysis..."):
            try:
                headlines = "\n".join([a.get('title', '') for a in news_data])
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model='gemini-3.5-flash', # UPDATED TO 3.5 FLASH
                    contents=f"You are a quant. Read these headlines for {ticker}:\n{headlines}\n\nProvide a 3-sentence sentiment summary (Bullish/Bearish/Neutral)."
                )
                st.success("Analysis Complete")
                st.info(response.text)
            except Exception as e:
                st.error(f"Neural Error: {e}")
                
    st.markdown("---")
    if news_data:
        for article in news_data:
            title = article.get('title', 'No Title')
            source = article.get('source', 'Unknown Source')
            url = article.get('url', '#')
            date_str = str(article.get('publishedDate', ''))[:10]
            
            st.markdown(f"""
            <div class="news-card">
                <a href="{url}" target="_blank" style="color: #00ffcc; text-decoration: none; font-size: 1.1rem; font-weight: bold;">{title}</a>
                <br>
                <span style="font-size: 0.8rem; color: #aaaaaa;">{source} | {date_str}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No current news available for this ticker.")

# ------------------------------------------
# SECTION 4: AI CHAT
# ------------------------------------------
elif app_mode == "💬 4. Neural AI Chat":
    st.title(f"💬 Neural AI Assistant ({ticker})")
    st.write("Ask the quantitative model about trading strategies, indicators, or recent price action.")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if user_input := st.chat_input(f"E.g., Based on the Beta of {beta:.2f}, how volatile is this asset?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    response = client.models.generate_content(
                        model='gemini-3.5-flash', # UPDATED TO 3.5 FLASH
                        contents=f"You are an expert quantitative analyst. Stock: {ticker}. Current Price: {current_price:.2f}. RSI: {latest_rsi:.1f}. Beta: {beta:.2f}. CAPM Expected Return: {capm_expected_return*100:.2f}%. User Query: {user_input}"
                    )
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"API Error: {e}")
