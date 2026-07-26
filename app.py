import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

# ==========================================
# 1. INITIALIZATION & COMPACT NEON STYLING
# ==========================================
st.set_page_config(page_title="SmarVest | Market Intelligence", page_icon="✦", layout="wide")

st.markdown("""
    <style>
    /* Remove vast top padding above header */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 95% !important;
    }

    /* Neon Dark Background */
    .stApp { 
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); 
        color: #e2e8f0; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Compact Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px; 
        padding: 16px; 
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Scrollable Box for Long Summaries */
    .scrollable-text {
        max-height: 110px;
        overflow-y: auto;
        padding-right: 8px;
        font-size: 0.85rem;
        line-height: 1.5;
        color: #cbd5e1;
        margin-bottom: 8px;
    }
    .scrollable-text::-webkit-scrollbar { width: 5px; }
    .scrollable-text::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
    .scrollable-text::-webkit-scrollbar-thumb { background: #38bdf8; border-radius: 4px; }
    
    /* Hover Tooltip Engine */
    .hover-tooltip {
        position: relative; display: inline-block;
        border-bottom: 1px dashed #38bdf8; color: #38bdf8; 
        cursor: help; font-weight: 600; transition: all 0.2s ease;
    }
    .hover-tooltip .tooltiptext {
        visibility: hidden; width: 240px; 
        background-color: rgba(15, 23, 42, 0.98); color: #fff; 
        text-align: left; border-radius: 6px; padding: 10px;
        position: absolute; z-index: 50; bottom: 130%; left: 50%;
        margin-left: -120px; opacity: 0; transition: opacity 0.3s;
        border: 1px solid #334155; font-size: 0.8rem; font-weight: normal; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); line-height: 1.4;
    }
    .hover-tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
    .hover-tooltip:hover { color: #7dd3fc; }
    
    /* Insight / Reasoning Box */
    .reasoning-box {
        background: rgba(56, 189, 248, 0.05); 
        border-left: 3px solid #38bdf8;
        padding: 12px; border-radius: 0 6px 6px 0; margin-top: 10px;
    }
    
    .news-link { color: #38bdf8; text-decoration: none; font-weight: 600; font-size: 0.92rem; }
    .news-link:hover { text-decoration: underline; color: #7dd3fc; }

    /* Compact Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        height: 42px; background-color: rgba(255, 255, 255, 0.03);
        border-radius: 6px 6px 0px 0px; padding: 6px 18px; color: #cbd5e1; font-weight: 600; font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border-bottom: 2px solid #38bdf8;
    }

    /* Expander Header Styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 6px !important;
        color: #38bdf8 !important;
        font-size: 0.88rem !important;
        padding: 8px 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title Header (Pulled Up)
st.markdown("""<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 2px;'>
<h2 style='color: #38bdf8; margin: 0;'>✦ SmarVest</h2>
<h4 style='color: #94a3b8; font-weight: normal; margin: 0; padding-top: 4px;'>| Market Intelligence</h4>
</div>
<p style='color: #64748b; font-size: 0.88rem; margin-bottom: 10px;'>A mature, simplified approach to understanding global equities.</p>""", unsafe_allow_html=True)

# ==========================================
# 2. ABOUT THE PROJECT (Compact)
# ==========================================
with st.expander("ℹ️ About This Project: Purpose & Architecture", expanded=False):
    st.markdown("""<div style="line-height: 1.5; color: #cbd5e1; font-size: 0.85rem; padding: 4px;">
<h5 style="color: #38bdf8; margin-top: 0; margin-bottom: 4px;">✦ Platform Overview</h5>
<p style="margin-bottom: 8px;"><b>SmarVest</b> translates complex quantitative market telemetry into simple, accessible, and actionable concepts.</p>
<h5 style="color: #38bdf8; margin-top: 0; margin-bottom: 4px;">💡 Motivation & Design Philosophy</h5>
<p style="margin-bottom: 8px;">Built on the principle of <b>Explainable Intelligence</b>—ensuring every insight is backed by transparent, step-by-step mathematical reasoning to build user trust instead of relying on opaque predictions.</p>
<h5 style="color: #38bdf8; margin-top: 0; margin-bottom: 4px;">🧠 Applied Quantitative Logic</h5>
<ul style="padding-left: 15px; margin-bottom: 0;">
<li><b>Feature Engineering:</b> Executes rolling transformations over historical time-series (50/200-day Averages) to extract momentum and reduce noise.</li>
<li><b>Explainable Logic:</b> Uses deterministic logic structures for directional signals (<i>Accumulate, Hold, Avoid</i>) paired with clear breakdowns.</li>
<li><b>Resilient ETL Pipeline:</b> Automated caching handles real-time retrieval, cleans missing entries, and dynamically processes API payloads.</li>
<li><b>Context Synthesis:</b> Integrates news sentiment and Wall Street targets to ground math in real-world business realities.</li>
</ul>
</div>""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS & DATA PIPELINE
# ==========================================
st.sidebar.markdown("### ❖ Find a Stock")
ticker_input = st.sidebar.text_input("Type a Ticker (e.g., AAPL, GOOGL)", "AAPL").upper().strip()

st.sidebar.markdown("---")
st.sidebar.markdown("### ◷ Timeframe")
history_years = st.sidebar.radio("View history for the last:", [1, 2, 3, 5], format_func=lambda x: f"{x} Year{'s' if x > 1 else ''}")

def format_large_number(num):
    if num is None: return "N/A"
    if num >= 1e12: return f"${num/1e12:.2f} Trillion"
    if num >= 1e9: return f"${num/1e9:.2f} Billion"
    if num >= 1e6: return f"${num/1e6:.2f} Million"
    return f"${num}"

def analyze_vibe(text):
    """User-friendly news vibe check."""
    if not text: return "Calm 🟡", "#fbbf24"
    text = text.lower()
    
    pos_words = ['surge', 'jump', 'beat', 'top', 'up', 'rally', 'gain', 'growth', 'dividend', 'buy', 'bullish', 'higher', 'strong', 'profit', 'soar', 'record', 'outperform']
    neg_words = ['drop', 'fall', 'miss', 'down', 'plunge', 'sell', 'bearish', 'lower', 'weak', 'loss', 'lawsuit', 'penalty', 'slow', 'crash', 'downgrade', 'underperform']
    
    pos_score = sum(1 for word in pos_words if word in text)
    neg_score = sum(1 for word in neg_words if word in text)
    
    if pos_score > neg_score: return "Upbeat 🟢", "#4ade80"
    elif neg_score > pos_score: return "Downbeat 🔴", "#f43f5e"
    else: return "Calm 🟡", "#fbbf24"

@st.cache_data(ttl=3600)
def fetch_company_data(ticker, years):
    try:
        stock = yf.Ticker(ticker)
        df_full = stock.history(period="5y").dropna(subset=['Close'])
        
        if df_full.empty: return None, None, None, None
            
        df_full.reset_index(inplace=True)
        info = stock.info
        news = stock.news[:4] if stock.news else []
        
        cutoff_date = pd.Timestamp.now(tz=df_full['Date'].dt.tz) - pd.DateOffset(years=years)
        df_view = df_full[df_full['Date'] >= cutoff_date].copy()
        
        return df_view, df_full, info, news
    except Exception:
        return None, None, None, None

with st.spinner("Fetching market data..."):
    df_view, df_full, info, news = fetch_company_data(ticker_input, history_years)

if df_view is None or df_view.empty:
    st.error(f"Stock '{ticker_input}' could not be found. Please double check the ticker symbol.")
    st.stop()

company_name = info.get('shortName', ticker_input) if info else ticker_input
current_price = float(df_view['Close'].iloc[-1])
start_price = float(df_view['Close'].iloc[0])

# ==========================================
# 4. TAB ARCHITECTURE WITH MATCHING ICONS
# ==========================================
tab1, tab2, tab3 = st.tabs(["✦ Learn & Discover", "◷ Price History", "⟡ Smart Insight"])

# ------------------------------------------
# TAB 1: LEARN
# ------------------------------------------
with tab1:
    summary = info.get('longBusinessSummary', 'Detailed company overview is not available for this stock.')
    sector = info.get('sector', 'Unknown Sector')
    mcap = format_large_number(info.get('marketCap'))
    target_price = info.get('targetMeanPrice', 'N/A')
    
    st.markdown(f"""<div style="display: flex; gap: 12px; flex-wrap: wrap;">
<div class="glass-card" style="flex: 1; min-width: 280px;">
<h4 style='margin-top:0; margin-bottom: 6px; color: #f1f5f9;'>What is Equity?</h4>
<p style='font-size: 0.85rem; line-height: 1.5; margin: 0; color: #cbd5e1;'>
A <span class="hover-tooltip">Stock<span class="tooltiptext">Also known as 'equity' or 'shares'. Represents fractional ownership.</span></span> represents piece of ownership in a business. If the company innovates and expands, your piece becomes more valuable.
</p>
</div>
<div class="glass-card" style="flex: 1; min-width: 280px;">
<h4 style='margin-top:0; margin-bottom: 6px; color: #f1f5f9;'>Market Glossary</h4>
<ul style='color: #cbd5e1; line-height: 1.5; font-size: 0.85rem; margin: 0; padding-left: 15px;'>
<li><span class="hover-tooltip">Market Cap<span class="tooltiptext">Price per share × total shares. The total value of the business.</span></span>: Overall size of the company.</li>
<li><span class="hover-tooltip">Dividend<span class="tooltiptext">Cash distributed back to shareholders from company profits.</span></span>: Cash reward paid to shareholders.</li>
<li><span class="hover-tooltip">Bull / Bear<span class="tooltiptext">Bull = Rising prices/optimism. Bear = Falling prices/pessimism.</span></span>: Rising vs Falling market mood.</li>
</ul>
</div>
</div>
<div class="glass-card">
<h4 style='margin-top:0; margin-bottom: 4px; color: #38bdf8;'>Company Story & Overview: {company_name}</h4>
<div style='color: #94a3b8; font-size: 0.8rem; margin-bottom: 8px;'><b>Sector:</b> {sector} &nbsp;|&nbsp; <b>Total Value:</b> {mcap}</div>
<div class="scrollable-text">{summary}</div>
<div style='font-size: 0.85rem; color: #cbd5e1; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 6px;'>
<b>Wall Street Target:</b> Current price is <b>${current_price:.2f}</b>. Analysts expect a 1-year target around <b>${target_price if target_price != 'N/A' else 'Unavailable'}</b>.
</div>
</div>""", unsafe_allow_html=True)
    
    # News Section with Easy Titles & Vibe Checks
    st.markdown("<h4 style='color: #f1f5f9; margin-top: 10px; margin-bottom: 8px;'>📰 Latest News & Market Vibe</h4>", unsafe_allow_html=True)
    valid_news_count = 0
    if news:
        for item in news:
            title = item.get('title', '')
            publisher = item.get('publisher', 'Financial Press')
            link = item.get('link', '#')
            pub_time = item.get('providerPublishTime', 0)
            summary_text = "Click to read full story coverage."
            
            content = item.get('content')
            if isinstance(content, dict):
                title = content.get('title', title)
                pub_time = content.get('pubDate', pub_time)
                summary_text = content.get('summary', summary_text)
                
                provider = content.get('provider')
                if isinstance(provider, dict):
                    publisher = provider.get('displayName', publisher)
                    
                click_url = content.get('clickThroughUrl')
                if isinstance(click_url, dict):
                    link = click_url.get('url', link)
            
            if not title: continue
                
            try:
                if isinstance(pub_time, str): date_str = pd.to_datetime(pub_time).strftime('%b %d, %Y')
                elif pub_time > 0: date_str = datetime.fromtimestamp(pub_time).strftime('%b %d, %Y')
                else: date_str = "Recent"
            except: date_str = "Recent"
            
            if len(summary_text) > 140: summary_text = summary_text[:137] + "..."
            
            vibe_label, vibe_color = analyze_vibe(title + " " + summary_text)
            valid_news_count += 1
            
            # Flush HTML string to prevent markdown text formatting bugs
            st.markdown(f"""<div style='background: rgba(255,255,255,0.02); padding: 10px; border-radius: 6px; border-left: 3px solid {vibe_color}; margin-bottom: 8px;'>
<a href="{link}" target="_blank" class="news-link">{title}</a>
<div style='color: #64748b; font-size: 0.75rem; margin-top: 2px; margin-bottom: 4px;'>{publisher} • {date_str}</div>
<div style='font-size: 0.82rem; color: #cbd5e1; line-height: 1.4; margin-bottom: 4px;'>{summary_text}</div>
<div style='font-size: 0.72rem; font-weight: bold; color: {vibe_color}; background: rgba(0,0,0,0.25); display: inline-block; padding: 2px 6px; border-radius: 4px;'>News Vibe: {vibe_label}</div>
</div>""", unsafe_allow_html=True)
            
            if valid_news_count >= 3: break
                
    if valid_news_count == 0:
        st.write("No recent news stories found for this stock.")

# ------------------------------------------
# TAB 2: PRICE HISTORY
# ------------------------------------------
with tab2:
    price_diff = current_price - start_price
    pct_change = (price_diff / start_price) * 100
    direction = "grown" if price_diff >= 0 else "dropped"
    color = "#4ade80" if price_diff >= 0 else "#f43f5e"
    
    st.markdown(f"""<div style='padding-bottom: 2px;'>
<h4 style='color: #f8fafc; margin: 0;'>Price History ({history_years} Year{'s' if history_years > 1 else ''})</h4>
<p style='font-size: 0.88rem; color: #cbd5e1; margin-top: 4px;'>
A share bought {history_years} year{'s' if history_years > 1 else ''} ago at <b>${start_price:.2f}</b> is now worth <b>${current_price:.2f}</b>. 
Overall, the price has <span style='color: {color}; font-weight: bold;'>{direction} by {abs(pct_change):.2f}%</span>.
</p>
</div>""", unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_view['Date'], y=df_view['Close'], 
        mode='lines', line=dict(color='#38bdf8', width=2), 
        name='Price', fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.05)'
    ))

    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=0, r=0, t=5, b=0), hovermode="x unified",
        xaxis=dict(showgrid=False, showticklabels=True), 
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickprefix="$")
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# TAB 3: SMART INSIGHT (HTML Code Bug Completely Resolved)
# ------------------------------------------
with tab3:
    df_full['50_Day_Avg'] = df_full['Close'].rolling(window=50).mean()
    df_full['200_Day_Avg'] = df_full['Close'].rolling(window=200).mean()
    
    latest_50 = float(df_full['50_Day_Avg'].dropna().iloc[-1]) if not df_full['50_Day_Avg'].dropna().empty else current_price
    latest_200 = float(df_full['200_Day_Avg'].dropna().iloc[-1]) if not df_full['200_Day_Avg'].dropna().empty else current_price
    
    if current_price > latest_50 and latest_50 > latest_200:
        recommendation = "BUY / ACCUMULATE"
        rec_color = "#4ade80"
        rec_desc = "Strong upward momentum. The mathematical trend indicates positive momentum."
    elif current_price < latest_50 and latest_50 < latest_200:
        recommendation = "SELL / AVOID"
        rec_color = "#f43f5e"
        rec_desc = "Downward trend. Market momentum is currently negative."
    else:
        recommendation = "HOLD / CAUTIOUS"
        rec_color = "#fbbf24"
        rec_desc = "Consolidating. A clear upward or downward path has not established yet."

    st.markdown(f"""<div style='padding-bottom: 2px;'>
<h4 style='color: #f8fafc; margin: 0;'>Smart Market Guidance for {company_name}</h4>
<p style='font-size: 0.88rem; color: #cbd5e1; margin-top: 4px;'>We use standard mathematical price averages to filter out daily noise and highlight the main direction.</p>
</div>
<div class="glass-card" style="border-top: 3px solid {rec_color}; padding: 14px;">
<h2 style='color: {rec_color}; margin-top:0; margin-bottom: 4px; font-size: 1.7rem; text-align: center; letter-spacing: 1px;'>{recommendation}</h2>
<p style='font-size: 0.88rem; color: #f8fafc; text-align: center; margin-bottom: 12px;'>{rec_desc}</p>
<div class="reasoning-box">
<h5 style='color: #38bdf8; margin-top:0; margin-bottom: 6px;'>⟡ How We Got This Result (Step-by-Step)</h5>
<ul style='margin-bottom: 0; color: #e2e8f0; line-height: 1.5; font-size: 0.82rem; padding-left: 18px;'>
<li><b>Short-Term Mood:</b> The 50-day average price is <b>${latest_50:.2f}</b>.</li>
<li><b>Long-Term Base:</b> The 200-day average price is <b>${latest_200:.2f}</b>.</li>
<li><b>Conclusion:</b> Because today's price (<b>${current_price:.2f}</b>) is <b>{'higher' if current_price > latest_50 else 'lower'}</b> than the short-term average, and the short-term average is <b>{'higher' if latest_50 > latest_200 else 'lower'}</b> than the long-term average, logic suggests: <b>{recommendation.split(' / ')[0]}</b>.</li>
</ul>
</div>
</div>
<div style='text-align: right; font-size: 10px; color: rgba(255,255,255,0.3); margin-top: -4px;'>Calculations processed locally based on quantitative metrics. Educational purposes only.</div>""", unsafe_allow_html=True)
