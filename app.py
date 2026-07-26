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
st.set_page_config(page_title="AI Stock Guide", page_icon="💡", layout="wide")

st.markdown("""
    <style>
    /* Animated Deep Space Background */
    .stApp {
        background: linear-gradient(-45deg, #070a10, #0f1422, #161f33, #090e1a);
        background-size: 400% 400%;
        animation: gradientBG 16s ease infinite;
    }
    @keyframes gradientBG { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }

    [data-testid="stSidebar"] { background: transparent !important; border-right: 1px solid rgba(255, 255, 255, 0.12) !important; }
    [data-testid="stHeader"] { background: transparent !important; }

    /* Main Glass Platform Pane */
    .block-container {
        background: rgba(13, 17, 28, 0.55); backdrop-filter: blur(16px);
        border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        padding-top: 2.5rem !important; padding-bottom: 3rem !important; margin-top: 1rem;
    }

    /* Refractive Diamonds */
    .diamond-crystal {
        position: fixed; width: 110px; height: 110px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1.5px solid rgba(255, 255, 255, 0.85); transform: rotate(45deg);
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.5), inset 0 0 15px rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(6px); z-index: -1; pointer-events: none;
    }
    .diamond-crystal::before {
        content: ''; position: absolute; top: 12%; left: 12%; right: 12%; bottom: 12%;
        border: 1px solid rgba(255, 255, 255, 0.4);
        background: linear-gradient(45deg, rgba(0, 255, 204, 0.08), rgba(188, 19, 254, 0.08));
    }
    .d1 { width: 130px; height: 130px; top: 12%; left: 3%; animation: floatDiamond1 14s infinite ease-in-out alternate; }
    .d2 { width: 200px; height: 200px; top: 55%; right: 2%; animation: floatDiamond2 20s infinite ease-in-out alternate; }
    .d3 { width: 85px; height: 85px; bottom: 8%; left: 28%; animation: floatDiamond3 16s infinite ease-in-out alternate; }

    @keyframes floatDiamond1 { 0% { transform: translateY(0px) rotate(45deg) scale(1); box-shadow: 0 0 20px rgba(255,255,255,0.4); } 100% { transform: translateY(-35px) rotate(60deg) scale(1.06); box-shadow: 0 0 35px rgba(255,255,255,0.8); } }
    @keyframes floatDiamond2 { 0% { transform: translateY(0px) rotate(45deg) scale(1); box-shadow: 0 0 25px rgba(0, 255, 204, 0.3); } 100% { transform: translateY(45px) rotate(30deg) scale(1.05); box-shadow: 0 0 45px rgba(255,255,255,0.9); } }
    @keyframes floatDiamond3 { 0% { transform: translateY(0px) rotate(45deg); box-shadow: 0 0 15px rgba(188, 19, 254, 0.3); } 100% { transform: translateY(-25px) rotate(75deg); box-shadow: 0 0 30px rgba(255,255,255,0.7); } }

    /* Clean Tabs */
    button[data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 6px 6px 0px 0px !important; color: #94a3b8 !important;
        font-weight: 600 !important; font-size: 0.85rem !important;
        padding: 10px 16px !important; margin-right: 4px !important; transition: all 0.25s ease-in-out !important;
    }
    button[data-baseweb="tab"]:hover { color: #f1f5f9 !important; background: rgba(255, 255, 255, 0.08) !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, rgba(0, 255, 204, 0.15) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
        border-top: 2px solid #00ffcc !important; border-left: 1px solid rgba(0, 255, 204, 0.3) !important;
        border-right: 1px solid rgba(0, 255, 204, 0.3) !important; color: #00ffcc !important;
    }

    /* Custom UI Cards & Educational Tooltips */
    .metric-box, .ai-explain, .dict-row, .edu-box { 
        backdrop-filter: blur(6px); border-radius: 8px; margin-bottom: 15px; padding: 16px;
        border-top: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); 
    }
    .metric-box { background: rgba(0, 255, 204, 0.03); border-left: 3px solid #00ffcc; }
    .ai-explain { background: rgba(188, 19, 254, 0.06); border-left: 3px solid #bc13fe; font-size: 0.95rem; }
    .dict-row { background: rgba(255, 255, 255, 0.02); border-left: 3px solid #4a90e2; font-size: 0.9rem; }
    .edu-box { background: rgba(255, 153, 0, 0.05); border-left: 3px solid #ff9900; }
    
    /* Educational Hover Tip */
    .help-tip { border-bottom: 1px dotted #00ffcc; cursor: help; color: #f1f5f9; font-weight: bold; }
    .help-tip:hover { color: #00ffcc; }
    </style>
    
    <div class="diamond-crystal d1"></div>
    <div class="diamond-crystal d2"></div>
    <div class="diamond-crystal d3"></div>
""", unsafe_allow_html=True)

# Title Block
st.markdown("<h1 style='letter-spacing: 1.5px; font-weight: 700;'><span style='color: #00ffcc;'>💡</span> Smart Stock Explorer</h1>", unsafe_allow_html=True)
st.write("An easy-to-use guide that uses AI to help you understand the stock market.")

# ==========================================
# 2. DYNAMIC SIDEBAR CONFIGURATION
# ==========================================
st.sidebar.markdown("<h4 style='letter-spacing: 1px; color: #cbd5e1;'>SEARCH MENU</h4>", unsafe_allow_html=True)

market_region = st.sidebar.selectbox("1. Pick a Market:", ["United States (US)", "India (NSE)", "United Kingdom (LSE)", "Cryptocurrency"], help="Which country's stock market do you want to look at?")
raw_ticker = st.sidebar.text_input("2. Enter a Stock Symbol:", "NVDA", help="A stock symbol is a short nickname for a company. Example: AAPL is Apple, NVDA is NVIDIA.").upper().strip()

search_ticker = raw_ticker
if market_region == "India (NSE)" and not raw_ticker.endswith(".NS"): search_ticker = f"{raw_ticker}.NS"
elif market_region == "United Kingdom (LSE)" and not raw_ticker.endswith(".L"): search_ticker = f"{raw_ticker}.L"
elif market_region == "Cryptocurrency" and not raw_ticker.endswith("-USD"): search_ticker = f"{raw_ticker}-USD"

historical_years = st.sidebar.slider("Look back how far? (Years):", 1, 5, 2, help="How many years of past data should the AI look at to learn the stock's habits?")
prediction_days = st.sidebar.slider("AI Forecast length (Days):", 10, 365, 90, help="How many days into the future should the AI try to guess the price trend?")

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
    equities = {
        "AAPL": "Apple Inc.", "MSFT": "Microsoft", "NVDA": "NVIDIA", "AMZN": "Amazon",
        "TSLA": "Tesla", "BRK-B": "Berkshire Hathaway", "LLY": "Eli Lilly", "JPM": "JPMorgan Chase",
        "XOM": "Exxon Mobil", "WMT": "Walmart", "PG": "Procter & Gamble"
    }
    tickers_str = " ".join(equities.keys())
    try:
        data = yf.download(tickers_str, period="5y", interval="1wk", progress=False)['Close']
        results = []
        for ticker, name in equities.items():
            if ticker in data.columns:
                series = data[ticker].dropna()
                if len(series) > 50:
                    start_price = series.iloc[0]
                    end_price = series.iloc[-1]
                    max_price = series.max()
                    
                    total_return = ((end_price - start_price) / start_price) * 100
                    max_drawdown = ((series.min() - max_price) / max_price) * 100
                    sma_52wk = series.tail(52).mean()
                    
                    status = "🟢 GOOD (Stable Growth)" if (total_return > 30 and end_price > sma_52wk) else "🔴 CAREFUL (Bumpy Ride)"
                    xai = f"Over 5 years, if you invested in this, it grew by <b>{total_return:+.1f}%</b>. Its biggest temporary drop was <b>{max_drawdown:.1f}%</b>. Currently at <b>${end_price:.2f}</b>, it is {'doing better' if end_price > sma_52wk else 'doing worse'} than its 1-year average."
                    results.append({"Company": name, "Ticker": ticker, "Status": status, "XAI": xai, "Return": total_return})
        return sorted(results, key=lambda x: x['Return'], reverse=True)
    except: return []

@st.cache_data(ttl=3600)
def get_macro_benchmarks():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    benchmarks = {"Overall Stock Market (S&P 500)": "^GSPC", "Gold (Safe Money)": "GC=F", "Bitcoin (Risky Crypto)": "BTC-USD"}
    df_bench = pd.DataFrame()
    for name, tkr in benchmarks.items():
        data = yf.download(tkr, start=start_date, end=end_date, progress=False)['Close']
        if isinstance(data, pd.Series): df_bench[name] = data
        elif not data.empty: df_bench[name] = data.iloc[:, 0]
    return df_bench

# Process main target data
with st.spinner("Downloading market data..."):
    df = load_data(search_ticker, historical_years)

if df.empty or 'Close' not in df.columns:
    st.error(f"Oops! We couldn't find data for '{search_ticker}'.")
    st.info("Tip: Make sure you selected the right country in the menu on the left.")
    st.stop()

# Indicators 
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['SMA_200'] = df['Close'].rolling(window=200).mean()
df['Vol_SMA20'] = df.get('Volume', pd.Series(0, index=df.index)).rolling(window=20).mean()
df['Price_Change_Pct'] = df['Close'].pct_change().abs() * 100

# Stealth Anomaly (Whale Tracking)
df['Stealth_Anomaly'] = np.where((df['Volume'] > 2.5 * df['Vol_SMA20']) & (df['Price_Change_Pct'] < 1.5), df['Close'], np.nan)

# RSI Calculation
delta = df['Close'].diff(1)
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

current_price = float(df['Close'].iloc[-1])
pct_change = ((float(df['Close'].iloc[-1]) - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Price:** ${current_price:,.2f}")
st.sidebar.markdown(f"**Change Today:** {pct_change:+.2f}%")

# ==========================================
# 4. TABBED INTERFACE
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Chart", 
    "🔮 AI Forecast", 
    "⭐ Top Stocks", 
    "🔗 Connections",
    "⚖️ Verdict",
    "🎓 Learn Basics"
])

# ------------------------------------------
# TAB 1: CHART & WHALES
# ------------------------------------------
with tab1:
    st.header(f"Price History for {search_ticker}")
    st.markdown("This chart shows how the stock's price has moved over time. Hover over the lines to see exact prices.")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Stock Price', line=dict(color='#00bfff')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], name='50-Day Average', line=dict(color='#0aff68', dash='dot')))
    
    anomalies_exist = df['Stealth_Anomaly'].notna().any()
    if anomalies_exist:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Stealth_Anomaly'], mode='markers', name='Big Money Activity',
            marker=dict(color='#bc13fe', size=12, symbol='diamond', line=dict(color='white', width=1))
        ))
    
    # Reduced height from 600 to 450 to make it friendlier
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), height=450, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    explain_anomaly = "Our AI scanned the trading volume. "
    if anomalies_exist:
        num_anomalies = df['Stealth_Anomaly'].count()
        explain_anomaly += f"<br><br><span style='color:#bc13fe; font-weight:bold;'>What we found:</span> We found {num_anomalies} purple diamonds on the chart. This happens when a massive amount of shares are traded, but the price doesn't move. In the stock market, this usually means <span class='help-tip' title='Wealthy investors, banks, or hedge funds buying/selling quietly.'>Big Money (Whales)</span> are quietly buying or selling large amounts behind the scenes."
    else:
        explain_anomaly += "<br><br><span style='color:#cbd5e1;'>What we found:</span> No sneaky 'Big Money' activity detected recently. The price is moving normally with regular everyday investors."
    st.markdown(f"<div class='ai-explain'><b>AI Reasoning (Behind the Scenes):</b><br>{explain_anomaly}</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: AI FORECAST
# ------------------------------------------
with tab2:
    st.header("AI Future Trend Prediction")
    st.markdown("We use math to draw a line based on the past, and stretch it into the future. It's a highly educated guess, not a guarantee!")
    
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
    fig2.add_trace(go.Scatter(x=df_model['Date'], y=df_model['Close'], name='Past Prices', line=dict(color='rgba(255,255,255,0.2)')))
    fig2.add_trace(go.Scatter(x=df_model['Date'], y=df_model['Trend'], name='Mathematical Trend', line=dict(color='#bc13fe')))
    fig2.add_trace(go.Scatter(x=future_dates, y=future_preds, name='Future Guess', line=dict(color='#0aff68', width=3)))
    
    fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig2, use_container_width=True)
    
    pred_change = ((future_preds[-1] - current_price) / current_price) * 100
    st.markdown(f"<div class='ai-explain'><b>What the AI thinks:</b> By looking at the stock's habits over the last {historical_years} years, the math expects the price to shift by <b>{pred_change:+.2f}%</b> over the next {prediction_days} days. <i>Remember: Real-world news can easily break math predictions!</i></div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: TOP STOCKS (GLOBAL DICTIONARY)
# ------------------------------------------
with tab3:
    st.header("Top Global Stocks to Know")
    st.write("A quick cheat-sheet of famous companies. We analyzed their past 5 years to tell you if they are generally safe or risky.")
    
    with st.spinner("Checking 5-year history..."):
        dict_data = get_global_dictionary()
        
    if dict_data:
        for item in dict_data:
            color = "#0aff68" if "GOOD" in item["Status"] else "#ff007f"
            html = f"""
            <div class='dict-row'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                    <h3 style='margin: 0; color: #f1f5f9;'>{item["Company"]} <span style='font-size: 0.8em; color: #94a3b8;'>({item["Ticker"]})</span></h3>
                    <div style='background: rgba(0,0,0,0.3); padding: 5px 15px; border-radius: 20px; border: 1px solid {color}; font-weight: bold; color: {color};'>{item["Status"]}</div>
                </div>
                <div style='font-size: 0.95rem; color: #cbd5e1; border-left: 2px solid rgba(255,255,255,0.1); padding-left: 10px;'>
                    <b>AI Plain English Summary:</b> {item["XAI"]}
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: CONNECTIONS (MACRO NEXUS)
# ------------------------------------------
with tab4:
    st.header("Market Connections")
    st.write("Stocks don't move alone. Let's see if your stock copies the broader market, Gold, or Bitcoin.")
    
    with st.spinner("Comparing against the world..."):
        df_bench = get_macro_benchmarks()
        
    df_asset = df.set_index('Date')['Close'].tail(252)
    df_bench = df_bench.tail(252)
    
    nexus_df = df_bench.copy()
    nexus_df[search_ticker] = df_asset
    corr_matrix = nexus_df.corr(method='pearson')
    
    if search_ticker in corr_matrix.columns:
        col1, col2, col3 = st.columns(3)
        sp_corr = corr_matrix.loc[search_ticker, "Overall Stock Market (S&P 500)"]
        gold_corr = corr_matrix.loc[search_ticker, "Gold (Safe Money)"]
        btc_corr = corr_matrix.loc[search_ticker, "Bitcoin (Risky Crypto)"]
        
        def format_corr(val):
            color = "#0aff68" if val > 0.5 else ("#ff007f" if val < -0.5 else "#cbd5e1")
            return f"<h2 style='color: {color}; margin:0;'>{val:.2f}</h2><p style='color: #94a3b8; font-size: 0.85rem;'>1.0 = Exact Copycat<br>-1.0 = Total Opposite</p>"

        with col1: st.markdown(f"<div class='metric-box'><b>Vs. Whole Market</b><br>{format_corr(sp_corr)}</div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='metric-box'><b>Vs. Gold (Safe)</b><br>{format_corr(gold_corr)}</div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div class='metric-box'><b>Vs. Bitcoin (Risky)</b><br>{format_corr(btc_corr)}</div>", unsafe_allow_html=True)
            
        st.markdown(f"""
        <div class='ai-explain'>
        <b>AI Reasoning (Behind the Scenes):</b><br>
        If your score is close to <b>1.0</b> with Bitcoin, it means your stock is very risky and jumps around like a cryptocurrency. If your score is <b>negative</b> with the overall market, it means your stock actually goes UP when the rest of the world goes DOWN!
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 5: VERDICT (QUANT VALUATION)
# ------------------------------------------
with tab5:
    st.header("Final AI Verdict")
    st.write("We put all the numbers into a blender and let the AI decide if this stock looks good right now.")
    
    score = 0
    reasons = []
    
    current_rsi = float(df['RSI'].iloc[-1]) if 'RSI' in df.columns and not pd.isna(df['RSI'].iloc[-1]) else 50.0
    current_sma50 = float(df['SMA_50'].iloc[-1]) if 'SMA_50' in df.columns and not pd.isna(df['SMA_50'].iloc[-1]) else current_price
    
    # RSI Translation
    if current_rsi < 30:
        score += 1
        reasons.append(f"The 'Speedometer' (RSI) is {current_rsi:.1f}. This is very low, meaning the stock might be 'on sale' right now (Oversold).")
    elif current_rsi > 70:
        score -= 1
        reasons.append(f"The 'Speedometer' (RSI) is {current_rsi:.1f}. This is very high, meaning people might have bought too much too fast (Overbought).")
    else:
        reasons.append(f"The 'Speedometer' (RSI) is {current_rsi:.1f}. It's cruising at a normal, healthy speed.")
        
    # SMA Translation
    if current_price > current_sma50:
        score += 1
        reasons.append(f"The current price (${current_price:.2f}) is higher than its 50-day average. This means it has good upward momentum.")
    else:
        score -= 1
        reasons.append(f"The current price (${current_price:.2f}) is lower than its 50-day average. It is currently struggling.")
        
    # Forecast Translation
    if 'pred_change' in locals():
        if pred_change > 5:
            score += 1
            reasons.append(f"Our AI math forecast thinks it will go UP by {pred_change:.1f}% soon.")
        elif pred_change < -5:
            score -= 1
            reasons.append(f"Our AI math forecast thinks it will go DOWN by {pred_change:.1f}% soon.")
        
    if score >= 2: verdict, v_color = "🟢 GOOD BUY", "#0aff68"
    elif score <= -2: verdict, v_color = "🔴 PROBABLY AVOID", "#ff007f"
    else: verdict, v_color = "🟡 JUST WATCH IT", "#ff9900"
        
    st.markdown(f"<h1 style='text-align: center; color: {v_color}; font-size: 3.5rem; margin-top: 15px;'>{verdict}</h1>", unsafe_allow_html=True)
    st.markdown("### Why did the AI say this?")
    for r in reasons: st.markdown(f"- {r}")

# ------------------------------------------
# TAB 6: LEARN BASICS (EDUCATIONAL)
# ------------------------------------------
with tab6:
    st.header("🎓 Welcome to Stock Market Kindergarten")
    st.write("Confused by finance? Don't worry. Here are the absolute basics.")
    
    st.markdown("""
    <div class='edu-box'>
    <h3>🍕 What is a "Stock"?</h3>
    Imagine a massive, successful pizza restaurant. The owner wants to build 100 more restaurants but doesn't have the money. So, they slice the company into millions of tiny pieces and sell them to regular people. <b>When you buy a stock, you are buying one tiny slice of that pizza restaurant.</b> If the restaurant makes lots of money, your slice becomes more valuable!
    </div>
    
    <div class='edu-box'>
    <h3>🐂 Bulls vs. 🐻 Bears</h3>
    You will hear these animals mentioned all the time on the news.
    <ul>
        <li><b>The Bull 🐂:</b> A bull attacks by thrusting its horns <b>UP</b> in the air. A "Bull Market" means everyone is happy and prices are going UP.</li>
        <li><b>The Bear 🐻:</b> A bear attacks by swiping its paws <b>DOWN</b>. A "Bear Market" means people are scared and prices are falling DOWN.</li>
    </ul>
    </div>
    
    <div class='edu-box'>
    <h3>🗣️ What is "Volume"?</h3>
    Volume just means <b>how many shares were traded today.</b> Imagine the stock market is a room full of people. If volume is low, people are whispering. If volume is high, everyone is screaming and running around. High volume means something big is happening!
    </div>
    
    <div class='edu-box'>
    <h3>🎢 The Golden Rule</h3>
    Never invest money you need to pay for rent or food next week. The stock market goes up over long periods of time (years), but it bounces up and down crazily from day to day. <b>Patience makes money, panic loses it.</b>
    </div>
    """, unsafe_allow_html=True)
