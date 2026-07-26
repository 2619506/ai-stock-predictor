import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# ==========================================
# 1. INITIALIZATION & STYLING ENGINE
# ==========================================
st.set_page_config(page_title="Algorithmic Equity Intelligence", page_icon="❖", layout="wide")

st.markdown("""
    <style>
    /* 1. Animated Deep Space Background */
    .stApp {
        background: linear-gradient(-45deg, #070a10, #0f1422, #161f33, #090e1a);
        background-size: 400% 400%;
        animation: gradientBG 16s ease infinite;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* 2. Merged Sidebar with Subtle Vertical Divider */
    [data-testid="stSidebar"] {
        background: transparent !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 3. Main Glass Platform Pane */
    .block-container {
        background: rgba(13, 17, 28, 0.55);
        backdrop-filter: blur(16px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
        margin-top: 1rem;
    }

    /* 4. Refractive Glowing Diamond Crystals */
    .diamond-crystal {
        position: fixed;
        width: 110px;
        height: 110px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1.5px solid rgba(255, 255, 255, 0.85);
        transform: rotate(45deg);
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.5), inset 0 0 15px rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(6px);
        z-index: -1;
        pointer-events: none;
    }

    /* Inner Diamond Facet Lines */
    .diamond-crystal::before {
        content: '';
        position: absolute;
        top: 12%; left: 12%; right: 12%; bottom: 12%;
        border: 1px solid rgba(255, 255, 255, 0.4);
        background: linear-gradient(45deg, rgba(0, 255, 204, 0.08), rgba(188, 19, 254, 0.08));
    }

    .d1 { width: 130px; height: 130px; top: 12%; left: 3%; animation: floatDiamond1 14s infinite ease-in-out alternate; }
    .d2 { width: 200px; height: 200px; top: 55%; right: 2%; animation: floatDiamond2 20s infinite ease-in-out alternate; }
    .d3 { width: 85px; height: 85px; bottom: 8%; left: 28%; animation: floatDiamond3 16s infinite ease-in-out alternate; }

    @keyframes floatDiamond1 {
        0% { transform: translateY(0px) rotate(45deg) scale(1); box-shadow: 0 0 20px rgba(255,255,255,0.4); }
        100% { transform: translateY(-35px) rotate(60deg) scale(1.06); box-shadow: 0 0 35px rgba(255,255,255,0.8); }
    }
    @keyframes floatDiamond2 {
        0% { transform: translateY(0px) rotate(45deg) scale(1); box-shadow: 0 0 25px rgba(0, 255, 204, 0.3); }
        100% { transform: translateY(45px) rotate(30deg) scale(1.05); box-shadow: 0 0 45px rgba(255,255,255,0.9); }
    }
    @keyframes floatDiamond3 {
        0% { transform: translateY(0px) rotate(45deg); box-shadow: 0 0 15px rgba(188, 19, 254, 0.3); }
        100% { transform: translateY(-25px) rotate(75deg); box-shadow: 0 0 30px rgba(255,255,255,0.7); }
    }

    /* 5. Custom High-End Trading Platform Sheet Tabs */
    button[data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 6px 6px 0px 0px !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.8px !important;
        padding: 12px 22px !important;
        margin-right: 4px !important;
        transition: all 0.25s ease-in-out !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #f1f5f9 !important;
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, rgba(0, 255, 204, 0.15) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
        border-top: 2px solid #00ffcc !important;
        border-left: 1px solid rgba(0, 255, 204, 0.3) !important;
        border-right: 1px solid rgba(0, 255, 204, 0.3) !important;
        border-bottom: none !important;
        color: #00ffcc !important;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.4) !important;
    }

    /* Tab Divider Line */
    div[data-baseweb="tab-border"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* 6. Metric & Explainability Cards */
    .metric-box { 
        background: rgba(0, 255, 204, 0.03); 
        padding: 14px; 
        border-radius: 8px; 
        border-left: 3px solid #00ffcc; 
        margin-bottom: 15px; 
        backdrop-filter: blur(6px); 
        border-top: 1px solid rgba(255,255,255,0.05); 
        border-right: 1px solid rgba(255,255,255,0.05); 
        border-bottom: 1px solid rgba(255,255,255,0.05); 
    }
    .sentiment-pos { color: #0aff68; font-weight: bold; }
    .sentiment-neg { color: #ff007f; font-weight: bold; }
    .sentiment-neu { color: #cbd5e1; font-weight: bold; }
    .ai-explain { 
        background: rgba(188, 19, 254, 0.06); 
        padding: 16px; 
        border-radius: 8px; 
        border-left: 3px solid #bc13fe; 
        font-size: 0.92rem; 
        backdrop-filter: blur(6px); 
        border-top: 1px solid rgba(255,255,255,0.05); 
        border-right: 1px solid rgba(255,255,255,0.05); 
        border-bottom: 1px solid rgba(255,255,255,0.05); 
    }
    </style>
    
    <!-- Background Refractive Diamonds -->
    <div class="diamond-crystal d1"></div>
    <div class="diamond-crystal d2"></div>
    <div class="diamond-crystal d3"></div>
""", unsafe_allow_html=True)

# Title Block
st.markdown("<h1 style='letter-spacing: 1.5px; font-weight: 700;'><span style='color: #00ffcc;'>❖</span> ALGORITHMIC EQUITY INTELLIGENCE</h1>", unsafe_allow_html=True)
st.write("Quantitative Data Aggregation, Technical Visualization, and Algorithmic Forecasting.")

# ==========================================
# 2. DYNAMIC SIDEBAR CONFIGURATION
# ==========================================
st.sidebar.markdown("<h4 style='letter-spacing: 1px; color: #cbd5e1;'>CONTROL PANEL</h4>", unsafe_allow_html=True)

# Smart Region Selector
market_region = st.sidebar.selectbox(
    "Select Market Region:", 
    ["United States (US)", "India (NSE)", "United Kingdom (LSE)", "Cryptocurrency"]
)

# Base Ticker Input
raw_ticker = st.sidebar.text_input("Target Ticker:", "NVDA").upper().strip()

# Minimalist Muted Grey Tip
st.sidebar.caption("💡 Tip: Select region or append suffix (.NS, .L, -USD) for global tickers.")

# Auto-Formatting Logic for Yahoo Finance
search_ticker = raw_ticker
if market_region == "India (NSE)" and not raw_ticker.endswith(".NS"):
    search_ticker = f"{raw_ticker}.NS"
elif market_region == "United Kingdom (LSE)" and not raw_ticker.endswith(".L"):
    search_ticker = f"{raw_ticker}.L"
elif market_region == "Cryptocurrency" and not raw_ticker.endswith("-USD"):
    search_ticker = f"{raw_ticker}-USD"

historical_years = st.sidebar.slider("Historical Lookback (Years):", 1, 5, 2)
prediction_days = st.sidebar.slider("Algorithmic Projection Window (Days):", 10, 365, 90)

@st.cache_data(ttl=3600)
def load_data(ticker, years):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years * 365)
    
    # METHOD 1: Try yf.Ticker().history
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        if not df.empty:
            df.reset_index(inplace=True)
            if df['Date'].dt.tz is not None:
                df['Date'] = df['Date'].dt.tz_localize(None)
            return df
    except:
        pass

    # METHOD 2: Fallback to yf.download 
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        df.reset_index(inplace=True)
        if 'Date' in df.columns and df['Date'].dt.tz is not None:
            df['Date'] = df['Date'].dt.tz_localize(None)
            
    return df

@st.cache_data(ttl=3600)
def fetch_news(ticker):
    try:
        tkr = yf.Ticker(ticker)
        return tkr.news[:10]
    except:
        return []

@st.cache_data(ttl=86400)
def get_market_screener():
    tickers_list = [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "LLY", "AVGO", "V", 
        "JPM", "UNH", "WMT", "JNJ", "XOM", "MA", "PG", "COST", "HD", "ORCL", 
        "MRK", "BAC", "ABBV", "CRM", "CVX", "NFLX", "AMD", "KO", "PEP", "TMO", 
        "LIN", "WFC", "ADBE", "DIS", "CSCO", "MCD", "NKE", "INTU", "PFE", "TXN",
        "INTC", "CAT", "QCOM", "IBM", "PM", "BA", "GE", "HON", "UNP", "AMGN",
        "LOW", "CMCSA", "SPGI", "GS", "COP", "RTX", "NOW", "SYK", "ELV", "BKNG",
        "MDT", "AXP", "ISRG", "LMT", "T", "VRTX", "ADP", "REGN", "CB", "ADI",
        "GILD", "MMM", "C", "TGT", "MO", "SLB", "EOG", "GM", "F", "UBER", 
        "PYPL", "ABNB", "SQ", "SHOP", "ZM", "SNOW", "PLTR", "RIVN", "LCID", "SOFI",
        "DKNG", "COIN", "ROKU", "PINS", "ETSY", "Z", "DOCU", "TWLO", "CRWD", "DDOG"
    ]
    tickers_str = " ".join(tickers_list)
    try:
        data = yf.download(tickers_str, period="1y", interval="1d", progress=False)['Close']
        latest_prices = data.ffill().iloc[-1]
        first_prices = data.bfill().iloc[0]
        returns = ((latest_prices - first_prices) / first_prices) * 100
        
        df_screener = pd.DataFrame({
            "Ticker": returns.index,
            "Last Price ($)": latest_prices.values,
            "1-Year Return (%)": returns.values
        }).dropna().sort_values(by="1-Year Return (%)", ascending=False).reset_index(drop=True)
        return df_screener
    except:
        return pd.DataFrame()

# Load main target data
with st.spinner("Synchronizing with Market Matrices..."):
    df = load_data(search_ticker, historical_years)

if df.empty or 'Close' not in df.columns:
    st.error(f"No equity data found for '{search_ticker}'.")
    st.info("""
    **Search Assistance:**
    * Ensure the appropriate market region is selected in the sidebar dropdown.
    * For European stocks, select 'US' and manually append `.PA` (Paris) or `.DE` (Germany).
    """)
    st.stop()

# Technical Indicator Calculations
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['SMA_200'] = df['Close'].rolling(window=200).mean()

delta = df['Close'].diff(1)
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

try:
    current_price = float(df['Close'].iloc[-1])
    price_change = float(df['Close'].iloc[-1] - df['Close'].iloc[-2])
    pct_change = (price_change / float(df['Close'].iloc[-2])) * 100
    current_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
    current_sma50 = float(df['SMA_50'].iloc[-1]) if not pd.isna(df['SMA_50'].iloc[-1]) else current_price
except:
    current_price, price_change, pct_change, current_rsi, current_sma50 = 0, 0, 0, 50, 0

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Price:** ${current_price:,.2f}")
st.sidebar.markdown(f"**24h Trailing Change:** {pct_change:+.2f}%")

# ==========================================
# 3. SHEET TABS ARCHITECTURE
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "TECHNICAL CHARTING", 
    "ALGORITHMIC FORECAST", 
    "SENTIMENT HEURISTICS", 
    "MARKET SCREENER",
    "GLOBAL EXPLORER",
    "QUANT VALUATION"
])

# ------------------------------------------
# TAB 1: TECHNICAL CHARTING
# ------------------------------------------
with tab1:
    st.header(f"Historical Trajectory: {search_ticker}")
    st.write("Visualizing price action against institutional Moving Averages.")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close Price', line=dict(color='#00bfff')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], name='50-Day SMA', line=dict(color='#0aff68', dash='dot')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_200'], name='200-Day SMA', line=dict(color='#ff007f', dash='dot')))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# TAB 2: ALGORITHMIC FORECAST
# ------------------------------------------
with tab2:
    st.header("Algorithmic Trend Forecasting")
    st.write(f"Polynomial regression model fitted on {historical_years} years of market data projecting {prediction_days} days ahead.")
    
    df_model = df[['Date', 'Close']].dropna().copy()
    df_model['Days'] = (df_model['Date'] - df_model['Date'].min()).dt.days
    X = df_model[['Days']]
    y = df_model['Close']
    
    model = make_pipeline(PolynomialFeatures(degree=3), Ridge(alpha=1.0))
    model.fit(X, y)
    
    df_model['Trend'] = model.predict(X)
    
    last_date = df_model['Date'].max()
    last_day = df_model['Days'].max()
    future_days = np.array([[last_day + i] for i in range(1, prediction_days + 1)])
    future_dates = [last_date + timedelta(days=i) for i in range(1, prediction_days + 1)]
    future_preds = model.predict(future_days)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_model['Date'], y=df_model['Close'], name='Historical Close', line=dict(color='rgba(255,255,255,0.2)')))
    fig2.add_trace(go.Scatter(x=df_model['Date'], y=df_model['Trend'], name='Algorithmic Trend', line=dict(color='#bc13fe')))
    fig2.add_trace(go.Scatter(x=future_dates, y=future_preds, name='Forward Forecast', line=dict(color='#0aff68', width=3)))
    
    fig2.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    pred_change = ((future_preds[-1] - current_price) / current_price) * 100
    st.markdown(f"<div class='ai-explain'><b>Extrapolation Summary:</b> Deriving momentum vectors from the past {historical_years} years, the regression model estimates a price shift of <b>{pred_change:+.2f}%</b> over the subsequent {prediction_days} days.</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: SENTIMENT HEURISTICS
# ------------------------------------------
with tab3:
    st.header("Sentiment Heuristics & Explainable AI")
    st.write("Executing Natural Language Processing over real-time financial headlines.")
    
    news_items = fetch_news(search_ticker)
    pos_words = ['surge', 'jump', 'grow', 'beat', 'up', 'profit', 'dividend', 'buy', 'upgrade', 'bull', 'high', 'gain']
    neg_words = ['drop', 'fall', 'miss', 'down', 'loss', 'sell', 'downgrade', 'bear', 'low', 'lawsuit', 'penalty', 'plunge']
    
    if not news_items:
        st.info("No recent news found for this ticker from the primary data feed.")
    else:
        total_score = 0
        for item in news_items:
            if 'content' in item and isinstance(item['content'], dict):
                content = item['content']
                title = content.get('title', 'No Title')
                publisher = content.get('provider', {}).get('displayName', 'News Source')
                link = content.get('canonicalUrl', {}).get('url', '#')
            else:
                title = item.get('title', 'No Title')
                publisher = item.get('publisher', 'News Source')
                link = item.get('link', '#')
            
            t_lower = title.lower()
            score = sum(1 for w in pos_words if w in t_lower) - sum(1 for w in neg_words if w in t_lower)
            total_score += score
            
            if score > 0:
                badge = "<span class='sentiment-pos'>[BULLISH]</span>"
            elif score < 0:
                badge = "<span class='sentiment-neg'>[BEARISH]</span>"
            else:
                badge = "<span class='sentiment-neu'>[NEUTRAL]</span>"
                
            st.markdown(f"- {badge} **{publisher}:** [{title}]({link})", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Algorithmic Sentiment Explainability (XAI)")
        explain_text = f"The heuristic engine processed {len(news_items)} recent headlines. "
        if total_score > 2:
            explain_text += "The aggregated sentiment leans **Positive**, identifying vocabulary correlated with growth or institutional upgrades."
        elif total_score < -2:
            explain_text += "The aggregated sentiment leans **Negative**, identifying vocabulary correlated with pullbacks or institutional selling."
        else:
            explain_text += "The aggregated sentiment is **Neutral/Mixed**, indicating potential price consolidation."
            
        st.markdown(f"<div class='ai-explain'><b>Why this matters:</b> {explain_text} Correlating sentiment with numerical chart indicators provides context to raw market movements.</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: MARKET SCREENER
# ------------------------------------------
with tab4:
    st.header("Sector Performance Extremes")
    st.write("Evaluating a 100-ticker benchmark for trailing 1-Year returns.")
    
    with st.spinner("Aggregating cross-market scan..."):
        screener_df = get_market_screener()
    
    if not screener_df.empty:
        colA, colB = st.columns(2)
        with colA:
            st.subheader("Top 10 Outperformers")
            top_10 = screener_df.head(10)
            for _, row in top_10.iterrows():
                st.markdown(f"<div class='metric-box'><b>{row['Ticker']}</b>: <span style='color:#0aff68'>+{row['1-Year Return (%)']:.2f}%</span></div>", unsafe_allow_html=True)
                
        with colB:
            st.subheader("Bottom 10 Underperformers")
            bottom_10 = screener_df.tail(10)
            for _, row in bottom_10.iterrows():
                color = "#ff007f" if row['1-Year Return (%)'] < 0 else "#0aff68"
                st.markdown(f"<div class='metric-box' style='border-left-color:#ff007f;'><b>{row['Ticker']}</b>: <span style='color:{color}'>{row['1-Year Return (%)']:.2f}%</span></div>", unsafe_allow_html=True)
    else:
        st.error("Market data pipeline temporarily unavailable.")

# ------------------------------------------
# TAB 5: GLOBAL EXPLORER
# ------------------------------------------
with tab5:
    st.header("Global Equities Explorer")
    st.write("Browse trailing 1-Year performance metrics across high-volume equities.")
    
    if 'screener_df' not in locals():
        with st.spinner("Fetching metrics..."):
            screener_df = get_market_screener()
            
    if not screener_df.empty:
        display_df = screener_df.copy()
        display_df['Last Price ($)'] = display_df['Last Price ($)'].apply(lambda x: f"${x:,.2f}")
        display_df['1-Year Return (%)'] = display_df['1-Year Return (%)'].apply(lambda x: f"{x:+.2f}%")
        st.dataframe(display_df, use_container_width=True, height=600)
    else:
        st.error("Data pipeline timeout.")

# ------------------------------------------
# TAB 6: QUANT VALUATION ENGINE
# ------------------------------------------
with tab6:
    st.header("Quantitative Valuation Engine")
    st.write("Synthesizing indicators into a quantitative rating.")
    
    score = 0
    reasons = []
    
    if current_rsi < 30:
        score += 1
        reasons.append(f"RSI is {current_rsi:.1f} (Technically 'Oversold').")
    elif current_rsi > 70:
        score -= 1
        reasons.append(f"RSI is {current_rsi:.1f} (Technically 'Overbought').")
    else:
        reasons.append(f"RSI is {current_rsi:.1f} (Neutral momentum zone).")
        
    if current_price > current_sma50:
        score += 1
        reasons.append(f"Price (${current_price:.2f}) sits above the 50-day SMA (${current_sma50:.2f}).")
    else:
        score -= 1
        reasons.append(f"Price (${current_price:.2f}) sits below the 50-day SMA (${current_sma50:.2f}).")
        
    if 'pred_change' in locals():
        if pred_change > 5:
            score += 1
            reasons.append(f"ML polynomial forecast projects positive trend (+{pred_change:.1f}%).")
        elif pred_change < -5:
            score -= 1
            reasons.append(f"ML polynomial forecast projects negative trend ({pred_change:.1f}%).")
        
    if score >= 2:
        verdict = "STRONG BUY"
        v_color = "#0aff68"
    elif score <= -2:
        verdict = "SELL / AVOID"
        v_color = "#ff007f"
    else:
        verdict = "HOLD / NEUTRAL"
        v_color = "#ff9900"
        
    st.markdown(f"<h1 style='text-align: center; color: {v_color}; font-size: 3.8rem; margin-top: 15px;'>{verdict}</h1>", unsafe_allow_html=True)
    
    st.markdown("### Logical Synthesis Breakdown:")
    for r in reasons:
        st.markdown(f"- {r}")
        
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.caption("ACADEMIC DISCLAIMER: Constructed for portfolio demonstration and research purposes only. Algorithmic predictions carry inherent risk.")
