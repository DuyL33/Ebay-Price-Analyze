import sqlite3
from typing import Iterable, Dict, Any, Optional
from datetime import datetime


def connect_db(db_path: str = "market.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Helps with concurrency a bit + performance
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            source      TEXT NOT NULL,
            query       TEXT NOT NULL,
            condition   TEXT NOT NULL,
            include_shipping INTEGER NOT NULL,
            limit_n     INTEGER NOT NULL,
            scraped_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS listings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id      INTEGER NOT NULL,
            source      TEXT NOT NULL,
            query       TEXT NOT NULL,
            condition   TEXT NOT NULL,
            item_id     TEXT,               -- eBay item number if available
            title       TEXT,
            url         TEXT,
            item_price  REAL NOT NULL,
            shipping    REAL NOT NULL,
            total       REAL NOT NULL,
            scraped_at  TEXT NOT NULL,

            FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
        );

        -- Dedupe: prevent saving the same sold listing multiple times for the same query+condition.
        -- (If item_id is null, SQLite allows multiple NULLs; that’s fine.)
        CREATE UNIQUE INDEX IF NOT EXISTS uq_listing
        ON listings(source, query, condition, item_id);
        """
    )
    conn.commit()


def create_run(
    conn: sqlite3.Connection,
    source: str,
    query: str,
    condition: str,
    include_shipping: bool,
    limit_n: int,
) -> int:
    scraped_at = datetime.utcnow().isoformat()
    cur = conn.execute(
        """
        INSERT INTO runs (source, query, condition, include_shipping, limit_n, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (source, query, condition, int(include_shipping), int(limit_n), scraped_at),
    )
    conn.commit()
    return int(cur.lastrowid)


def save_listings(
    conn: sqlite3.Connection,
    run_id: int,
    source: str,
    query: str,
    condition: str,
    records: Iterable[Dict[str, Any]],
) -> int:
    """
    records expected keys:
      - item_id (optional)
      - title (optional)
      - url (optional)
      - item_price (float)
      - shipping (float)
      - total (float)
      - scraped_at (optional; if missing, set to now UTC)
    Returns number of newly inserted rows (duplicates ignored).
    """
    now = datetime.utcnow().isoformat()

    to_insert = []
    for r in records:
        to_insert.append(
            (
                run_id,
                source,
                query,
                condition,
                r.get("item_id"),
                r.get("title"),
                r.get("url"),
                float(r.get("item_price", 0.0)),
                float(r.get("shipping", 0.0)),
                float(r.get("total", 0.0)),
                r.get("scraped_at") or now,
            )
        )

    cur = conn.executemany(
        """
        INSERT OR IGNORE INTO listings
        (run_id, source, query, condition, item_id, title, url, item_price, shipping, total, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        to_insert,
    )
    conn.commit()

    # sqlite3 doesn't directly tell inserted count for executemany reliably across versions;
    # but we can approximate via changes() in SQLite.
    inserted = conn.execute("SELECT changes() AS n;").fetchone()["n"]
    return int(inserted)


def get_recent_totals(
    conn: sqlite3.Connection,
    source: str,
    query: str,
    condition: str,
    days: int = 30,
) -> list[float]:
    rows = conn.execute(
        """
        SELECT total
        FROM listings
        WHERE source = ? AND query = ? AND condition = ?
          AND scraped_at >= datetime('now', ?)
        """,
        (source, query, condition, f"-{int(days)} days"),
    ).fetchall()
    return [float(r["total"]) for r in rows]