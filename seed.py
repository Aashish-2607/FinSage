from app.database.connection import get_connection


DEFAULT_CATEGORIES = [
    ("Food", "expense"),
    ("Transport", "expense"),
    ("Shopping", "expense"),
    ("Bills", "expense"),
    ("Entertainment", "expense"),
    ("Health", "expense"),
    ("Education", "expense"),
    ("Investment", "expense"),
    ("Salary", "income"),
    ("Freelance", "income"),
    ("Other", "expense"),
]


def create_user(name: str, email: str | None = None) -> int:
    """Create a FinSage user and return the generated user ID."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (name, email)
        VALUES (?, ?)
        """,
        (name, email),
    )

    user_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return user_id


def create_default_categories(user_id: int) -> None:
    """Create the default categories for a user."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.executemany(
        """
        INSERT OR IGNORE INTO categories
        (user_id, name, category_type)
        VALUES (?, ?, ?)
        """,
        [
            (user_id, name, category_type)
            for name, category_type in DEFAULT_CATEGORIES
        ],
    )

    connection.commit()
    connection.close()


def main() -> None:
    """Create initial FinSage data."""

    user_id = create_user(
        name="Kanha",
        email=None,
    )

    create_default_categories(user_id)

    print(f"FinSage user created successfully. ID: {user_id}")
    print("Default categories created successfully.")


if __name__ == "__main__":
    main()