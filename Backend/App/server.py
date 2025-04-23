from flask import Flask, jsonify, request
from flask_cors import CORS
from graphing import get_graph
import psycopg2
import os
import logging
from dotenv import load_dotenv
from collections import defaultdict

# Load .env
load_dotenv()

app = Flask(__name__)

# Allow CORS only from the frontend S3/EC2 IP
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})

logging.basicConfig(level=logging.DEBUG)

# Central DB connection function using env vars
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route('/analysis/volatility')
def volatility():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT unique_id, name, MIN(market), MAX(market)
        FROM pokemon_prices
        GROUP BY unique_id, name
        HAVING COUNT(*) > 1
    """)
    data = cur.fetchall()
    conn.close()

    result = []
    for unique_id, name, min_price, max_price in data:
        if min_price and min_price > 0:
            change_pct = ((max_price - min_price) / min_price) * 100
            result.append({
                "unique_id": unique_id,
                "name": name,
                "change": change_pct
            })
    top10 = sorted(result, key=lambda x: abs(x['change']), reverse=True)[:10]
    return jsonify(top10)

@app.route('/analysis/rarity_changes')
def rarity_changes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT rarity, MIN(date_pulled), MAX(date_pulled)
        FROM pokemon_prices
        GROUP BY rarity
    """)
    date_ranges = cur.fetchall()

    changes = []
    non_rarities = {
        "MEGA", "Stage 1", "Stage 2", "TAG TEAM", "Rapid Strike", "Basic",
        "Ancient", "Single Strike", "Level-Up", "Promo", "Supporter",
        "Fusion Strike", "Future", "Stadium", "Pokemon Tool", "Tera", "Item"
    }

    unknown_rarity_changes = []

    for rarity, min_date, max_date in date_ranges:
        cur.execute("""
            SELECT AVG(market)
            FROM pokemon_prices
            WHERE rarity = %s AND date_pulled = %s
        """, (rarity, min_date))
        start_avg = cur.fetchone()[0]

        cur.execute("""
            SELECT AVG(market)
            FROM pokemon_prices
            WHERE rarity = %s AND date_pulled = %s
        """, (rarity, max_date))
        end_avg = cur.fetchone()[0]

        if start_avg and start_avg > 0 and end_avg:
            pct_change = ((end_avg - start_avg) / start_avg) * 100

            if rarity in non_rarities:
                unknown_rarity_changes.append(pct_change)
            else:
                changes.append({
                    "rarity": rarity,
                    "change": pct_change
                })

    if unknown_rarity_changes:
        avg_unknown = sum(unknown_rarity_changes) / len(unknown_rarity_changes)
        changes.append({
            "rarity": "Unknown Rarity",
            "change": avg_unknown
        })

    conn.close()
    changes.sort(key=lambda x: x["change"], reverse=True)
    return jsonify(changes)


@app.route('/analysis/top_by_rarity')
def top_by_rarity():
    conn = get_db_connection()
    cur = conn.cursor()

    non_rarities = {
        "MEGA", "Stage 1", "Stage 2", "TAG TEAM", "Rapid Strike", "Basic",
        "Ancient", "Single Strike", "Level-Up", "Promo", "Supporter",
        "Fusion Strike", "Future", "Stadium", "Pokemon Tool", "Tera", "Item"
    }

    cur.execute("""
        SELECT rarity, name, unique_id, MAX(market)
        FROM pokemon_prices
        WHERE market IS NOT NULL AND market > 0
        GROUP BY rarity, name, unique_id
    """)
    data = cur.fetchall()
    conn.close()

    rarity_map = defaultdict(list)
    for rarity, name, unique_id, max_price in data:
        if rarity and rarity not in non_rarities:
            rarity_map[rarity].append({
                "name": name,
                "unique_id": unique_id,
                "price": max_price
            })

    for rarity in rarity_map:
        rarity_map[rarity] = sorted(rarity_map[rarity], key=lambda x: x["price"], reverse=True)[:10]

    return jsonify(rarity_map)

@app.route('/analysis/full_summary')
def full_summary():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*), MIN(date_pulled), MAX(date_pulled)
        FROM pokemon_prices
    """)
    total_rows, min_date, max_date = cur.fetchone()

    cur.execute("""
        SELECT COUNT(low), COUNT(mid), COUNT(high), COUNT(market)
        FROM pokemon_prices
    """)
    low_count, mid_count, high_count, market_count = cur.fetchone()
    total_datapoints = low_count + mid_count + high_count + market_count

    cur.execute("""
        SELECT name, unique_id, MAX(market)
        FROM pokemon_prices
        WHERE market IS NOT NULL AND market > 0 AND market < 4500
        GROUP BY name, unique_id
        ORDER BY MAX(market) DESC
        LIMIT 1
    """)
    most_expensive = cur.fetchone()

    cur.execute("""
        SELECT name, unique_id, MIN(market)
        FROM pokemon_prices
        WHERE market IS NOT NULL AND market > 0
        GROUP BY name, unique_id
        ORDER BY MIN(market) ASC
        LIMIT 1
    """)
    least_expensive = cur.fetchone()

    conn.close()

    return jsonify({
        "total_rows": total_rows,
        "total_datapoints": total_datapoints,
        "timeframe": f"{min_date} to {max_date}",
        "most_expensive": {
            "name": most_expensive[0],
            "id": most_expensive[1],
            "price": most_expensive[2]
        },
        "least_expensive": {
            "name": least_expensive[0],
            "id": least_expensive[1],
            "price": least_expensive[2]
        }
    })

@app.route('/get_latest_prices')
def get_latest_prices():
    unique_id = request.args.get('id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT low, mid, high, market
        FROM pokemon_prices
        WHERE unique_id = %s
        ORDER BY date_pulled DESC
        LIMIT 1
    """, (unique_id,))
    result = cur.fetchone()
    conn.close()

    if result:
        return jsonify({
            "low": result[0],
            "mid": result[1],
            "high": result[2],
            "market": result[3]
        })
    else:
        return jsonify({
            "low": "Not Available",
            "mid": "Not Available",
            "high": "Not Available",
            "market": "Not Available"
        })

@app.route('/get_graph')
def get_graph_route():
    card_id = request.args.get('id')
    if not card_id:
        return jsonify({'error': 'Card ID is required'}), 400

    try:
        logging.debug(f"Request received for card_id: {card_id}")
        dates, prices = get_graph(card_id)
        if not dates or not prices:
            return jsonify({'error': 'No data available for this card'}), 404
        return jsonify({'dates': dates, 'prices': prices})
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)