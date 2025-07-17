import requests
import pandas as pd
from sqlalchemy import create_engine
from config import ALPHAVANTAGE_API_KEY, STOCK_TICKERS, POSTGRES_URI
from tqdm import tqdm
import time

BASE_URL = "https://www.alphavantage.co/query"

def fetch_stock_data(symbol):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": ALPHAVANTAGE_API_KEY,
        "outputsize": "compact"
    }
    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    data = r.json().get("Time Series (Daily)", {})
    df = pd.DataFrame.from_dict(data, orient="index")
    df = df.rename(columns={"4. close": "close"})
    if "close" not in df.columns:
        print(f"No close data for {symbol}. Response: {r.json()}")
        return pd.DataFrame()
    df = df[["close"]].astype(float)
    df["ticker"] = symbol
    df["date"] = df.index
    return df

def main():
    engine = create_engine(POSTGRES_URI)
    all_dfs = []
    for symbol in tqdm(STOCK_TICKERS):
        df = fetch_stock_data(symbol)
        if not df.empty:
            all_dfs.append(df)
        time.sleep(15)  # Alpha Vantage free API rate limit
    if all_dfs:
        result = pd.concat(all_dfs)
        result.to_sql("stock_prices", engine, if_exists="append", index=False, method="multi")
        print("Stock data fetched and stored in PostgreSQL.")
    else:
        print("No stock data fetched.")

if __name__ == "__main__":
    main() 