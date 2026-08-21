"""SQLite setup and Aldi SKU seeding helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

DB_FILENAME = "smartmacro_aldi.db"

DEFAULT_SKUS = [
    ("Chicken Breast Fillets", 3.95, 31.0, 165.0),
    ("5% Fat Beef Mince", 3.49, 26.0, 171.0),
    ("Greek Yogurt", 1.69, 10.0, 59.0),
    ("Eggs (6 pack)", 1.35, 12.5, 155.0),
    ("Tuna Chunks in Spring Water", 0.99, 25.0, 116.0),
    ("Porridge Oats", 0.95, 13.0, 389.0),
    ("Brown Rice", 0.55, 7.5, 360.0),
    ("Broccoli", 0.79, 2.8, 34.0),
]


def create_connection(db_path: str | Path = DB_FILENAME) -> sqlite3.Connection:
    """Create a SQLite connection for the configured database file."""
    return sqlite3.connect(str(db_path))


def initialize_database(conn: sqlite3.Connection) -> None:
    """Create required tables if they don't already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS aldi_skus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price_gbp REAL NOT NULL,
            protein_per_100g REAL NOT NULL,
            calories_per_100g REAL NOT NULL
        )
        """
    )
    conn.commit()


def seed_aldi_skus(conn: sqlite3.Connection, skus: Iterable[tuple[str, float, float, float]] = DEFAULT_SKUS) -> int:
    """Insert default SKU records, ignoring rows that already exist."""
    inserted = 0
    for sku in skus:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO aldi_skus
            (name, price_gbp, protein_per_100g, calories_per_100g)
            VALUES (?, ?, ?, ?)
            """,
            sku,
        )
        inserted += int(cursor.rowcount > 0)
    conn.commit()
    return inserted


def fetch_skus(conn: sqlite3.Connection) -> list[dict]:
    """Return seeded Aldi products as dictionaries."""
    cursor = conn.execute(
        "SELECT name, price_gbp, protein_per_100g, calories_per_100g FROM aldi_skus ORDER BY name"
    )
    return [
        {
            "name": row[0],
            "price_gbp": row[1],
            "protein_per_100g": row[2],
            "calories_per_100g": row[3],
        }
        for row in cursor.fetchall()
    ]
