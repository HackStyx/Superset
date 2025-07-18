from sqlalchemy import create_engine, text
from config import POSTGRES_URI

# Query to delete duplicates, keeping the row with the lowest id for each (ticker, date)
DELETE_DUPLICATES_QUERY = """
DELETE FROM stock_prices a
USING stock_prices b
WHERE a.id > b.id
  AND a.ticker = b.ticker
  AND a.date = b.date;
"""

def main():
    engine = create_engine(POSTGRES_URI)
    conn = engine.connect()
    try:
        print("Removing duplicate rows from stock_prices...")
        result = conn.execute(text("SELECT COUNT(*) FROM stock_prices;")).scalar()
        print(f"Rows before deletion: {result}")
        deleted = conn.execute(text(DELETE_DUPLICATES_QUERY))
        result_after = conn.execute(text("SELECT COUNT(*) FROM stock_prices;")).scalar()
        print(f"Rows after deletion: {result_after}")
        print(f"Deleted {result - result_after} duplicate rows.")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 