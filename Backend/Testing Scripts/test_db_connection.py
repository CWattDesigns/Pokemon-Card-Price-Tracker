import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database connection settings from environment
db_settings = {
    "host": os.getenv("DB_HOST"), #Add DB_HOST to .env file
    "dbname": os.getenv("DB_NAME"), #Add DB_NAME to .env file
    "user": os.getenv("DB_USER"), #Add DB_USER to .env file
    "password": os.getenv("DB_PASSWORD"), #Add DB_PASSWORD to .env file
    "port": os.getenv("DB_PORT", "5432"),  # default PostgreSQL port
}

def test_connection():
    #Test and print the current database connection.
    with psycopg2.connect(**db_settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(f"Connected to database: {db_name}")

def check_table_exists():
    #Check if the 'card_sets' table exists in the database.
    with psycopg2.connect(**db_settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'card_sets'
            """)
            result = cursor.fetchone()
            print("Success! Table 'card_sets' exists." if result else "Failed. Table 'card_sets' does not exist.")

if __name__ == "__main__":
    test_connection()
    check_table_exists()