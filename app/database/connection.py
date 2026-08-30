import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/finsage.db")


def get_connection() -> sqlite3.Connection:
    """Create and return a connection to the FinSage database."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    # Enable foreign-key enforcement in SQLite.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection