import os
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

# --- BULLETPROOF .ENV LOADING ---
# 1. Get the exact folder where this app.py file lives
current_dir = Path(__file__).parent
# 2. Tell Python exactly where the .env file is inside that folder
env_path = current_dir / ".env"
# 3. Force load that specific file
load_dotenv(dotenv_path=env_path)

st.title("📈 AI Stock Analyzer & Predictor")
st.write("Calculate Beta, visualize returns, and get an AI-powered short-term trend prediction.")

# --- Background API Key Loading ---
tiingo_key = os.environ.get("TIINGO_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY")

# --- UI Inputs ---
col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, NVDA)", "AAPL").upper()
with col2:
    period = st.selectbox("Historical Data Range", ["1 Year", "2 Years", "5 Years"])

period_map = {"1 Year": 365, "2 Years": 730, "5 Years": 1825}
end_date = datetime.now()
start_date = end_date - timedelta(days=period_map[period])

str_start = start_date.strftime('%Y-%m-%d')
str_end = end_date.strftime('%Y-%m-%d')

# Helper function to fetch from Tiingo manually
def fetch_tiingo_data(symbol, start, end, api_key):
    url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start}&endDate={end}&token={api_key}"
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Tiingo API Error: {response.text}")
        
    data = response.json()
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

if st.button("Analyze & Predict"):
    # Failsafe check
    if not tiingo_key or not gemini_key:
        st.error("⚠️ Missing API Keys! Please ensure your .env file contains TIINGO_API_KEY and GEMINI_API_KEY.")
        st.stop()

    with st.spinner(f"Pulling data directly from Tiingo and running AI models..."):
        try:
            # 1. Fetch Data
            stock_data = fetch_tiingo_data(ticker, str_start, str_end, tiingo_key)
            market_data = fetch_tiingo_data("SPY", str_start, str_end, tiingo_key)
            
            # 2. Beta Calculation
            stock_returns = stock_data["adjClose"].pct_change().dropna()
            market_returns = market_data["adjClose"].pct_change().dropna()
            
            covariance = np.cov(stock_returns, market_returns)[0][1]
            variance = np.var(market_returns)
            beta = covariance / variance
            
            # Display Latest Price & Beta
            latest_price = stock_data["adjClose"].iloc[-1]
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric(label="Latest Closing Price", value=f"${latest_price:.2f}")
            metric_col2.metric(label=f"Beta ({period})", value=f"{beta:.2f}")
            
            # 3. Visualization
            df = pd.DataFrame({"Market Returns": market_returns, "Stock Returns": stock_returns})
            fig = px.scatter(
                df, x="Market Returns", y="Stock Returns", 
                trendline="ols", 
                title=f"{ticker} vs S&P 500 Daily Returns",
                opacity=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. Extract recent data for prediction
            recent_prices = stock_data['adjClose'].tail(14).round(2).tolist()
            
            # 5. Gemini AI Analysis & Prediction
            st.subheader("🤖 AI Trend Prediction")
            prompt = (
                f"You are a quantitative stock analyst. The stock {ticker} has a beta of {beta:.2f}. "
                f"Its closing prices over the last 14 trading days are: {recent_prices}. "
                f"Based on this momentum and volatility, provide a brief 2-sentence prediction of the short-term trend. "
                f"End with a short disclaimer that this is AI-generated and not financial advice."
            )
            
            # Using the modern GenAI SDK
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt
            )
            st.info(response.text)
            
        except Exception as e:
            st.error(f"Error fetching data. Details: {e}")