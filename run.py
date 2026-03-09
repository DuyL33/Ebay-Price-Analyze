# run.py
from ebay_scraper import ebay_advanced_analysis  # adjust import if your file name differs


def main():
    ebay_advanced_analysis(
        search_query="Seiko 5 SNK803",
        condition="used",
        limit=50,
        include_shipping=True,
        trim_ratio=0.10,
        db_path="market.db",
    )

    ebay_advanced_analysis(
        search_query="Seiko prospex srpc41k1 mini turtle",
        condition="used",
        limit=50,
        include_shipping=True,
        trim_ratio=0.10,
        db_path="market.db",
    )


if __name__ == "__main__":
    main()