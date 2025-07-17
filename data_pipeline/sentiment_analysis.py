from config import MONGO_URI
from pymongo import MongoClient
from textblob import TextBlob
from tqdm import tqdm

def main():
    client = MongoClient(MONGO_URI)
    db = client["news"]
    articles = list(db["articles"].find())
    sentiment_results = []
    for article in tqdm(articles):
        text = article.get("title", "") + ". " + article.get("summary", "")
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        sentiment_results.append({
            "article_id": article.get("_id"),
            "ticker": article.get("ticker"),
            "sentiment": sentiment,
            "title": article.get("title", ""),
            "summary": article.get("summary", "")
        })
    if sentiment_results:
        db["sentiment"].insert_many(sentiment_results)
    print("Sentiment analysis complete and stored in MongoDB.")

if __name__ == "__main__":
    main() 