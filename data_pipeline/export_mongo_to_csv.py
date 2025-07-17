from config import MONGO_URI
from pymongo import MongoClient
import pandas as pd

def export_collection_to_csv(db_name, collection_name, csv_path):
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    cursor = db[collection_name].find()
    df = pd.DataFrame(list(cursor))
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    df.to_csv(csv_path, index=False)
    print(f"Exported {collection_name} to {csv_path}")

def main():
    export_collection_to_csv('news', 'articles', 'news_articles.csv')
    export_collection_to_csv('news', 'sentiment', 'news_sentiment.csv')

if __name__ == "__main__":
    main() 