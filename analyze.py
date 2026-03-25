import matplotlib.pyplot as plt

from db import connect_db, init_db, get_totals_grouped_by_day
from utils import get_market_stats


def plot_query_trend(query: str, condition: str = "used", source: str = "ebay", trim_ratio: float = 0.10):
    conn = connect_db("market.db")
    init_db(conn)

    grouped = get_totals_grouped_by_day(conn, source=source, query=query, condition=condition)

    if not grouped:
        print("No data found.")
        conn.close()
        return

    days = []
    medians = []
    trimmed_means = []
    p25s = []
    p75s = []

    for day, totals in grouped.items():
        stats = get_market_stats(totals, trim_ratio=trim_ratio)

        if not stats:
            continue

        days.append(day)
        medians.append(stats["median"])
        trimmed_means.append(stats["trimmed_mean"])
        p25s.append(stats["p25"])
        p75s.append(stats["p75"])

    conn.close()

    plt.figure(figsize=(10, 6))
    plt.plot(days, medians, marker="o", label="Median")
    plt.plot(days, trimmed_means, marker="o", label="Trimmed Mean")
    plt.plot(days, p25s, linestyle="--", label="P25")
    plt.plot(days, p75s, linestyle="--", label="P75")

    plt.title(f"{query} Price Trend ({condition})")
    plt.xlabel("Scrape Date")
    plt.ylabel("Price")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_query_trend("Seiko 5 SNK803", condition="used")
    plot_query_trend("Seiko prospex srpc41k1 mini turtle", condition="used")