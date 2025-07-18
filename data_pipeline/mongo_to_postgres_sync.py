import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine
from config import MONGO_URI, POSTGRES_URI

def flatten_news(doc):
    return {
        'title': doc.get('title') or doc.get('title_m129') or doc.get('title_m130'),
        'summary': doc.get('summary') or doc.get('summary_m129') or doc.get('summary_m130'),
        'url': doc.get('url') or doc.get('url_m129') or doc.get('url_m130'),
        'ticker': doc.get('ticker') or doc.get('ticker_m129') or doc.get('ticker_m130'),
        'time_published': doc.get('time_published') or doc.get('time_published_m129') or doc.get('time_published_m130'),
        'source': doc.get('source') or doc.get('source_m129') or doc.get('source_m130'),
        'overall_sentiment_score': doc.get('overall_sentiment_score') or doc.get('overall_sentiment_score_m129') or doc.get('overall_sentiment_score_m130'),
        'overall_sentiment_label': doc.get('overall_sentiment_label') or doc.get('overall_sentiment_label_m129') or doc.get('overall_sentiment_label_m130'),
    }

def flatten_sentiment(doc):
    return {
        'ticker': doc.get('ticker'),
        'sentiment': doc.get('sentiment'),
        'title': doc.get('title'),
        'summary': doc.get('summary'),
    }

def sync_news():
    client = MongoClient(MONGO_URI)
    db = client['news']
    collection = db['articles']
    docs = list(collection.find())
    if not docs:
        print("No news articles found.")
        return
    flat_docs = [flatten_news(doc) for doc in docs]
    df = pd.DataFrame(flat_docs)
    engine = create_engine(POSTGRES_URI)
    df.to_sql('news_articles', engine, if_exists='replace', index=False, method='multi')
    print(f"Synced {len(df)} news articles to news_articles table.")

def sync_sentiment():
    client = MongoClient(MONGO_URI)
    db = client['news']
    collection = db['sentiment']
    docs = list(collection.find())
    if not docs:
        print("No sentiment records found.")
        return
    flat_docs = [flatten_sentiment(doc) for doc in docs]
    df = pd.DataFrame(flat_docs)
    engine = create_engine(POSTGRES_URI)
    df.to_sql('news_sentiment', engine, if_exists='replace', index=False, method='multi')
    print(f"Synced {len(df)} sentiment records to news_sentiment table.")

def main():
    sync_news()
    sync_sentiment()

if __name__ == "__main__":
    main() 