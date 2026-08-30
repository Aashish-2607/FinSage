from app.database.connection import get_connection


def initialize_database() -> None:
    """Create all FinSage database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # ==========================================
    # USERS
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ==========================================
    # INSTITUTIONS
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS institutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            UNIQUE(user_id, name)
        )
        """
    )

    # ==========================================
    # ACCOUNTS
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            institution_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            account_type TEXT NOT NULL,

            opening_balance INTEGER NOT NULL DEFAULT 0,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY (institution_id)
                REFERENCES institutions(id)
                ON DELETE CASCADE
        )
        """
    )

    # ==========================================
    # CATEGORIES
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            name TEXT NOT NULL,

            category_type TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            UNIQUE(user_id, name, category_type)
        )
        """
    )

    # ==========================================
    # TRANSACTIONS
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            account_id INTEGER NOT NULL,

            category_id INTEGER,

            amount INTEGER NOT NULL,

            transaction_type TEXT NOT NULL,

            description TEXT,

            merchant TEXT,

            transaction_date DATE NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY (account_id)
                REFERENCES accounts(id)
                ON DELETE CASCADE,

            FOREIGN KEY (category_id)
                REFERENCES categories(id)
                ON DELETE SET NULL,

            CHECK (amount > 0),

            CHECK (
                transaction_type
                IN ('income', 'expense')
            )
        )
        """
    )
        # Add is_active to existing accounts if needed.
    cursor.execute(
        """
        PRAGMA table_info(accounts)
        """
    )

    account_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    if "is_active" not in account_columns:
        cursor.execute(
            """
            ALTER TABLE accounts
            ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
            """
        )

    # Add is_deleted to existing transactions if needed.
    cursor.execute(
        """
        PRAGMA table_info(transactions)
        """
    )

    transaction_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    if "is_deleted" not in transaction_columns:
        cursor.execute(
            """
            ALTER TABLE transactions
            ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0
            """
        )

    connection.commit()
    connection.close()