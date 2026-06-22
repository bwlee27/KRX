from pykrx import stock
import pandas as pd
from datetime import datetime
import os

today = datetime.today().strftime("%Y%m%d")

dfs = []

for market in ["KOSPI", "KOSDAQ", "KONEX"]:
    ohlcv = stock.get_market_ohlcv_by_ticker(today, market)
    if ohlcv.empty:
        continue
    ohlcv["name"] = [stock.get_market_ticker_name(t) for t in ohlcv.index]
    ohlcv["market"] = market
    ohlcv["date"] = today
    dfs.append(ohlcv[["name", "market", "date", "시가", "종가"]])

df = pd.concat(dfs)
df.index.name = "ticker"
df.reset_index(inplace=True)
df.sort_values(["market", "ticker"], inplace=True)

os.makedirs("data", exist_ok=True)

df.to_csv(
    "data/stocks.csv",
    index=False,
    encoding="utf-8-sig"
)

print(df.head())
print(f"{len(df)} stocks saved.")