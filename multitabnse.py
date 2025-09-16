import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from utils import send_telegram_message, log_to_csv
from datetime import datetime

st.set_page_config(page_title="Ultimate NSE Cockpit", layout="wide")
st.title("🚀 Ultimate NSE Cockpit")

# ------------------------ Fetch Top NSE Stocks ------------------------
top_stocks = ["RELIANCE.NS", "TCS.NS", "HDFC.NS", "INFY.NS", "ICICI.NS", "SBIN.NS", "HINDUNILVR.NS"]

stock_data = []
for ticker in top_stocks:
    try:
        data = yf.Ticker(ticker).history(period="1d")
        price = round(data['Close'].iloc[-1], 2)
        stock_name = ticker.replace(".NS", "")
        # Placeholder ML logic for demo; replace with your model
        signal = "BUY" if price % 2 == 0 else "SELL"
        confidence = 80  # placeholder
        target = round(price * 1.01, 2)
        sl = round(price * 0.995, 2)
        options_strategy = "Straddle" if signal=="BUY" else "Strangle"
        predicted_action = signal
        next_day_price = round(price * 1.002, 2)
        strategy = "RSI Oversold" if signal=="BUY" else "MACD Cross"
        stock_data.append([stock_name, price, signal, target, sl, confidence, strategy, options_strategy, predicted_action, next_day_price])
    except:
        continue

df = pd.DataFrame(stock_data, columns=["Stock","Price","Signal","Target","SL","Confidence","Strategy","Options_Strategy","Predicted_Action","Next_Day_Price"])
df = df.sort_values(by="Confidence", ascending=False)

# ------------------------ Tabs ------------------------
tabs = st.tabs([
    "Signals", "Options Strategies", "Predictions", "Index Analysis",
    "Stock Recommendations", "News & Events", "Learning Hub", "Global Markets", "Alerts History"
])

# ------------------------ Signals Tab ------------------------
with tabs[0]:
    st.header("📈 Signals")
    for idx, row in df.iterrows():
        stock = row["Stock"]
        price = row["Price"]
        action = row["Signal"]
        target = row["Target"]
        sl = row["SL"]
        confidence = row["Confidence"]
        message = f"🚀 {action} Alert\nStock: {stock}\nPrice: ₹{price}\nStrategy: {row['Strategy']}\nTarget: {target} | SL: {sl}\nConfidence: {confidence}%"
        
        st.subheader(f"{stock} Signal")
        st.write(message)
        if st.button(f"Send Telegram Alert: {stock}", key=f"{stock}_signal"):
            send_telegram_message(message)
            log_to_csv(stock, action, message)
            st.success(f"✅ Alert sent for {stock}!")

# ------------------------ Options Strategies Tab ------------------------
with tabs[1]:
    st.header("📊 Options Strategies")
    st.dataframe(df[["Stock", "Options_Strategy", "Signal", "Price", "Target", "SL"]])

# ------------------------ Predictions Tab ------------------------
with tabs[2]:
    st.header("🤖 ML Predictions")
    st.dataframe(df[["Stock", "Predicted_Action", "Confidence", "Next_Day_Price"]])

# ------------------------ Index Analysis Tab ------------------------
with tabs[3]:
    st.header("🏦 Index Analysis")
    indices = {"NIFTY 50": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    for name, ticker in indices.items():
        data = yf.download(ticker, period="7d", interval="1d")
        st.subheader(name)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=name))
        st.plotly_chart(fig, use_container_width=True)

# ------------------------ Stock Recommendations Tab ------------------------
with tabs[4]:
    st.header("💹 Stock Recommendations")
    top_stocks_df = df.sort_values(by="Confidence", ascending=False).head(5)
    st.dataframe(top_stocks_df[["Stock", "Signal", "Price", "Target", "SL", "Confidence"]])

# ------------------------ News & Events Tab ------------------------
with tabs[5]:
    st.header("📰 News & Events")
    news = [
        "NIFTY opens 50 pts higher on global cues",
        "RELIANCE quarterly results beat estimates",
        "RBI policy decision tomorrow"
    ]
    for n in news:
        st.write(f"- {n}")
        if st.button(f"Send News Alert: {n}", key=f"news_{n}"):
            send_telegram_message(f"📰 News Alert:\n{n}")
            st.success("✅ News alert sent!")

# ------------------------ Learning Hub Tab ------------------------
with tabs[6]:
    st.header("📚 Learning Hub")
    st.write("""
    **Indicators Explained:**
    - RSI: Relative Strength Index
    - MACD: Moving Average Convergence Divergence
    - Bollinger Bands: Price volatility measure
    **Strategies:**
    - Straddle, Strangle, Iron Condor explained
    """)

# ------------------------ Global Markets Tab ------------------------
with tabs[7]:
    st.header("🌎 Global Markets")
    global_indices = {"Dow Jones": "^DJI", "Nasdaq": "^IXIC", "S&P 500": "^GSPC"}
    for name, ticker in global_indices.items():
        data = yf.download(ticker, period="7d", interval="1d")
        st.subheader(name)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=name))
        st.plotly_chart(fig, use_container_width=True)

# ------------------------ Alerts History Tab ------------------------
with tabs[8]:
    st.header("📂 Alerts History")
    try:
        history = pd.read_csv("alert_history.csv", names=["Timestamp", "Stock", "Action", "Message"])
        st.dataframe(history)
    except FileNotFoundError:
        st.write("No alerts sent yet.")