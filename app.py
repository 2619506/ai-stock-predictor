import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

# ==========================================
# 1. INITIALIZATION & MATURE NEON STYLING
# ==========================================
st.set_page_config(page_title="NeonVest | Market Intelligence", page_icon="✦", layout="wide")

st.markdown("""
    <style>
    /* Neon Dark Background */
    .stApp { 
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); 
        color: #e2e8f0; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Refined Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; 
        padding: 24px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Subtle Hover Tooltip Engine */
    .hover-tooltip {
        position: relative; display: inline-block;
        border-bottom: 1px dashed #38bdf8; color: #38bdf8; 
        cursor: help; font-weight: 600; transition: all 0.2s ease;
    }
    .hover-tooltip .tooltiptext {
        visibility: hidden; width: 280px; 
        background-color: rgba(15, 23, 42, 0.98); color: #fff; 
        text-align: left; border-radius: 6px; padding: 14px;
        position: absolute; z-index: 50; bottom: 130%; left: 50%;
        margin-left: -140px; opacity: 0; transition: opacity 0.3s;
        border: 1px solid #334155; font-size: 0.9rem; font-weight: normal; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); line-height: 1.5;
    }
    .hover-tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
    .hover-tooltip:hover { color: #7dd3fc; }
    
    /* Insight / Reasoning Box */
    .reasoning-box {
        background: rgba(56, 189, 248, 0.05); 
        border-left: 3px solid #38bdf8;
        padding: 16px; border-radius: 0 6px 6px 0; margin-top: 15px;
    }
    
    .news-link { color: #38bdf8; text-decoration: none; font-weight: 500; }
    .news-link:hover { text-decoration: underline; color: #7dd3fc; }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: rgba(255, 255, 255, 0.03);
        border-radius: 6px 6px 0px 0px; padding: 10px 20px; color: #cbd5e1; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border-bottom: 2px solid #38bdf8;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>
    <h1 style='color: #38bdf8; margin: 0;'>✦ NeonVest</h1>
    <h3 style='color: #94a3b8; font-weight: normal; margin: 0; padding-top: 8px;'>| Market Intelligence</h3>
</div>
<p style='color: #64748b; font-size: 1.1rem; margin-bottom: 30px;'>A mature, simplified approach to understanding global equities.</p>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA PIPELINE & SIDEBAR
# ==========================================
st.sidebar.markdown("### ❖ Asset Locator")
ticker_input = st.sidebar.text_input("Enter Ticker (e.g., AAPL, GOOGL)", "AAPL").upper().strip()

st.sidebar.markdown("---")
st.sidebar.markdown("### ◷ Time Horizon")
history_years = st.sidebar.radio("Analyze data for the last:", [1, 2, 3, 5], format_func=lambda x: f"{x} Year{'s' if x > 1 else ''}")

def format_large_number(num):
    if num is None: return "N/A"
    if num >= 1e12: return f"${num/1e12:.2f} Trillion"
    if num >= 1e9: return f"${num/1e9:.2f} Billion"
    if num >= 1e6: return f"${num/1e6:.2f} Million"
    return f"${num}"

@st.cache_data(ttl=3600)
def fetch_company_data(ticker, years):
    try:
        stock = yf.Ticker(ticker)
        df_full = stock.history(period="5y") 
        
        # FIX FOR NaN BUG: Drop any rows where closing price is missing
        df_full = df_full.dropna(subset=['Close'])
        
        if df_full.empty: return None, None, None, None
            
        df_full.reset_index(inplace=True)
        info = stock.info
        news = stock.news[:3] # Get top 3 news items
        
        cutoff_date = pd.Timestamp.now(tz=df_full['Date'].dt.tz) - pd.DateOffset(years=years)
        df_view = df_full[df_full['Date'] >= cutoff_date].copy()
        
        return df_view, df_full, info, news
    except Exception:
        return None, None, None, None

with st.spinner("Synchronizing market data..."):
    df_view, df_full, info, news = fetch_company_data(ticker_input, history_years)

if df_view is None or df_view.empty:
    st.error(f"Asset '{ticker_input}' could not be located. Please verify the ticker symbol.")
    st.stop()

company_name = info.get('shortName', ticker_input) if info else ticker_input
current_price = float(df_view['Close'].iloc[-1])
start_price = float(df_view['Close'].iloc[0])

# ==========================================
# 3. MATURE EDUCATIONAL TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏛️ Learn & Discover", "📊 Historical Trajectory", "⟡ Strategic Insight"])

# ------------------------------------------
# TAB 1: LEARN (Comprehensive & Mature)
# ------------------------------------------
with tab1:
    summary = info.get('longBusinessSummary', 'Detailed business summary is not available for this asset.')
    sector = info.get('sector', 'Unknown Sector')
    mcap = format_large_number(info.get('marketCap'))
    target_price = info.get('targetMeanPrice', 'N/A')
    
    st.markdown(f"""
    <div class="glass-card">
        <h3 style='margin-top:0; color: #f1f5f9;'>The Core Concept: What is Equity?</h3>
        <p style='font-size: 1.05rem; line-height: 1.7; color: #cbd5e1;'>
            When you purchase a <span class="hover-tooltip">Stock<span class="tooltiptext">Also known as 'equity' or 'shares'. It represents a fraction of ownership in a corporation.</span></span>, you are not just buying a ticker on a screen—you are acquiring actual fractional ownership in a living, breathing business. 
            If the company innovates, increases revenue, and expands, the underlying value of the business grows, making your fraction more valuable. 
        </p>
    </div>
    
    <div class="glass-card">
        <h3 style='margin-top:0; color: #38bdf8;'>Corporate Profile: {company_name}</h3>
        <p style='color: #94a3b8; font-size: 0.95rem;'><b>Sector:</b> {sector} &nbsp;|&nbsp; <b>Market Valuation:</b> {mcap}</p>
        <p style='font-size: 1.05rem; line-height: 1.7; color: #cbd5e1;'>{summary}</p>
        
        <h4 style='color: #f1f5f9; margin-top: 20px;'>Future Outlook & Analyst Consensus</h4>
        <p style='font-size: 1.05rem; color: #cbd5e1;'>
            While the current price is <b>${current_price:.2f}</b>, Wall Street analysts have a consensus future price target of <b>${target_price if target_price != 'N/A' else 'Unavailable'}</b> for the coming year. 
            <i>(Note: Analyst targets are estimates, not guarantees.)</i>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # News Section
    st.markdown("<h3 style='color: #f1f5f9; margin-top: 30px;'>📰 Real-Time Market News</h3>", unsafe_allow_html=True)
    if news:
        for item in news:
            title = item.get('title', 'Market Update')
            publisher = item.get('publisher', 'Financial Press')
            link = item.get('link', '#')
            # Handle Yahoo Finance API timestamp formatting
            try:
                date = datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%B %d, %Y')
            except:
                date = "Recent"
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.02); padding: 15px; border-radius: 8px; border-left: 2px solid #38bdf8; margin-bottom: 10px;'>
                <a href="{link}" target="_blank" class="news-link">{title}</a>
                <div style='color: #64748b; font-size: 0.85rem; margin-top: 5px;'>{publisher} • {date}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No recent news articles found for this asset.")

    st.markdown("""
    <div class="glass-card" style="margin-top: 30px;">
        <h3 style='margin-top:0; color: #f1f5f9;'>Market Vocabulary</h3>
        <ul style='color: #cbd5e1; line-height: 2;'>
            <li><span class="hover-tooltip">Market Capitalization<span class="tooltiptext">The total dollar market value of a company's outstanding shares. Calculated by multiplying the stock price by total shares.</span></span>: The total size and value of the company.</li>
            <li><span class="hover-tooltip">Dividend Yield<span class="tooltiptext">A financial ratio that shows how much a company pays out in dividends each year relative to its stock price.</span></span>: A percentage of profits distributed back to the shareholders as cash.</li>
            <li><span class="hover-tooltip">Bull vs. Bear Market<span class="tooltiptext">Bull = Rising prices and optimism. Bear = Falling prices (usually 20% or more) and pessimism.</span></span>: Terms used to describe the overall trend of the market (Optimistic vs. Pessimistic).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: HISTORY (Bug-Free)
# ------------------------------------------
with tab2:
    st.markdown(f"<h3 style='color: #f8fafc;'>Historical Trajectory ({history_years} Year{'s' if history_years > 1 else ''})</h3>", unsafe_allow_html=True)
    
    price_diff = current_price - start_price
    pct_change = (price_diff / start_price) * 100
    direction = "appreciated" if price_diff >= 0 else "depreciated"
    color = "#4ade80" if price_diff >= 0 else "#f43f5e"
    
    st.markdown(f"""
    <p style='font-size: 1.1rem; color: #cbd5e1;'>
        An initial position taken {history_years} year{'s' if history_years > 1 else ''} ago would have been acquired at <b>${start_price:.2f}</b>. <br>
        Today, that position is valued at <b>${current_price:.2f}</b>. The asset has <span style='color: {color}; font-weight: bold;'>{direction} by {abs(pct_change):.2f}%</span> over this period.
    </p>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_view['Date'], y=df_view['Close'], 
        mode='lines', line=dict(color='#38bdf8', width=2.5), 
        name='Price', fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.05)'
    ))

    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=400, margin=dict(l=0, r=0, t=10, b=0), hovermode="x unified",
        xaxis=dict(showgrid=False, showticklabels=True), 
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickprefix="$")
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='data-credit'>Market Data reliably sourced via Yahoo Finance API</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: INSIGHT (Pure HTML Fix)
# ------------------------------------------
with tab3:
    st.markdown(f"<h3 style='color: #f8fafc;'>Analytical Outlook for {company_name}</h3>", unsafe_allow_html=True)
    st.write("We utilize standard mathematical averages to filter out daily noise and identify the true market trend.")
    
    # Calculate averages and handle NaN
    df_full['50_Day_Avg'] = df_full['Close'].rolling(window=50).mean()
    df_full['200_Day_Avg'] = df_full['Close'].rolling(window=200).mean()
    
    latest_50 = float(df_full['50_Day_Avg'].dropna().iloc[-1]) if not df_full['50_Day_Avg'].dropna().empty else current_price
    latest_200 = float(df_full['200_Day_Avg'].dropna().iloc[-1]) if not df_full['200_Day_Avg'].dropna().empty else current_price
    
    if current_price > latest_50 and latest_50 > latest_200:
        recommendation = "ACCUMULATE / BUY"
        rec_color = "#4ade80"
        rec_desc = "The asset is exhibiting strong upward momentum. Institutional and retail accumulation is prevalent."
    elif current_price < latest_50 and latest_50 < latest_200:
        recommendation = "AVOID / SELL"
        rec_color = "#f43f5e"
        rec_desc = "The asset is in a downward phase. Market sentiment is currently negative."
    else:
        recommendation = "HOLD / MONITOR"
        rec_color = "#fbbf24"
        rec_desc = "The asset is consolidating or recovering. A clear directional trend has not yet established."

    # Completely rewritten in pure HTML to prevent Streamlit Markdown parsing errors
    st.markdown(f"""
    <div class="glass-card" style="border-top: 4px solid {rec_color};">
        <h2 style='color: {rec_color}; margin-top:0; font-size: 2.2rem; text-align: center; letter-spacing: 1px;'>{recommendation}</h2>
        <p style='font-size: 1.1rem; color: #f8fafc; text-align: center; margin-bottom: 25px;'>{rec_desc}</p>
        
        <div class="reasoning-box">
            <h4 style='color: #38bdf8; margin-top:0; display: flex; align-items: center; gap: 8px;'>
                ⟡ Analytical Breakdown
            </h4>
            <p style='margin-bottom: 15px; color: #e2e8f0;'>By tracking historical moving averages, we can map the current market sentiment mathematically, avoiding emotional decisions:</p>
            <ul style='margin-bottom: 0; color: #e2e8f0; line-height: 1.8;'>
                <li><b>Step 1:</b> The 50-day average is <b>${latest_50:.2f}</b>. This line represents the short-term mood of the market.</li>
                <li><b>Step 2:</b> The 200-day average is <b>${latest_200:.2f}</b>. This line represents the long-term, foundational health of the asset.</li>
                <li><b>Step 3:</b> Because the current price (<b>${current_price:.2f}</b>) is <b>{'higher' if current_price > latest_50 else 'lower'}</b> than the 50-day average, and the 50-day average is <b>{'higher' if latest_50 > latest_200 else 'lower'}</b> than the 200-day average, the mathematical logic points strictly to: <b>{recommendation.split(' / ')[0]}</b>.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='data-credit'>Calculations processed locally based on standard quantitative metrics. Educational purposes only.</div>", unsafe_allow_html=True)
