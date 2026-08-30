from app.database.connection import get_connection


def create_category(
    user_id: int,
    name: str,
    category_type: str,
) -> int:
    """
    Create a category for a specific user.

    category_type must be either:
    - expense
    - income
    """

    name = name.strip()

    if not name:
        raise ValueError("Category name cannot be empty.")

    if category_type not in ("expense", "income"):
        raise ValueError(
            "Category type must be 'expense' or 'income'."
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO categories (
                user_id,
                name,
                category_type
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                name,
                category_type,
            ),
        )

        category_id = cursor.lastrowid

        connection.commit()

        return category_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_categories(
    user_id: int,
    category_type: str | None = None,
) -> list[dict]:
    """
    Get categories belonging only to the specified user.

    Optionally filter by category type.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if category_type is None:

        cursor.execute(
            """
            SELECT
                id,
                name,
                category_type,
                created_at
            FROM categories
            WHERE user_id = ?
            ORDER BY name
            """,
            (user_id,),
        )

    else:

        if category_type not in ("expense", "income"):
            raise ValueError(
                "Category type must be 'expense' or 'income'."
            )

        cursor.execute(
            """
            SELECT
                id,
                name,
                category_type,
                created_at
            FROM categories
            WHERE user_id = ?
              AND category_type = ?
            ORDER BY name
            """,
            (
                user_id,
                category_type,
            ),
        )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]
def create_default_categories(user_id: int) -> None:
    """
    Create the default FinSage categories for a new user.
    """

    default_categories = [
        ("Food", "expense"),
        ("Transport", "expense"),
        ("Shopping", "expense"),
        ("Bills", "expense"),
        ("Entertainment", "expense"),
        ("Health", "expense"),
        ("Education", "expense"),
        ("Other", "expense"),
        ("Salary", "income"),
        ("Freelance", "income"),
        ("Investment", "income"),
        ("Other Income", "income"),
    ]

    for name, category_type in default_categories:

        create_category(
            user_id=user_id,
            name=name,
            category_type=category_type,
        )