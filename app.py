import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

# ==========================================
# 1. INITIALIZATION & NEON UI STYLING
# ==========================================
st.set_page_config(page_title="NeonVest - Learn to Invest", page_icon="✨", layout="wide")

# Injecting Custom CSS for Glassmorphism, Neon Gradients, and Tooltips
st.markdown("""
    <style>
    /* Neon Dark Background - Matching image_48edd6.jpg */
    .stApp { 
        background: linear-gradient(135deg, #111424 0%, #1a1b3b 100%); 
        color: #e2e8f0; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }
    
    /* Hide Streamlit Branding for a cleaner look */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; 
        padding: 24px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Custom Hover Tooltip Engine */
    .hover-tooltip {
        position: relative; 
        display: inline-block;
        border-bottom: 2px dotted #22d3ee; 
        color: #22d3ee; 
        cursor: help; 
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .hover-tooltip .tooltiptext {
        visibility: hidden; 
        width: 260px; 
        background-color: rgba(15, 23, 42, 0.95);
        color: #fff; 
        text-align: left; 
        border-radius: 8px; 
        padding: 12px;
        position: absolute; 
        z-index: 50; 
        bottom: 130%; 
        left: 50%;
        margin-left: -130px; 
        opacity: 0; 
        transition: opacity 0.3s;
        border: 1px solid #334155; 
        font-size: 0.9rem; 
        font-weight: normal; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .hover-tooltip:hover .tooltiptext { 
        visibility: visible; 
        opacity: 1; 
    }
    .hover-tooltip:hover {
        color: #67e8f9;
    }
    
    /* Insight / Reasoning Box */
    .reasoning-box {
        background: rgba(34, 211, 238, 0.05); 
        border-left: 4px solid #22d3ee;
        padding: 16px; 
        border-radius: 0 8px 8px 0; 
        margin-top: 15px;
    }
    
    /* Tiny Data Credit */
    .data-credit { 
        text-align: right; 
        font-size: 10px; 
        color: rgba(255,255,255,0.4); 
        margin-top: -5px; 
        margin-bottom: 15px;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #cbd5e1;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(34, 211, 238, 0.1);
        color: #22d3ee !important;
        border-bottom: 2px solid #22d3ee;
    }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>
    <h1 style='color: #22d3ee; margin: 0;'>✨ NeonVest</h1>
    <h3 style='color: #cbd5e1; font-weight: normal; margin: 0; padding-top: 8px;'>| The friendly way to learn stocks</h3>
</div>
<p style='color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px;'>Welcome to your personal, beginner-friendly gateway to the stock market.</p>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR CONFIGURATION
# ==========================================
st.sidebar.markdown("### 🔍 Find a Company")
ticker_input = st.sidebar.text_input("Type a ticker (e.g., AAPL, TSLA)", "AAPL").upper().strip()
st.sidebar.caption("💡 Not sure what to type? Try **MSFT** for Microsoft or **AMZN** for Amazon.")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⏳ Time Travel")
history_years = st.sidebar.radio("View history for the last:", [1, 2, 3, 5], format_func=lambda x: f"{x} Year{'s' if x > 1 else ''}")

@st.cache_data(ttl=3600)
def fetch_company_data(ticker, years):
    """Fetches historical price data and basic company info."""
    try:
        stock = yf.Ticker(ticker)
        # We fetch 5y max so we always have enough data for a 200-day average calculation in the Insight tab
        df_full = stock.history(period="5y") 
        if df_full.empty:
            return None, None
            
        df_full.reset_index(inplace=True)
        info = stock.info
        
        # Filter for the requested timeframe for the chart
        cutoff_date = pd.Timestamp.now(tz=df_full['Date'].dt.tz) - pd.DateOffset(years=years)
        df_view = df_full[df_full['Date'] >= cutoff_date].copy()
        
        return df_view, df_full, info
    except Exception:
        return None, None, None

with st.spinner("Gathering market data..."):
    df_view, df_full, company_info = fetch_company_data(ticker_input, history_years)

if df_view is None or df_view.empty:
    st.error(f"Oops! We couldn't find data for '{ticker_input}'. Try typing 'AAPL' or 'MSFT' instead.")
    st.stop()

# Basic Info Extraction
company_name = company_info.get('shortName', ticker_input) if company_info else ticker_input
industry = company_info.get('industry', 'their industry') if company_info else 'their industry'
current_price = float(df_view['Close'].iloc[-1])
start_price = float(df_view['Close'].iloc[0])

# ==========================================
# 3. THE THREE BEGINNER TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🍕 Learn", "📈 History", "💡 Insight"])

# ------------------------------------------
# TAB 1: LEARN (Analogies & Tooltips)
# ------------------------------------------
with tab1:
    st.markdown(f"""
    <div class="glass-card">
        <h2 style='margin-top:0; color: #f8fafc;'>What exactly is a Stock?</h2>
        <p style='font-size: 1.1rem; line-height: 1.7; color: #cbd5e1;'>
            Imagine a massive, highly successful pizza shop. The owners want to open 10 more shops across the country, but they need money to do it. <br><br>
            So, they divide the company into millions of tiny "slices" and sell them to people like you. 
            When you buy a stock, you literally own a <span class="hover-tooltip">Share<span class="tooltiptext">A single piece of ownership in a company. You are a part-owner!</span></span> of that business. 
            If the company sells lots of pizza and becomes more popular, your slice becomes more valuable. If you want, you can sell your slice to someone else later for a profit!
        </p>
    </div>
    
    <div class="glass-card">
        <h2 style='margin-top:0; color: #f8fafc;'>About {company_name}</h2>
        <p style='font-size: 1.1rem; line-height: 1.7; color: #cbd5e1;'>
            You are looking at <b>{company_name}</b>, which operates in the {industry} sector. <br><br>
            If you buy shares in this company, you are placing a bet that they will continue to grow, sell more products, and become more successful in the future.
        </p>
    </div>
    
    <div class="glass-card">
        <h2 style='margin-top:0; color: #f8fafc;'>Hover to Learn: Market Vocabulary</h2>
        <ul style='color: #cbd5e1;'>
            <li style='margin-bottom: 15px; font-size: 1.1rem;'>
                <span class="hover-tooltip">Volatility<span class="tooltiptext">How 'jumpy' a stock price is. Think of it like a wild roller coaster vs. a calm, steady train.</span></span>: 
                Some stocks jump up and down a lot every day. Others move very slowly.
            </li>
            <li style='margin-bottom: 15px; font-size: 1.1rem;'>
                <span class="hover-tooltip">Dividend<span class="tooltiptext">A cash 'thank you' gift the company deposits directly into your account just for holding their stock.</span></span>: 
                Some mature companies pay you a little bit of cash every few months just to say thank you for being an owner.
            </li>
            <li style='margin-bottom: 15px; font-size: 1.1rem;'>
                <span class="hover-tooltip">Volume<span class="tooltiptext">The number of shares traded in a single day. High volume means lots of people are interested today!</span></span>: 
                How many people are buying and selling slices of the pizza today.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: HISTORY
# ------------------------------------------
with tab2:
    st.markdown(f"<h3 style='color: #f8fafc;'>The ups and downs over the last {history_years} year{'s' if history_years > 1 else ''}</h3>", unsafe_allow_html=True)
    
    price_diff = current_price - start_price
    pct_change = (price_diff / start_price) * 100
    direction = "grown" if price_diff >= 0 else "dropped"
    color = "#4ade80" if price_diff >= 0 else "#f472b6"
    
    st.markdown(f"""
    <p style='font-size: 1.1rem; color: #cbd5e1;'>
        If you bought one share {history_years} year{'s' if history_years > 1 else ''} ago, it would have cost you <b>${start_price:.2f}</b>. <br>
        Today, that same share is worth <b>${current_price:.2f}</b>. The price has <span style='color: {color}; font-weight: bold;'>{direction} by {abs(pct_change):.1f}%</span>.
    </p>
    """, unsafe_allow_html=True)
    
    # Compact, beginner-friendly chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_view['Date'], y=df_view['Close'], 
        mode='lines', 
        line=dict(color='#22d3ee', width=3), 
        name='Price',
        fill='tozeroy',
        fillcolor='rgba(34, 211, 238, 0.08)'
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        height=350, # Compact height
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified",
        xaxis=dict(showgrid=False, showticklabels=True), 
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickprefix="$")
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='data-credit'>Verified Market Data provided by: Yahoo Finance</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: INSIGHT (Educational Recommendation)
# ------------------------------------------
with tab3:
    st.markdown(f"<h3 style='color: #f8fafc;'>Educational Market Insight for {company_name}</h3>", unsafe_allow_html=True)
    st.write("We use simple math to figure out the 'trend' (direction) of a stock so you can make informed decisions.")
    
    # Calculate simple moving averages using the full 5-year dataset to ensure we have enough data
    df_full['50_Day_Avg'] = df_full['Close'].rolling(window=50).mean()
    df_full['200_Day_Avg'] = df_full['Close'].rolling(window=200).mean()
    
    # Get the latest values
    latest_50 = float(df_full['50_Day_Avg'].iloc[-1]) if not pd.isna(df_full['50_Day_Avg'].iloc[-1]) else current_price
    latest_200 = float(df_full['200_Day_Avg'].iloc[-1]) if not pd.isna(df_full['200_Day_Avg'].iloc[-1]) else current_price
    
    # Simple Logic Gate for Recommendation
    if current_price > latest_50 and latest_50 > latest_200:
        recommendation = "BUY 🟢"
        rec_color = "#4ade80"
        rec_desc = "The stock is in a strong upward trend. People are consistently buying it."
    elif current_price < latest_50 and latest_50 < latest_200:
        recommendation = "SELL / WAIT 🔴"
        rec_color = "#f472b6"
        rec_desc = "The stock is in a downward trend. It might be best to wait until it recovers."
    else:
        recommendation = "HOLD / CAUTIOUS 🟡"
        rec_color = "#fbbf24"
        rec_desc = "The stock is moving sideways or recovering from a drop. It's in a 'wait and see' phase."

    st.markdown(f"""
    <div class="glass-card" style="border-top: 4px solid {rec_color};">
        <h2 style='color: {rec_color}; margin-top:0; font-size: 2.5rem; text-align: center;'>{recommendation}</h2>
        <p style='font-size: 1.2rem; color: #f8fafc; text-align: center;'>{rec_desc}</p>
        
        <div class="reasoning-box">
            <h4 style='color: #22d3ee; margin-top:0; display: flex; align-items: center; gap: 8px;'>
                🔍 How we got this result (Step-by-Step):
            </h4>
            <p style='margin-bottom: 10px; color: #e2e8f0;'>To avoid guessing, investors use "Averages" to smooth out the daily roller coaster. Here is the math we ran on {ticker_input}:</p>
            <ul style='margin-bottom: 0; color: #e2e8f0; line-height: 1.8;'>
                <li><b>Step 1:</b> We calculated the average price over the last 50 days (<b>${latest_50:.2f}</b>). This shows the short-term mood.</li>
                <li><b>Step 2:</b> We calculated the average price over the last 200 days (<b>${latest_200:.2f}</b>). This shows the long-term health.</li>
                <li><b>Step 3:</b> Because the current price (${current_price:.2f}) is <b>{'higher' if current_price > latest_50 else 'lower'}</b> than the 50-day average, and the 50-day average is <b>{'higher' if latest_50 > latest_200 else 'lower'}</b> than the 200-day average, the mathematical trend points to: <b>{recommendation.split()[0]}</b>.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='data-credit'>Calculations processed locally based on historical pricing. Intended for educational purposes, not financial advice.</div>", unsafe_allow_html=True)
