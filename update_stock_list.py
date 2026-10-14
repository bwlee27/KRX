from pykrx import stock
from pykrx.website.comm import get_auth_session
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import sys

# KRX 데이터는 로그인 세션이 있어야 조회된다.
# 로그인 실패(비밀번호 만료 등) 시 빈 응답으로 KeyError가 나므로 먼저 확인하고 중단한다.
if get_auth_session() is None:
    print("::error::KRX 로그인 실패. https://data.krx.co.kr 에서 로그인/비밀번호 변경 후 "
          "GitHub Secrets(KRX_ID, KRX_PW)를 확인하세요.")
    sys.exit(1)

# GitHub Actions 러너는 UTC이므로 KST 기준 날짜를 구한 뒤 가장 가까운 이전 영업일을 사용한다.
today_kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d")
date = stock.get_nearest_business_day_in_a_week(today_kst)
print(f"기준일: {date}")

dfs = []

for market in ["KOSPI", "KOSDAQ", "KONEX"]:
    ohlcv = stock.get_market_ohlcv_by_ticker(date, market)
    if ohlcv.empty or "종가" not in ohlcv.columns:
        print(f"{market}: 데이터 없음")
        continue
    ohlcv["name"] = [stock.get_market_ticker_name(t) for t in ohlcv.index]
    ohlcv["market"] = market
    ohlcv["date"] = date
    dfs.append(ohlcv[["name", "market", "date", "시가", "종가"]])

if not dfs:
    print("::error::조회된 데이터가 없습니다. 기존 data/stocks.csv를 유지합니다.")
    sys.exit(1)

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
