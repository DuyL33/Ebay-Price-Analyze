# analyze.py
from db import connect_db, init_db, get_recent_totals
from utils import get_market_stats


def analyze_query(query: str, condition: str = "used", source: str = "ebay", trim_ratio: float = 0.10):
    conn = connect_db("market.db")
    init_db(conn)

    for days in (7, 30, 90):
        totals = get_recent_totals(conn, source=source, query=query, condition=condition, days=days)
        stats = get_market_stats(totals, trim_ratio=trim_ratio)

        print(f"\n=== {query} ({condition}) | last {days} days ===")
        print(f"n = {len(totals)}")
        if not stats:
            print("No data yet.")
            continue

        spread = stats["p75"] - stats["p25"]
        print(f"Median: ${stats['median']:.2f} | TrimMean: ${stats['trimmed_mean']:.2f}")
        print(f"P25: ${stats['p25']:.2f} | P75: ${stats['p75']:.2f} | Spread: ${spread:.2f}")
        print(f"Min: ${stats['min']:.2f} | Max: ${stats['max']:.2f}")

    conn.close()


if __name__ == "__main__":
    analyze_query("Seiko 5 SNK803", condition="used")