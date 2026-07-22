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
st.set_page_config(page_title="Algorithmic Equity Intelligence", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .metric-box { background: rgba(0, 255, 204, 0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #00ffcc; margin-bottom: 20px;}
    .sentiment-pos { color: #0aff68; font-weight: bold; }
    .sentiment-neg { color: #ff007f; font-weight: bold; }
    .sentiment-neu { color: #cbd5e1; font-weight: bold; }
    .ai-explain { background: rgba(188, 19, 254, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #bc13fe; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Algorithmic Equity Intelligence")
st.write("Quantitative Data Aggregation, Technical Visualization, and Algorithmic Forecasting.")

# ==========================================
# 2. DYNAMIC SIDEBAR CONFIGURATION
# ==========================================
st.sidebar.header("Equities Control Panel")
search_ticker = st.sidebar.text_input("Target Ticker (e.g., AAPL, TSLA, NVDA):", "NVDA").upper()
historical_years = st.sidebar.slider("Historical Lookback (Years):", 1, 5, 2)
prediction_days = st.sidebar.slider("Algorithmic Projection Window (Days):", 10, 365, 90)

@st.cache_data(ttl=3600)
def load_data(ticker, years):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years * 365)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
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

@st.cache_data(ttl=86400) # Cache daily to prevent heavy API pulling
def get_market_screener():
    # 100 high-volume market tickers representing a broad market subset
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
    st.error(f"No equity data found for '{search_ticker}'. Please verify the ticker symbol.")
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
# 3. TABS ARCHITECTURE
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Technical Charting", 
    "🧠 Algorithmic Forecast", 
    "📰 Sentiment Heuristics", 
    "⚖️ Top & Bottom 10",
    "🌎 Broad Market Explorer",
    "⚙️ Quantitative Engine"
])

# ------------------------------------------
# TAB 1: TECHNICAL CHARTING
# ------------------------------------------
with tab1:
    st.header(f"Historical Trajectory: {search_ticker}")
    st.write("Visualizing raw price action against standard institutional Moving Averages.")
    
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
# TAB 2: ALGORITHMIC FORECAST
# ------------------------------------------
with tab2:
    st.header("Algorithmic Trend Forecasting")
    st.write(f"Utilizing polynomial machine learning regression on {historical_years} years of market data to project {prediction_days} days ahead.")
    
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
    
    fig2.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig2, use_container_width=True)
    
    pred_change = ((future_preds[-1] - current_price) / current_price) * 100
    st.markdown(f"<div class='ai-explain'><b>Extrapolation Summary:</b> Deriving mathematical momentum from the past {historical_years} years, the regression model estimates a price shift of <b>{pred_change:+.2f}%</b> over the subsequent {prediction_days} days. <i>Note: Statistical models identify trends and momentum; they cannot account for geopolitical volatility or unexpected corporate earnings surprises.</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: SENTIMENT HEURISTICS & XAI
# ------------------------------------------
with tab3:
    st.header("Sentiment Heuristics & Explainable AI")
    st.write("Executing Natural Language Processing over real-time financial headlines to calculate market consensus.")
    
    news_items = fetch_news(search_ticker)
    
    pos_words = ['surge', 'jump', 'grow', 'beat', 'up', 'profit', 'dividend', 'buy', 'upgrade', 'bull', 'high', 'gain']
    neg_words = ['drop', 'fall', 'miss', 'down', 'loss', 'sell', 'downgrade', 'bear', 'low', 'lawsuit', 'penalty', 'plunge']
    
    if not news_items:
        st.info("No recent news found for this ticker from the primary data feed.")
    else:
        total_score = 0
        for item in news_items:
            # Dynamic dictionary parsing to handle both legacy and modern yfinance data structures
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
            explain_text += "The aggregated sentiment leans **Positive**. Lexical analysis identifies vocabulary correlated with growth, institutional upgrades, or earnings beats, which historically maps to short-term retail buying pressure."
        elif total_score < -2:
            explain_text += "The aggregated sentiment leans **Negative**. Lexical analysis identifies vocabulary correlated with drops, downgrades, or losses, suggesting short-term market anxiety or aggressive institutional selling."
        else:
            explain_text += "The aggregated sentiment is **Neutral/Mixed**. The news feed contains a balanced ratio of positive and negative drivers, indicating potential price consolidation."
            
        st.markdown(f"<div class='ai-explain'><b>Why this matters:</b> {explain_text} Algorithmic trading systems constantly parse headlines in milliseconds. Correlating human and media sentiment provides a crucial psychological context to purely numerical chart movements.</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: MARKET SCREENER (TOP & BOTTOM 10)
# ------------------------------------------
with tab4:
    st.header("Sector Performance Extremes")
    st.write("Evaluating a 100-ticker subset for trailing 1-Year returns to identify statistical outliers.")
    
    with st.spinner("Aggregating cross-market scan..."):
        screener_df = get_market_screener()
    
    if not screener_df.empty:
        colA, colB = st.columns(2)
        with colA:
            st.subheader("🔥 Top 10 Outperformers")
            top_10 = screener_df.head(10)
            for _, row in top_10.iterrows():
                st.markdown(f"<div class='metric-box'><b>{row['Ticker']}</b>: <span style='color:#0aff68'>+{row['1-Year Return (%)']:.2f}%</span></div>", unsafe_allow_html=True)
                
        with colB:
            st.subheader("🧊 Bottom 10 Underperformers")
            bottom_10 = screener_df.tail(10)
            for _, row in bottom_10.iterrows():
                color = "#ff007f" if row['1-Year Return (%)'] < 0 else "#0aff68"
                st.markdown(f"<div class='metric-box' style='border-left-color:#ff007f;'><b>{row['Ticker']}</b>: <span style='color:{color}'>{row['1-Year Return (%)']:.2f}%</span></div>", unsafe_allow_html=True)
    else:
        st.error("Market data pipeline temporarily unavailable. Please try again later.")

# ------------------------------------------
# TAB 5: BROAD MARKET EXPLORER
# ------------------------------------------
with tab5:
    st.header("Global Equities Explorer")
    st.write("Browse current prices and 1-Year trailing returns for a representative basket of 100 high-volume market tickers.")
    
    if 'screener_df' not in locals():
        with st.spinner("Fetching global metrics..."):
            screener_df = get_market_screener()
            
    if not screener_df.empty:
        display_df = screener_df.copy()
        display_df['Last Price ($)'] = display_df['Last Price ($)'].apply(lambda x: f"${x:,.2f}")
        display_df['1-Year Return (%)'] = display_df['1-Year Return (%)'].apply(lambda x: f"{x:+.2f}%")
        st.dataframe(display_df, use_container_width=True, height=600)
    else:
        st.error("Data pipeline timeout. Please refresh the module.")

# ------------------------------------------
# TAB 6: QUANTITATIVE VALUATION ENGINE
# ------------------------------------------
with tab6:
    st.header("Quantitative Valuation Engine")
    st.write("Synthesizing technical indicators and algorithmic projections into a logical valuation rating.")
    
    score = 0
    reasons = []
    
    if current_rsi < 30:
        score += 1
        reasons.append(f"The RSI is {current_rsi:.1f}. This designates the asset as technically 'Oversold', indicating it may be undervalued and positioned for a bullish rebound.")
    elif current_rsi > 70:
        score -= 1
        reasons.append(f"The RSI is {current_rsi:.1f}. This designates the asset as technically 'Overbought', indicating it may be overvalued and susceptible to a bearish correction.")
    else:
        reasons.append(f"The RSI is {current_rsi:.1f}, placing the asset in a neutral momentum zone.")
        
    if current_price > current_sma50:
        score += 1
        reasons.append(f"The current price (${current_price:.2f}) sits safely above its 50-day SMA (${current_sma50:.2f}), confirming an ongoing medium-term uptrend.")
    else:
        score -= 1
        reasons.append(f"The current price (${current_price:.2f}) has fallen below its 50-day SMA (${current_sma50:.2f}), confirming an ongoing medium-term downtrend.")
        
    if 'pred_change' in locals():
        if pred_change > 5:
            score += 1
            reasons.append(f"The ML polynomial forecast projects a statistically significant positive trajectory (+{pred_change:.1f}%) over the selected timeframe.")
        elif pred_change < -5:
            score -= 1
            reasons.append(f"The ML polynomial forecast projects a statistically significant negative trajectory ({pred_change:.1f}%) over the selected timeframe.")
        
    if score >= 2:
        verdict = "STRONG BUY"
        v_color = "#0aff68"
    elif score <= -2:
        verdict = "SELL / AVOID"
        v_color = "#ff007f"
    else:
        verdict = "HOLD / NEUTRAL"
        v_color = "#ff9900"
        
    st.markdown(f"<h1 style='text-align: center; color: {v_color}; font-size: 4rem; margin-top: 20px;'>{verdict}</h1>", unsafe_allow_html=True)
    
    st.markdown("### 🧠 Logical Synthesis Breakdown:")
    for r in reasons:
        st.markdown(f"- {r}")
        
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.caption("🚨 ACADEMIC DISCLAIMER: This application is constructed for portfolio demonstration and academic research purposes only. Algorithmic predictions carry inherent financial risk. Always perform independent due diligence before executing live market trades.")
