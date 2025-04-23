import os
import requests
import datetime
import time
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("POKEMON_API_KEY") #Add POKEMON_API_KEY to your .env file
BASE_URL = "https://api.pokemontcg.io/v2/cards"

# Generate output filename using current date
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = rf"file_name_goes_here{current_date}.txt" #Replace "file_name_goes_here" with the name you want the file to be + {current_date}

def fetch_all_cards():
    """
    Fetch all Pokémon cards from the TCG API with pagination and rate-limit handling.
    Returns a list of all cards retrieved.
    """
    all_cards = []
    page = 1
    headers = {"X-Api-Key": API_KEY}
    page_size = 250

    while True:
        url = f"{BASE_URL}?page={page}&pageSize={page_size}&nocache={random.randint(1, 100000)}"
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            #Catches the rate limit
            print("Rate limited. Retrying in 5 seconds...")
            time.sleep(5)
            continue

        if response.status_code != 200:
            #Catches failed page
            print(f"Error: Failed to fetch page {page}. Status Code: {response.status_code}")
            break

        data = response.json().get("data", [])
        if not data:
            print(f"No more cards found on page {page}. Stopping fetch.")
            break

        all_cards.extend(data)
        print(f"Fetched {len(data)} cards from page {page}. Total so far: {len(all_cards)}")
        page += 1
        time.sleep(1)

    return all_cards

def get_tcgplayer_prices(card):
    """
    Extract price details from a card's TCGPlayer data.
    Returns a dictionary of price tiers or None if unavailable.
    """
    prices = card.get("tcgplayer", {}).get("prices", {})
    for _, price_data in prices.items():
        return {
            "low": price_data.get("low"),
            "mid": price_data.get("mid"),
            "high": price_data.get("high"),
            "market": price_data.get("market"),
        }
    return None

def get_base_name(card):
    """
    Return the simplified base name for sorting.
    Preserves full name unless the card is a Pokémon.
    """
    name = card.get("name", "Unknown Card")
    supertype = card.get("supertype", "Unknown")
    return name if supertype != "Pokémon" else name.split(" ")[0]

def main():
    all_cards = fetch_all_cards()

    if not all_cards:
        print("No cards were fetched. Exiting.")
        return

    all_cards.sort(key=get_base_name)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(f"=== TCGPlayer Pricing Data ({current_date}) ===\n\n")

        for i, card in enumerate(all_cards, start=1):
            card_id = card.get("id", "Unknown ID")
            card_name = card.get("name", "Unknown Card")
            rarity = card.get("rarity", "Unknown Rarity")
            supertype = card.get("supertype", "Unknown")
            subtypes = ", ".join(card.get("subtypes", [])) or "None"
            prices = get_tcgplayer_prices(card)

            print(f"{i}. {card_name} ({supertype}) [ID: {card_id}]")

            output = f"{i}. {card_name} ({supertype}, {rarity}, {subtypes}) [ID: {card_id}]\n"
            if prices:
                output += f"  Low: ${prices['low']}\n"
                output += f"  Mid: ${prices['mid']}\n"
                output += f"  High: ${prices['high']}\n"
                output += f"  Market: ${prices['market']}\n"
            else:
                output += "  TCGPlayer prices not available.\n"

            output += "-" * 40 + "\n"
            file.write(output)

    print("\n=== Summary ===")
    print(f"Total cards fetched: {len(all_cards)}")
    print(f"Pricing data saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
