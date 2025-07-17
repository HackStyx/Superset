import sqlalchemy as sa
from sqlalchemy import create_engine, text
from config import POSTGRES_URI, MONGO_URI
from pymongo import MongoClient

def setup_postgres():
    engine = create_engine(POSTGRES_URI)
    with engine.connect() as conn:
        # Stock prices table
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10),
            date DATE,
            close FLOAT,
            UNIQUE(ticker, date)
        );
        '''))
        # Bridgestone financials table
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS bridgestone_financials (
            id SERIAL PRIMARY KEY,
            year INT,
            quarter VARCHAR(10),
            revenue BIGINT,
            gross_profit BIGINT,
            UNIQUE(year, quarter)
        );
        '''))
    print("PostgreSQL tables created or already exist.")

def test_mongo():
    client = MongoClient(MONGO_URI)
    db = client['news']
    print("MongoDB connection successful. Database 'news' ready.")

def main():
    setup_postgres()
    test_mongo()

if __name__ == "__main__":
    main() 