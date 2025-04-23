# Pokémon TCG Price Tracker & Data Analysis Platform

A full-stack web application for searching Pokémon Trading Card Game (TCG) cards, viewing pricing trends over time, and analyzing insights such as volatility and rarity-based price changes. Built to empower users with dynamic, visual, and data-driven views of the TCG marketplace.

---

Features
- **Card Search**: Look up cards by name, set, and rarity using the Pokémon TCG API.
- **Price Details**: View low, mid, high, and market price estimates from TCGPlayer.
- **Historical Trend Graph**: Dynamically rendered line chart showing market price trends over time per card.
- **Data Analysis Dashboard**:
  - Summary statistics (total cards, time range, datapoints)
  - Most/least expensive cards
  - Top 10 most volatile cards by price
  - Average price changes by rarity
  - Top 10 most expensive cards per rarity as a scatterplot

---

**Frontend**: HTML, CSS, JavaScript, Chart.js, Luxon<br>
**Backend**: Python (Flask), psycopg2, dotenv<br>
**Database**: PostgreSQL (hosted on AWS RDS)<br>
**Deployment**: AWS EC2 (backend), AWS S3 (static frontend)<br>
**APIs**: Pokémon TCG API, TCGPlayer (via Pokémon TCG API data)

---

Setup Instructions
1. Clone the Repository
```bash
git clone https://github.com//pokemon-tcg-price-tracker.git
cd pokemon-tcg-price-tracker
```

2. Environment Variables
Create a `.env` file in the project root with the following:
```env
DB_HOST=your-db-host
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
FRONTEND_ORIGIN=http://your-frontend-url
POKEMON_API_KEY=your-pokemon-api-key
```

3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

4. Run Flask Backend
```bash
python server.py
```
The server will run at `http://localhost:5000` or your configured host.

---

Frontend Usage
If hosted via AWS S3:
- Upload the `frontend/` folder contents.
- Ensure the `pokemoninfo.html` and `data_analysis.html` files use the correct backend IP in their fetch requests (these are dynamically configured in code for flexibility).

---

Sample Workflow
1. Run `pricing_test_delay.py` to fetch and export card pricing data.
2. Use `convert_to_CSV.py` to parse and store it in CSV.
3. Load that data into PostgreSQL manually or use an ETL script.
4. Start the Flask server (I ran mine in Git Bash) and visit the frontend to:
   - Search cards and see prices
   - Click a card to view trend graph
   - Explore insights on the analysis page

---

Contributing
Contributions are welcome! Open a pull request or issue for feature ideas or bug fixes.


