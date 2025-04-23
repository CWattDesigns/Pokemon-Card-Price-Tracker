import os
from datetime import date
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from pokemontcgsdk import Card

# Load environment variables from .env file
load_dotenv()

# Database connection settings pulled from .env
db_settings = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432")
}

def insert_card_set(set_name, set_code):
    """
    Insert a card set into the 'card_sets' table if it doesn't already exist.
    """
    with psycopg2.connect(**db_settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.card_sets (set_name, set_code)
                VALUES (%s, %s)
                ON CONFLICT (set_code) DO NOTHING
            """, (set_name, set_code))
        connection.commit()

def insert_card(name, set_id, rarity, card_type, hp,
                price_low, price_mid, price_high, price_market,
                currency, image_url, pull_date, card_type_name):
    """
    Insert a Pokémon card into the 'pokemon_cards' table.
    Skips insertion if a record already exists for the same name, set_id, and type.
    """
    with psycopg2.connect(**db_settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.pokemon_cards (
                    name, set_id, rarity, card_type, hp,
                    price_low, price_mid, price_high, price_market,
                    currency, image_url, pull_date, card_type_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name, set_id, card_type_name) DO NOTHING
            """, (
                name, set_id, rarity, card_type, hp,
                price_low, price_mid, price_high, price_market,
                currency, image_url, pull_date, card_type_name
            ))
        connection.commit()

def fetch_all_cards():
    """
    Fetch all cards using the pokemontcgsdk.
    Handles pagination internally and returns a list of Card objects.
    """
    all_cards = []
    try:
        for card in Card.all():
            all_cards.append(card)
        print(f"Fetched {len(all_cards)} cards.")
    except Exception as e:
        print(f"Error fetching data from SDK: {e}")
    return all_cards

def main():
    """
    Main execution point:
    - Fetches all card data
    - Inserts new sets and cards into the PostgreSQL database
    """
    card_data = fetch_all_cards()
    pull_date = date.today()

    for card in card_data:
        set_name = card.set.name
        set_code = card.set.id

        # Insert card set if not already in the database
        insert_card_set(set_name, set_code)

        # Prepare card attributes
        name = card.name
        rarity = card.rarity if card.rarity else "Unknown"
        card_type = card.types[0] if card.types else "Unknown"
        hp = card.hp if card.hp else None
        image_url = card.image_url
        currency = "USD"

        # Extract pricing info
        prices = card.tcgplayer.prices if card.tcgplayer and card.tcgplayer.prices else {}
        price_low = prices.get('low')
        price_mid = prices.get('mid')
        price_high = prices.get('high')
        price_market = prices.get('market')

        # Get set_id from the card_sets table
        try:
            with psycopg2.connect(**db_settings) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM card_sets WHERE set_code = %s", (set_code,))
                    result = cursor.fetchone()
                    if not result:
                        print(f"Warning: Set code {set_code} not found in database.")
                        continue
                    set_id = result[0]
        except Exception as db_error:
            print(f"Database lookup error for set_code {set_code}: {db_error}")
            continue

        # Insert the card into the database
        insert_card(name, set_id, rarity, card_type, hp,
                    price_low, price_mid, price_high, price_market,
                    currency, image_url, pull_date, card_type)

    print(f"Finished processing {len(card_data)} cards.")

if __name__ == "__main__":
    main()
