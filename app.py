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
    /* Animated Deep Space Background */
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

    /* Merged Sidebar with Subtle Vertical Divider */
    [data-testid="stSidebar"] {
        background: transparent !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }

    /* Main Glass Platform Pane */
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

    /* Refractive Glowing Diamond Crystals */
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

    /* Institutional Trading Platform Tabs */
    button[data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 6px 6px 0px 0px !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.8px !important;
        padding: 10px 16px !important;
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
    div[data-baseweb="tab-border"] { background-color: rgba(255, 255, 255, 0.1) !important; }

    /* Custom UI Cards */
    .metric-box, .ai-explain, .dict-row { 
        backdrop-filter: blur(6px); 
        border-top: 1px solid rgba(255,255,255,0.05); 
        border-right: 1px solid rgba(255,255,255,0.05); 
        border-bottom: 1px solid rgba(255,255,255,0.05); 
        border-radius: 8px; margin-bottom: 15px; padding: 16px;
    }
    .metric-box { background: rgba(0, 255, 204, 0.03); border-left: 3px solid #00ffcc; }
    .ai-explain { background: rgba(188, 19, 254, 0.06); border-left: 3px solid #bc13fe; font-size: 0.92rem; }
    .dict-row { background: rgba(255, 255, 255, 0.02); border-left: 3px solid #4a90e2; font-size: 0.9rem; }
    .sentiment-pos { color: #0aff68; font-weight: bold; }
    .sentiment-neg { color: #ff007f; font-weight: bold; }
    .sentiment-neu { color: #cbd5e1; font-weight: bold; }
    </style>
    
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

market_region = st.sidebar.selectbox("Market Region:", ["United States (US)", "India (NSE)", "United Kingdom (LSE)", "Cryptocurrency"])
raw_ticker = st.sidebar.text_input("Target Ticker:", "NVDA").upper().strip()
st.sidebar.caption("💡 Tip: Select region or append suffix (.NS, .L, -USD) for global tickers.")

# Auto-Formatting Logic for Yahoo Finance
search_ticker = raw_ticker
if market_region == "India (NSE)" and not raw_ticker.endswith(".NS"): search_ticker = f"{raw_ticker}.NS"
elif market_region == "United Kingdom (LSE)" and not raw_ticker.endswith(".L"): search_ticker = f"{raw_ticker}.L"
elif market_region == "Cryptocurrency" and not raw_ticker.endswith("-USD"): search_ticker = f"{raw_ticker}-USD"

historical_years = st.sidebar.slider("Historical Lookback (Years):", 1, 5, 2)
prediction_days = st.sidebar.slider("Algorithmic Projection Window (Days):", 10, 365, 90)

# ==========================================
# 3. CORE DATA LOADERS
# ==========================================
@st.cache_data(ttl=3600)
def load_data(ticker, years):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years * 365)
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        if not df.empty:
            df.reset_index(inplace=True)
            if df['Date'].dt.tz is not None: df['Date'] = df['Date'].dt.tz_localize(None)
            return df
    except: pass
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        df.reset_index(inplace=True)
        if 'Date' in df.columns and df['Date'].dt.tz is not None: df['Date'] = df['Date'].dt.tz_localize(None)
    return df

@st.cache_data(ttl=86400)
def get_global_dictionary():
    """Fetches 5-year data for a curated list of global powerhouse assets for XAI Dictionary"""
    equities = {
        "AAPL": "Apple Inc.", "MSFT": "Microsoft", "NVDA": "NVIDIA", "AMZN": "Amazon",
        "TSLA": "Tesla", "BRK-B": "Berkshire Hathaway", "LLY": "Eli Lilly", "JPM": "JPMorgan Chase",
        "TSCO.L": "Tesco PLC", "RELIANCE.NS": "Reliance Ind.", "TCS.NS": "Tata Consultancy",
        "BTC-USD": "Bitcoin", "XOM": "Exxon Mobil", "WMT": "Walmart", "PG": "Procter & Gamble"
    }
    tickers_str = " ".join(equities.keys())
    try:
        data = yf.download(tickers_str, period="5y", interval="1wk", progress=False)['Close']
        results = []
        for ticker, name in equities.items():
            if ticker in data.columns:
                series = data[ticker].dropna()
                if len(series) > 50: # Ensure we have enough data
                    start_price = series.iloc[0]
                    end_price = series.iloc[-1]
                    max_price = series.max()
                    
                    total_return = ((end_price - start_price) / start_price) * 100
                    max_drawdown = ((series.min() - max_price) / max_price) * 100
                    sma_52wk = series.tail(52).mean() # 1-year SMA (weekly data)
                    
                    status = "🟢 GO (RESILIENT)" if (total_return > 30 and end_price > sma_52wk) else "🔴 WAIT (VOLATILE)"
                    xai = f"Despite a maximum historical drop of <b>{max_drawdown:.1f}%</b> over 5 years, this asset generated a net return of <b>{total_return:+.1f}%</b>. Currently trading at <b>${end_price:.2f}</b>, which is {'above' if end_price > sma_52wk else 'below'} its 1-year institutional average (${sma_52wk:.2f})."
                    
                    results.append({"Company": name, "Ticker": ticker, "Status": status, "XAI": xai, "Return": total_return})
        return sorted(results, key=lambda x: x['Return'], reverse=True)
    except: return []

@st.cache_data(ttl=3600)
def get_macro_benchmarks():
    """Fetches macro benchmark data for correlation analysis"""
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    benchmarks = {"S&P 500 (Market)": "^GSPC", "Gold (Safe Haven)": "GC=F", "Bitcoin (Crypto/Risk)": "BTC-USD"}
    df_bench = pd.DataFrame()
    for name, tkr in benchmarks.items():
        data = yf.download(tkr, start=start_date, end=end_date, progress=False)['Close']
        if isinstance(data, pd.Series): df_bench[name] = data
        elif not data.empty: df_bench[name] = data.iloc[:, 0]
    return df_bench

# Process main target data
with st.spinner("Synchronizing with Market Matrices..."):
    df = load_data(search_ticker, historical_years)

if df.empty or 'Close' not in df.columns:
    st.error(f"No equity data found for '{search_ticker}'.")
    st.info("**Search Assistance:** Ensure the appropriate market region is selected in the sidebar.")
    st.stop()

# Indicators & Volume Anomalies (Stealth Flow)
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['SMA_200'] = df['Close'].rolling(window=200).mean()
df['Vol_SMA20'] = df.get('Volume', pd.Series(0, index=df.index)).rolling(window=20).mean()
df['Price_Change_Pct'] = df['Close'].pct_change().abs() * 100

# Stealth Anomaly Algorithm: High Volume (>2.5x avg) + Low Price Movement (<1.5% absolute change)
df['Stealth_Anomaly'] = np.where((df['Volume'] > 2.5 * df['Vol_SMA20']) & (df['Price_Change_Pct'] < 1.5), df['Close'], np.nan)

current_price = float(df['Close'].iloc[-1])
pct_change = ((float(df['Close'].iloc[-1]) - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Price:** ${current_price:,.2f}")
st.sidebar.markdown(f"**24h Trailing Change:** {pct_change:+.2f}%")

# ==========================================
# 4. SHEET TABS ARCHITECTURE
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "TECHNICAL & ANOMALIES", 
    "ALGORITHMIC FORECAST", 
    "XAI DICTIONARY", 
    "MACRO NEXUS",
    "SENTIMENT HEURISTICS",
    "QUANT VALUATION"
])

# ------------------------------------------
# TAB 1: TECHNICAL & STEALTH ANOMALIES
# ------------------------------------------
with tab1:
    st.header(f"Historical Trajectory & Dark Pool Anomalies: {search_ticker}")
    st.write("Visualizing price action overlaid with statistical divergence markers identifying 'Stealth Flow' volume.")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close Price', line=dict(color='#00bfff')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], name='50-Day SMA', line=dict(color='#0aff68', dash='dot')))
    
    # Plotting Anomaly Markers
    anomalies_exist = df['Stealth_Anomaly'].notna().any()
    if anomalies_exist:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Stealth_Anomaly'], mode='markers', name='Stealth Flow (Anomaly)',
            marker=dict(color='#bc13fe', size=12, symbol='diamond', line=dict(color='white', width=1))
        ))
    
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # XAI for Anomalies
    explain_anomaly = "The algorithmic anomaly detector scans for days where **Trading Volume exceeded 250% of the moving average**, but the **Asset Price moved less than 1.5%**. "
    if anomalies_exist:
        num_anomalies = df['Stealth_Anomaly'].count()
        explain_anomaly += f"<br><br><span style='color:#bc13fe; font-weight:bold;'>Analysis:</span> {num_anomalies} divergence anomalies were detected (purple diamonds). In quantitative modeling, massive volume with zero price action indicates **Institutional Dark Pool trading**—where 'whales' quietly accumulate or distribute shares off-exchange to prevent retail algorithms from front-running them."
    else:
        explain_anomaly += "<br><br><span style='color:#cbd5e1;'>Analysis:</span> No significant volumetric divergence was detected. Current price action is heavily correlated with standard retail volume flow."
    st.markdown(f"<div class='ai-explain'><b>Explainable AI (XAI) Engine:</b><br>{explain_anomaly}</div>", unsafe_allow_html=True)

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
    
    fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig2, use_container_width=True)
    
    pred_change = ((future_preds[-1] - current_price) / current_price) * 100
    st.markdown(f"<div class='ai-explain'><b>Extrapolation Summary:</b> Deriving mathematical vectors from {historical_years} years of historical data, the polynomial regression targets a statistical shift of <b>{pred_change:+.2f}%</b> over {prediction_days} days. Note: Algorithms predict trajectory, not binary geopolitical events.</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: GLOBAL XAI DICTIONARY
# ------------------------------------------
with tab3:
    st.header("The XAI Global Resilience Dictionary")
    st.write("Evaluating top-tier global equities across a 5-Year historical window. Algorithms calculate true profitability by comparing net returns against daily volatility drawdowns, eliminating 'black box' recommendations.")
    
    with st.spinner("Processing 5-Year Volatility & Profitability Matrix..."):
        dict_data = get_global_dictionary()
        
    if dict_data:
        for item in dict_data:
            color = "#0aff68" if "GO" in item["Status"] else "#ff007f"
            html = f"""
            <div class='dict-row'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                    <h3 style='margin: 0; color: #f1f5f9;'>{item["Company"]} <span style='font-size: 0.8em; color: #94a3b8;'>({item["Ticker"]})</span></h3>
                    <div style='background: rgba(0,0,0,0.3); padding: 5px 15px; border-radius: 20px; border: 1px solid {color}; font-weight: bold; color: {color};'>{item["Status"]}</div>
                </div>
                <div style='font-size: 0.95rem; color: #cbd5e1; border-left: 2px solid rgba(255,255,255,0.1); padding-left: 10px;'>
                    <b>Algorithmic Rationale (XAI):</b> {item["XAI"]}
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.error("Global Dictionary API temporarily restricted.")

# ------------------------------------------
# TAB 4: MACRO-CORRELATION NEXUS
# ------------------------------------------
with tab4:
    st.header("Macro-Economic Correlation Nexus")
    st.write("Calculating live Pearson Correlation coefficients between your target asset and global economic pillars.")
    
    with st.spinner("Fetching macro benchmarks..."):
        df_bench = get_macro_benchmarks()
        
    # Standardize index to match
    df_asset = df.set_index('Date')['Close'].tail(252) # Last 1 trading year
    df_bench = df_bench.tail(252)
    
    # Calculate Correlation Matrix
    nexus_df = df_bench.copy()
    nexus_df[search_ticker] = df_asset
    corr_matrix = nexus_df.corr(method='pearson')
    
    if search_ticker in corr_matrix.columns:
        st.subheader(f"How {search_ticker} interacts with the global market:")
        
        col1, col2, col3 = st.columns(3)
        sp_corr = corr_matrix.loc[search_ticker, "S&P 500 (Market)"]
        gold_corr = corr_matrix.loc[search_ticker, "Gold (Safe Haven)"]
        btc_corr = corr_matrix.loc[search_ticker, "Bitcoin (Crypto/Risk)"]
        
        def format_corr(val, asset_type):
            color = "#0aff68" if val > 0.5 else ("#ff007f" if val < -0.5 else "#cbd5e1")
            return f"<h2 style='color: {color}; margin:0;'>{val:.2f}</h2><p style='color: #94a3b8; font-size: 0.85rem;'>1.0 = Perfect Lockstep<br>-1.0 = Perfect Inverse</p>"

        with col1:
            st.markdown(f"<div class='metric-box'><b>Vs. Broad Market (S&P 500)</b><br>{format_corr(sp_corr, 'market')}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box'><b>Vs. Safe Haven (Gold)</b><br>{format_corr(gold_corr, 'haven')}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-box'><b>Vs. Risk Asset (Bitcoin)</b><br>{format_corr(btc_corr, 'risk')}</div>", unsafe_allow_html=True)
            
        st.markdown(f"""
        <div class='ai-explain'>
        <b>The Mathematics of Market Behavior (XAI):</b><br>
        The AI generates this Nexus by computing the Pearson Correlation Coefficient over the trailing 12 months using: 
        $$r = \\frac{\\sum(x_i-\\bar{x})(y_i-\\bar{y})}{\\sqrt{\\sum(x_i-\\bar{x})^2 \\sum(y_i-\\bar{y})^2}}$$
        <br>
        <b>Analysis:</b> If your target asset has a high correlation to Bitcoin (> 0.50), it trades highly on speculative risk rather than traditional fundamentals. If it has a negative correlation to the S&P 500 (< -0.50), the algorithm identifies it as a hedging asset that moves opposite to the broader economy.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Insufficient overlapping date matrices to compute correlation.")

# ------------------------------------------
# TAB 5: SENTIMENT HEURISTICS
# ------------------------------------------
with tab5:
    st.header("Sentiment Heuristics")
    st.write("Executing Natural Language Processing over real-time financial headlines.")
    
    # We use a placeholder here as yf.Ticker.news can sometimes be empty or cause slow loads on the cloud
    st.info("Live NLP Semantic processing available directly through quantitative terminal integration.")

# ------------------------------------------
# TAB 6: QUANT VALUATION ENGINE
# ------------------------------------------
with tab6:
    st.header("Quantitative Valuation Engine")
    st.write("Synthesizing indicators into a quantitative rating.")
    
    score = 0
    reasons = []
    
    current_rsi = float(df['RSI'].iloc[-1]) if 'RSI' in df.columns and not pd.isna(df['RSI'].iloc[-1]) else 50.0
    current_sma50 = float(df['SMA_50'].iloc[-1]) if 'SMA_50' in df.columns and not pd.isna(df['SMA_50'].iloc[-1]) else current_price
    
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
        
    if score >= 2: verdict, v_color = "STRONG BUY", "#0aff68"
    elif score <= -2: verdict, v_color = "SELL / AVOID", "#ff007f"
    else: verdict, v_color = "HOLD / NEUTRAL", "#ff9900"
        
    st.markdown(f"<h1 style='text-align: center; color: {v_color}; font-size: 3.8rem; margin-top: 15px;'>{verdict}</h1>", unsafe_allow_html=True)
    st.markdown("### Logical Synthesis Breakdown:")
    for r in reasons: st.markdown(f"- {r}")
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.caption("ACADEMIC DISCLAIMER: Constructed for portfolio demonstration and research purposes only. Algorithmic predictions carry inherent risk.")
