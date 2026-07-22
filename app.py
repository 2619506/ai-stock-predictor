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
# 1. INITIALIZATION & SETUP
# ==========================================
st.set_page_config(page_title="AI Equity Oracle", page_icon="📈", layout="wide")

# Custom CSS for glassmorphic/dark theme components
st.markdown("""
    <style>
    .metric-box { background: rgba(0, 255, 204, 0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #00ffcc; margin-bottom: 20px;}
    .sentiment-pos { color: #0aff68; font-weight: bold; }
    .sentiment-neg { color: #ff007f; font-weight: bold; }
    .sentiment-neu { color: #cbd5e1; font-weight: bold; }
    .ai-explain { background: rgba(188, 19, 254, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #bc13fe; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 AI Equity Oracle")
st.write("Unbiased Market Intelligence: Search, Visualize, Analyze, and Predict.")

# ==========================================
# 2. DYNAMIC SIDEBAR CONFIGURATION
# ==========================================
st.sidebar.header("Target Matrix")
search_ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, NVDA):", "NVDA").upper()
historical_years = st.sidebar.slider("Historical Data (Years):", 1, 5, 2)
prediction_days = st.sidebar.slider("AI Forecast Horizon (Days):", 10, 365, 90)

@st.cache_data(ttl=3600)
def load_data(ticker, years):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years * 365)
    df = yf.download(ticker, start=start_date, end=end_date)
    # Flatten MultiIndex columns if necessary (common in newer yfinance versions)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.reset_index(inplace=True)
    return df

@st.cache_data(ttl=3600)
def fetch_news(ticker):
    try:
        tkr = yf.Ticker(ticker)
        return tkr.news[:10]
    except:
        return []

@st.cache_data(ttl=86400) # Cache daily to prevent API limits
def get_market_screener():
    # Basket of popular market-driving stocks for the Top/Bottom screener
    tickers = "AAPL MSFT TSLA NVDA AMZN META GOOGL NFLX AMD INTC BA DIS JPM V WMT PG XOM"
    data = yf.download(tickers, period="1y", interval="1d")['Close']
    returns = ((data.iloc[-1] - data.iloc[0]) / data.iloc[0]) * 100
    returns = returns.sort_values(ascending=False).dropna()
    return returns

# Load main target data
with st.spinner("Syncing with Market Matrices..."):
    df = load_data(search_ticker, historical_years)

if df.empty or 'Close' not in df.columns:
    st.error(f"No data found for '{search_ticker}'. Please check the ticker symbol.")
    st.stop()

# Technical Indicator Calculations
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['SMA_200'] = df['Close'].rolling(window=200).mean()

# Relative Strength Index (RSI) Calculation
delta = df['Close'].diff(1)
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

# Extract safe scalars for metrics
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
st.sidebar.markdown(f"**24h Change:** {pct_change:+.2f}%")

# ==========================================
# 3. TABS ARCHITECTURE
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Technical Chart", 
    "🔮 AI Predictor", 
    "📰 Sentiment & Explainability", 
    "⚖️ Market Screener",
    "🤖 Unbiased Verdict"
])

# ------------------------------------------
# TAB 1: INTERACTIVE CHART (1 to 5 Years)
# ------------------------------------------
with tab1:
    st.header(f"Historical Trajectory: {search_ticker}")
    st.write("Analyze the market ups and downs using raw price and long-term Moving Averages.")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close Price', line=dict(color='#00bfff')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], name='50-Day SMA', line=dict(color='#0aff68', dash='dot')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_200'], name='200-Day SMA', line=dict(color='#ff007f', dash='dot')))
    
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# TAB 2: AI FUTURE PREDICTION
# ------------------------------------------
with tab2:
    st.header("AI Future Trend Forecasting")
    st.write(f"Using polynomial machine learning regression on {historical_years} years of historical data to project {prediction_days} days into the future.")
    
    # Prepare data for Machine Learning model
    df_model = df[['Date', 'Close']].dropna().copy()
    df_model['Days'] = (df_model['Date'] - df_model['Date'].min()).dt.days
    X = df_model[['Days']]
    y = df_model['Close']
    
    # Train Model (Polynomial Ridge Regression captures overarching trends while reducing severe overfitting)
    model = make_pipeline(PolynomialFeatures(degree=3), Ridge(alpha=1.0))
    model.fit(X, y)
    
    # Predict the past (to draw the AI's fitted trendline)
    df_model['Trend'] = model.predict(X)
    
    # Predict the future
    last_date = df_model['Date'].max()
    last_day = df_model['Days'].max()
    future_days = np.array([[last_day + i] for i in range(1, prediction_days + 1)])
    future_dates = [last_date + timedelta(days=i) for i in range(1, prediction_days + 1)]
    future_preds = model.predict(future_days)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_model['Date'], y=df_model['Close'], name='Historical Close', line=dict(color='rgba(255,255,255,0.2)')))
    fig2.add_trace(go.Scatter(x=df_model['Date'], y=df_model['Trend'], name='AI Fitted Trend', line=dict(color='#bc13fe')))
    fig2.add_trace(go.Scatter(x=future_dates, y=future_preds, name='AI Forecast', line=dict(color='#0aff68', width=3)))
    
    fig2.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig2, use_container_width=True)
    
    pred_change = ((future_preds[-1] - current_price) / current_price) * 100
    st.markdown(f"<div class='ai-explain'><b>AI Extrapolation Summary:</b> Based strictly on the mathematical momentum of the past {historical_years} years, the ML model predicts the asset price will shift by <b>{pred_change:+.2f}%</b> over the next {prediction_days} days. <i>Note: Mathematical models identify trends; they do not account for sudden black swan events or unexpected corporate earnings surprises.</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: AI SENTIMENT & NEWS EXPLAINABILITY
# ------------------------------------------
with tab3:
    st.header("News & Sentiment Analysis")
    st.write("Aggregating current news headlines and running Natural Language heuristics.")
    
    news_items = fetch_news(search_ticker)
    
    # Simple NLP dictionaries
    pos_words = ['surge', 'jump', 'grow', 'beat', 'up', 'profit', 'dividend', 'buy', 'upgrade', 'bull', 'high', 'gain']
    neg_words = ['drop', 'fall', 'miss', 'down', 'loss', 'sell', 'downgrade', 'bear', 'low', 'lawsuit', 'penalty', 'plunge']
    
    if not news_items:
        st.info("No recent news found for this ticker from the primary data source.")
    else:
        total_score = 0
        for item in news_items:
            title = item.get('title', '')
            publisher = item.get('publisher', 'News Source')
            link = item.get('link', '#')
            
            # NLP Keyword matching
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
        st.subheader("AI Explainability")
        explain_text = f"The AI processed {len(news_items)} recent headlines. "
        if total_score > 2:
            explain_text += "The aggregated sentiment leans **Positive**. Words indicating growth, institutional upgrades, or earnings beats currently dominate the media narrative, which historically correlates with short-term buying pressure."
        elif total_score < -2:
            explain_text += "The aggregated sentiment leans **Negative**. Words indicating drops, downgrades, or losses dominate the narrative, suggesting short-term market anxiety or aggressive selling pressure."
        else:
            explain_text += "The aggregated sentiment is **Neutral/Mixed**. The news contains an equal balance of positive and negative drivers, or lacks strong emotional trigger words, indicating potential consolidation."
            
        st.markdown(f"<div class='ai-explain'><b>Why this matters:</b> {explain_text} Algorithmic trading systems often parse headlines in milliseconds. Understanding human and media sentiment provides crucial context to purely numerical price movements on the charts.</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: MARKET SCREENER
# ------------------------------------------
with tab4:
    st.header("Top & Bottom Performers")
    st.write("Screening a dynamic basket of market leaders for 1-Year trailing returns.")
    
    with st.spinner("Running cross-market scan..."):
        screener_data = get_market_screener()
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("🔥 Top 5 (Highly Profitable)")
        top_5 = screener_data.head(5)
        for tkr, val in top_5.items():
            st.markdown(f"<div class='metric-box'><b>{tkr}</b>: <span style='color:#0aff68'>+{val:.2f}%</span></div>", unsafe_allow_html=True)
            
    with colB:
        st.subheader("🧊 Bottom 5 (Caution/Avoid)")
        bottom_5 = screener_data.tail(5)
        for tkr, val in bottom_5.items():
            color = "#ff007f" if val < 0 else "#0aff68"
            st.markdown(f"<div class='metric-box' style='border-left-color:#ff007f;'><b>{tkr}</b>: <span style='color:{color}'>{val:.2f}%</span></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 5: UNBIASED AI VERDICT
# ------------------------------------------
with tab5:
    st.header("Unbiased AI Recommendation")
    st.write("Synthesizing technical indicators and predictive data to generate an emotionless rating.")
    
    score = 0
    reasons = []
    
    # Logic Rule 1: RSI (Momentum)
    if current_rsi < 30:
        score += 1
        reasons.append(f"The RSI is {current_rsi:.1f}. This is technically 'Oversold', indicating the asset may be undervalued and due for a bullish rebound.")
    elif current_rsi > 70:
        score -= 1
        reasons.append(f"The RSI is {current_rsi:.1f}. This is technically 'Overbought', indicating the asset may be overvalued and due for a bearish correction.")
    else:
        reasons.append(f"The RSI is {current_rsi:.1f}, placing it in a neutral momentum zone.")
        
    # Logic Rule 2: Moving Average Crossover (Trend)
    if current_price > current_sma50:
        score += 1
        reasons.append(f"The current price (${current_price:.2f}) sits above its 50-day SMA (${current_sma50:.2f}), confirming an ongoing medium-term uptrend.")
    else:
        score -= 1
        reasons.append(f"The current price (${current_price:.2f}) sits below its 50-day SMA (${current_sma50:.2f}), confirming an ongoing medium-term downtrend.")
        
    # Logic Rule 3: Predictive Extrapolation (Future)
    if 'pred_change' in locals():
        if pred_change > 5:
            score += 1
            reasons.append(f"The ML polynomial forecast projects a positive trajectory (+{pred_change:.1f}%) over the selected timeframe.")
        elif pred_change < -5:
            score -= 1
            reasons.append(f"The ML polynomial forecast projects a negative trajectory ({pred_change:.1f}%) over the selected timeframe.")
        
    # Generate Verdict
    if score >= 2:
        verdict = "BUY"
        v_color = "#0aff68"
    elif score <= -2:
        verdict = "SELL / AVOID"
        v_color = "#ff007f"
    else:
        verdict = "HOLD"
        v_color = "#ff9900"
        
    st.markdown(f"<h1 style='text-align: center; color: {v_color}; font-size: 4rem; margin-top: 20px;'>{verdict}</h1>", unsafe_allow_html=True)
    
    st.markdown("### 🧠 AI Logical Breakdown:")
    for r in reasons:
        st.markdown(f"- {r}")
        
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.caption("🚨 DISCLAIMER: This application is for academic demonstration and portfolio enhancement purposes only. Algorithmic predictions carry inherent risk. Always perform independent due diligence before executing trades.")
