import psycopg2
import os
import logging
from dotenv import load_dotenv

# Load database credentials from .env
load_dotenv()

def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    except Exception as e:
        logging.error(f"Error connecting to the database: {str(e)}")
        raise

# Retrieves historical market price trend for the given card
def get_graph(unique_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date_pulled, market
            FROM pokemon_prices
            WHERE unique_id = %s AND date_pulled >= '2025-02-01'
            ORDER BY date_pulled ASC;
        """, (unique_id,))
        data = cursor.fetchall()
        if not data:
            return None, None
        dates = [str(row[0]) for row in data]
        prices = [row[1] for row in data]
        return dates, prices
    except Exception as e:
        logging.error(f"Error generating graph for {unique_id}: {str(e)}")
        return None, None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
