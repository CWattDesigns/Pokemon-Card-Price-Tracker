from pokemontcgsdk import Card

def fetch_card_data():
    all_cards = Card.all()  # This will return all cards from the SDK
    
    if all_cards:
        return all_cards  # Return all cards data
    else:
        print("Failed to fetch data using the SDK.")
        return []

def main():
    # Fetch all card data using the SDK's card.all() method
    card_data = fetch_card_data()

    # Print names of all cards
    for count, card in enumerate(card_data, start=1):
        print(f"{count}. {card.name}")

if __name__ == "__main__":
    main()
