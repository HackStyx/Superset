import requests
from config import ALPHAVANTAGE_API_KEY, STOCK_TICKERS, MONGO_URI
from pymongo import MongoClient
from tqdm import tqdm
import time

BASE_URL = "https://www.alphavantage.co/query"

def fetch_news(symbol):
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    return r.json().get("feed", [])

def main():
    client = MongoClient(MONGO_URI)
    db = client["news"]
    collection = db["articles"]
    for symbol in tqdm(STOCK_TICKERS):
        news_items = fetch_news(symbol)
        for item in news_items:
            item["ticker"] = symbol
        if news_items:
            collection.insert_many(news_items)
        time.sleep(15)  # Alpha Vantage free API rate limit
    print("News data fetched and stored in MongoDB.")

if __name__ == "__main__":
    main() 