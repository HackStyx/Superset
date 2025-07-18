from sqlalchemy import create_engine, text
from config import POSTGRES_URI

# Query to find duplicate (ticker, date) pairs
DUPLICATE_QUERY = """
SELECT ticker, date, COUNT(*) as count
FROM stock_prices
GROUP BY ticker, date
HAVING COUNT(*) > 1;
"""

# Query to show all rows for a given (ticker, date)
ROW_QUERY = """
SELECT * FROM stock_prices WHERE ticker = :ticker AND date = :date;
"""

def main():
    engine = create_engine(POSTGRES_URI)
    conn = engine.connect()
    try:
        print("Checking for duplicate (ticker, date) pairs in stock_prices...")
        result = conn.execute(text(DUPLICATE_QUERY))
        duplicates = result.fetchall()
        if not duplicates:
            print("No duplicates found.")
            return
        print(f"Found {len(duplicates)} duplicate (ticker, date) pairs:")
        for row in duplicates:
            ticker, date, count = row
            print(f"\nTicker: {ticker}, Date: {date}, Count: {count}")
            # Print all rows for this duplicate
            rows = conn.execute(text(ROW_QUERY), {"ticker": ticker, "date": date}).fetchall()
            for r in rows:
                print(dict(r))
    finally:
        conn.close()

if __name__ == "__main__":
    main() 