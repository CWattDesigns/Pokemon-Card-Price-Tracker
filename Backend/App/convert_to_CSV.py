import csv
import re
import datetime

def fix_encoding_issues(text):
    """
    Fix common encoding issues (e.g., accented characters from misinterpreted text).
    Sometimes this does not perform replacements and will need to be double checked in your CSV file. 
    If it did not replace it, use a simple Find & Replace operation in Excel/Sheets.
    """
    if text is None:
        return ""
    return (text.replace("PokÃ©mon", "Pokémon")
                .replace("Î´", "δ"))

def parse_pokemon_prices(input_file, output_file, price_date):
    """
    Parses a plain text file of Pokémon card prices and writes structured data to a CSV file.

    Parameters:
    - input_file (str): Path to the input text file.
    - output_file (str): Path to the output CSV file.
    - price_date (str): Date associated with the prices (e.g., '2025-04-03').
    """
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    data = []
    current_card = None

    for line in lines:
        line = line.strip()
        #Match lines like: 1. Charizard (Pokémon, Rare, Fire) [ID: xy7-12]
        match = re.match(r"(\d+)\.\s(.+)\s\((.+),\s(.+),\s(.+)\)\s\[ID:\s(.+)\]", line)
        """
        -> (\d+)\.\s       matches digit, period, and space
        -> (.+)            matches any characters (the card name)
        -> \((.+)          matches supertype
        -> \s(.+)          matches rarity
        -> \s(.+)\)        matches subtypes inside of parentheses
        -> \[ID:\s(.+)\]   matches the unique ID at the end
        """

        if match:
            card_id, name, supertype, rarity, subtypes, unique_id = match.groups()
            current_card = {
                "id": card_id,
                "unique_id": unique_id,
                "name": fix_encoding_issues(name),
                "supertype": fix_encoding_issues(supertype),
                "rarity": fix_encoding_issues(rarity),
                "subtypes": fix_encoding_issues(subtypes),
                "low": None,
                "mid": None,
                "high": None,
                "market": None,
                "date": price_date
            }
            continue

        # Skip entries without pricing data
        if "TCGPlayer prices not available" in line:
            current_card = None
            continue

        # Extract price type and value
        price_match = re.match(r"(Low|Mid|High|Market): \$(\d+\.\d+)", line)
        if price_match and current_card:
            price_type, price_value = price_match.groups()
            current_card[price_type.lower()] = float(price_value)

        # When a separator line is found, store the current card
        if line.startswith("-") and current_card:
            if any(current_card[k] is not None for k in ["low", "mid", "high", "market"]):
                data.append(current_card)
            current_card = None

    # Write parsed data to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["id", "unique_id", "name", "supertype", "rarity", "subtypes", "low", "mid", "high", "market", "date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"CSV file saved to: {output_file}")

# Example usage
if __name__ == "__main__":
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    input_file = f"PokePrice_{today}.txt"
    output_file = f"pokemon_prices_{today.replace('-', '_')}.csv"
    parse_pokemon_prices(input_file, output_file, today)