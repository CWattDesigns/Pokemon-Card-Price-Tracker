import csv

def get_unique_column_values(file_path, column_index):
    # Returns a list of unique values from a specific column in a CSV file.
    unique_values = set()

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header_skipped = False

        for row in reader:
            if not header_skipped:
                header_skipped = True
                continue  # Skip header row

            if column_index <= len(row):
                value = row[column_index - 1].strip()
                if value:
                    unique_values.add(value)

    return sorted(unique_values)

if __name__ == "__main__":
    file_path = "" #Enter the file to run through this script
    column_index = 5  # Ensure this is pointed at the 'rarity' column, 1-indexed
    rarities = get_unique_column_values(file_path, column_index)

    print(f"Unique rarities found in {file_path}:\n")
    for rarity in rarities:
        print(f"- {rarity}")
