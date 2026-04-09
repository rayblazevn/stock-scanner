import pandas as pd
import yfinance as yf
import requests
import streamlit as st

# ===== TELEGRAM CONFIG =====
TELEGRAM_TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ===== LOAD STOCK LIST =====
stocks = open("stocks.txt").read().splitlines()

results = []
signals = []

for stock in stocks:
    try:
        df = yf.download(stock + ".VN", period="3mo", interval="1d")

        df["MA20"] = df["Close"].rolling(20).mean()

        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        df["VolAvg"] = df["Volume"].rolling(20).mean()

        latest = df.iloc[-1]

        # ===== CONDITION =====
        if latest["Close"] > latest["MA20"] and latest["RSI"] > 55:
            results.append({
                "Stock": stock,
                "Price": round(latest["Close"], 2),
                "RSI": round(latest["RSI"], 2),
                "MA20": round(latest["MA20"], 2)
            })

        # ===== BUY SIGNAL =====
        if latest["Close"] > latest["MA20"] and latest["RSI"] > 55 and latest["Volume"] > 1.5 * latest["VolAvg"]:
            msg = f"🔥 BUY: {stock} | Price: {round(latest['Close'],2)}"
            signals.append(msg)

    except:
        continue

# ===== SEND TELEGRAM =====
for s in signals:
    send_telegram(s)

# ===== WEB UI =====
st.title("🔥 STOCK SCANNER – PRE BREAK")

df_result = pd.DataFrame(results)

st.dataframe(df_result)

st.success("✔️ Danh sách cổ phiếu sắp chạy")
