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
    rows = []
    for date, values in data.items():
        try:
            close = float(values["4. close"])
            rows.append({
                "date": date,
                "close": close,
                "ticker": symbol
            })
        except Exception as e:
            print(f"Skipping {date} for {symbol}: {e}")
    return rows

def main():
    engine = create_engine(POSTGRES_URI)
    for symbol in tqdm(STOCK_TICKERS):
        rows = fetch_stock_data(symbol)
        if rows:
            # ---
            # Preferred approach:
            # Use ON CONFLICT (ticker, date) DO NOTHING to let the database handle duplicates.
            # This is efficient, safe, and avoids race conditions. The database will skip any row
            # that would violate the unique constraint on (ticker, date), so you don't need to check
            # for existing rows in Python. This is the recommended and simplest way to prevent duplicates.
            # ---
            with engine.begin() as conn:
                conn.execute(
                    "INSERT INTO stock_prices (date, close, ticker) VALUES (%(date)s, %(close)s, %(ticker)s) ON CONFLICT (ticker, date) DO NOTHING",
                    rows
                )
            print(f"Inserted {len(rows)} rows for {symbol}")

            # ---
            # Alternative approach :
            # Check for existing (ticker, date) pairs in Python before inserting.
            # This is less efficient and not recommended unless you need to do something special with skipped rows.
            #
            # conn = engine.connect()
            # try:
            #     result = conn.execute(
            #         "SELECT date FROM stock_prices WHERE ticker = %s", (symbol,)
            #     )
            #     existing_dates = set(str(row[0]) for row in result.fetchall())
            # finally:
            #     conn.close()
            # new_rows = [row for row in rows if row["date"] not in existing_dates]
            # if new_rows:
            #     with engine.begin() as conn:
            #         conn.execute(
            #             "INSERT INTO stock_prices (date, close, ticker) VALUES (%(date)s, %(close)s, %(ticker)s)",
            #             new_rows
            #         )
            #     print(f"Inserted {len(new_rows)} new rows for {symbol}")
            # else:
            #     print(f"No new data to insert for {symbol}")
            # ---
        else:
            print(f"No data for {symbol}")
        time.sleep(15)  # API rate limit

if __name__ == "__main__":
    main() 