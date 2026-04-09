import pandas as pd
import requests
import streamlit as st

st.title("🔥 STOCK SCANNER – REALTIME (TCBS)")

def get_data(symbol):
    url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term?symbol={symbol}&resolution=D&limit=100"
    res = requests.get(url)
    data = res.json()["data"]

    df = pd.DataFrame(data)
    df = df.rename(columns={"c": "Close", "v": "Volume"})
    return df

stocks = open("stocks.txt").read().splitlines()

results = []

for stock in stocks:
    try:
        df = get_data(stock)

        df["MA20"] = df["Close"].rolling(20).mean()

        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        latest = df.iloc[-1]

        if latest["RSI"] > 50:
            trend = "UP" if latest["Close"] > latest["MA20"] else "SIDE"

            results.append({
                "Stock": stock,
                "Price": round(latest["Close"], 2),
                "RSI": round(latest["RSI"], 2),
                "Trend": trend
            })

    except:
        continue

df_result = pd.DataFrame(results)

if df_result.empty:
    st.warning("⚠️ Không có cổ phiếu đạt điều kiện hôm nay")
else:
    st.dataframe(df_result)

st.success("✔️ Realtime scanner running")
