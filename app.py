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
# 1. INITIALIZATION & SETUP
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

load_dotenv()

TIINGO_API_KEY = os.environ.get("TIINGO_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="AI Quant Workstation", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #0b0f19; color: white; }
    .stMetric { background: rgba(0, 255, 204, 0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(0, 255, 204, 0.2); }
    .news-card { padding: 15px; border-radius: 8px; background: rgba(255, 255, 255, 0.05); margin-bottom: 10px; border-left: 4px solid #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

if not TIINGO_API_KEY or not GEMINI_API_KEY:
    st.error("⚠️ **API Keys Missing!** Check your Streamlit Secrets.")
    st.stop()

# ==========================================
# 2. DATA FUNCTIONS
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
    url = f"https://api.tiingo.com/tiingo/news?tickers={symbol}&limit=10"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except: pass
    return []

# ==========================================
# 3. SIDEBAR NAVIGATION & GLOBAL CONTROLS
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/182px-Python-logo-notext.svg.png", width=50)
st.sidebar.title("System Modules")

# The 4 distinct layout sections as a navigation menu
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

# Pre-fetch data for the active ticker
df = fetch_tiingo_data(ticker, days_back)
if df.empty:
    st.error(f"Data stream offline for '{ticker}'.")
    st.stop()

df['SMA20'] = df['close'].rolling(window=20).mean()
df['RSI'] = calculate_rsi(df['close'])
current_price = df['close'].iloc[-1]
latest_rsi = df['RSI'].iloc[-1]

# ==========================================
# 4. VIEW RENDERING (THE 4 SECTIONS)
# ==========================================

# ------------------------------------------
# SECTION 1: CHARTING
# ------------------------------------------
if app_mode == "📈 1. Market Charting":
    st.title(f"📈 Charting Terminal: {ticker}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Close", f"${current_price:.2f}")
    col2.metric("14-Day RSI", f"{latest_rsi:.2f}")
    col3.metric("20-Day SMA", f"${df['SMA20'].iloc[-1]:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='#ff9900', width=1.5), name="20 SMA"))
    fig.update_layout(template="plotly_dark", height=550, margin=dict(l=0, r=0, t=10, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# SECTION 2: GLOBAL SCREENER
# ------------------------------------------
elif app_mode == "🌐 2. Global Screener":
    st.title("🌐 Market Screener (Top & Bottom)")
    st.write("Cross-market analysis of currently highly-searched leading and lagging tech assets.")
    
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
                # USING GEMINI 1.5 FLASH TO PREVENT 404 ERRORS
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
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
            date_str = article.get('publishedDate', '')[:10]
            
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
# SECTION 4: AI CHAT (FLAT & STABLE)
# ------------------------------------------
elif app_mode == "💬 4. Neural AI Chat":
    st.title(f"💬 Neural AI Assistant ({ticker})")
    st.write("Ask the quantitative model about trading strategies, indicators, or recent price action.")
    
    # Render history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Render input box
    if user_input := st.chat_input("E.g., Based on the current RSI, is this stock overbought?"):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        # Display AI response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    # USING GEMINI 1.5 FLASH TO PREVENT 404 ERRORS
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=f"You are an expert quantitative analyst. Stock: {ticker}. Current Price: {current_price:.2f}. RSI: {latest_rsi:.1f}. User Query: {user_input}"
                    )
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"API Error: {e}")
