from app.database.connection import get_connection

from app.transactions.validators import (
    validate_amount,
    validate_transaction_date,
    validate_transaction_type,
)

from app.utils.money import (
    format_rupees,
    rupees_to_paise,
)


def create_transaction(
    user_id: int,
    account_id: int,
    category_id: int | None,
    amount: str | int | float,
    transaction_type: str,
    transaction_date: str,
    description: str | None = None,
    merchant: str | None = None,
) -> int:
    """
    Create a financial transaction.

    Amount is accepted in rupees and stored
    internally as paise.
    """

    transaction_type = validate_transaction_type(
        transaction_type
    )

    amount = validate_amount(amount)

    transaction_date = validate_transaction_date(
        transaction_date
    )

    amount_paise = rupees_to_paise(amount)

    connection = get_connection()
    cursor = connection.cursor()

    # ------------------------------------------
    # Verify account belongs to the user
    # ------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM accounts
        WHERE id = ?
        AND user_id = ?
        AND is_active = 1
        """,
        (
            account_id,
            user_id,
        ),
    )

    account = cursor.fetchone()

    if account is None:
        connection.close()

        raise ValueError(
            "Account not found, inactive, or does not belong to the user."
        )

    # ------------------------------------------
    # Verify category belongs to the user
    # ------------------------------------------

    if category_id is not None:

        cursor.execute(
            """
            SELECT id
            FROM categories
            WHERE id = ?
            AND (user_id = ? OR user_id IS NULL)
            """,
            (
                category_id,
                user_id,
            ),
        )

        category = cursor.fetchone()

        if category is None:
            connection.close()

            raise ValueError(
                "Category not found or does not belong to the user."
            )

    # ------------------------------------------
    # Insert transaction
    # ------------------------------------------

    cursor.execute(
        """
        INSERT INTO transactions (
            user_id,
            account_id,
            category_id,
            amount,
            transaction_type,
            description,
            merchant,
            transaction_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            account_id,
            category_id,
            amount_paise,
            transaction_type,
            description.strip()
            if description
            else None,
            merchant.strip()
            if merchant
            else None,
            transaction_date,
        ),
    )

    transaction_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return transaction_id
def get_transactions(
    user_id: int,
    account_id: int | None = None,
    category_id: int | None = None,
    transaction_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    include_deleted: bool = False,
) -> list[dict]:
    """
    Retrieve transactions for a user.

    Optional filters:
        account_id
        category_id
        transaction_type
        start_date
        end_date
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            transactions.id,
            transactions.account_id,
            transactions.category_id,
            transactions.amount,
            transactions.transaction_type,
            transactions.description,
            transactions.merchant,
            transactions.transaction_date,
            transactions.is_deleted,

            accounts.name AS account_name,

            institutions.name AS institution_name,

            categories.name AS category_name

        FROM transactions

        JOIN accounts
            ON transactions.account_id = accounts.id

        JOIN institutions
            ON accounts.institution_id = institutions.id

        LEFT JOIN categories
            ON transactions.category_id = categories.id

        WHERE transactions.user_id = ?
    """

    parameters: list = [user_id]
    if not include_deleted:
        query += """
        AND transactions.is_deleted = 0
    """
    # ------------------------------------------
    # Account filter
    # ------------------------------------------

    if account_id is not None:
        query += """
            AND transactions.account_id = ?
        """

        parameters.append(account_id)

    # ------------------------------------------
    # Category filter
    # ------------------------------------------

    if category_id is not None:
        query += """
            AND transactions.category_id = ?
        """

        parameters.append(category_id)

    # ------------------------------------------
    # Transaction type filter
    # ------------------------------------------

    if transaction_type is not None:
        transaction_type = validate_transaction_type(
            transaction_type
        )

        query += """
            AND transactions.transaction_type = ?
        """

        parameters.append(transaction_type)

    # ------------------------------------------
    # Start date filter
    # ------------------------------------------

    if start_date is not None:
        start_date = validate_transaction_date(
            start_date
        )

        query += """
            AND transactions.transaction_date >= ?
        """

        parameters.append(start_date)

    # ------------------------------------------
    # End date filter
    # ------------------------------------------

    if end_date is not None:
        end_date = validate_transaction_date(
            end_date
        )

        query += """
            AND transactions.transaction_date <= ?
        """

        parameters.append(end_date)

    # ------------------------------------------
    # Newest transactions first
    # ------------------------------------------

    query += """
        ORDER BY transactions.transaction_date DESC,
                 transactions.id DESC
    """

    cursor.execute(
        query,
        parameters,
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "account_id": row["account_id"],
            "category_id": row["category_id"],
            "amount": format_rupees(row["amount"]),
            "transaction_type": row["transaction_type"],
            "description": row["description"],
            "merchant": row["merchant"],
            "transaction_date": row["transaction_date"],
            "is_deleted": row["is_deleted"],
            "account_name": row["account_name"],
            "institution_name": row["institution_name"],
            "category_name": row["category_name"],
        }
        for row in rows
    ]
def update_transaction(
    transaction_id: int,
    user_id: int,
    account_id: int,
    category_id: int | None,
    amount: str | int | float,
    transaction_type: str,
    transaction_date: str,
    description: str | None = None,
    merchant: str | None = None,
) -> None:
    """
    Update an existing transaction.

    Amount is accepted in rupees and stored in paise.
    """

    transaction_type = validate_transaction_type(
        transaction_type
    )

    amount = validate_amount(amount)

    transaction_date = validate_transaction_date(
        transaction_date
    )

    amount_paise = rupees_to_paise(amount)

    connection = get_connection()
    cursor = connection.cursor()

    # ------------------------------------------
    # Verify transaction belongs to user
    # ------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM transactions
        WHERE id = ?
        AND user_id = ?
        """,
        (
            transaction_id,
            user_id,
        ),
    )

    transaction = cursor.fetchone()

    if transaction is None:
        connection.close()

        raise ValueError(
            "Transaction not found or does not belong to the user."
        )

    # ------------------------------------------
    # Verify account
    # ------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM accounts
        WHERE id = ?
        AND user_id = ?
        AND is_active = 1
        """,
        (
            account_id,
            user_id,
        ),
    )

    account = cursor.fetchone()

    if account is None:
        connection.close()

        raise ValueError(
            "Account not found, inactive, or does not belong to the user."
        )

    # ------------------------------------------
    # Verify category
    # ------------------------------------------

    if category_id is not None:

        cursor.execute(
            """
            SELECT id
            FROM categories
            WHERE id = ?
            AND (user_id = ? OR user_id IS NULL)
            """,
            (
                category_id,
                user_id,
            ),
        )

        category = cursor.fetchone()

        if category is None:
            connection.close()

            raise ValueError(
                "Category not found or does not belong to the user."
            )

    # ------------------------------------------
    # Update transaction
    # ------------------------------------------

    cursor.execute(
        """
        UPDATE transactions

        SET
            account_id = ?,
            category_id = ?,
            amount = ?,
            transaction_type = ?,
            description = ?,
            merchant = ?,
            transaction_date = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE id = ?
        AND user_id = ?
        """,
        (
            account_id,
            category_id,
            amount_paise,
            transaction_type,
            description.strip()
            if description
            else None,
            merchant.strip()
            if merchant
            else None,
            transaction_date,
            transaction_id,
            user_id,
        ),
    )

    connection.commit()
    connection.close()
def delete_transaction(
    transaction_id: int,
    user_id: int,
) -> None:
    """
    Soft-delete a transaction.

    The transaction remains in the database,
    but is excluded from normal history and
    balance calculations.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE transactions
        SET
            is_deleted = 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        AND user_id = ?
        AND is_deleted = 0
        """,
        (
            transaction_id,
            user_id,
        ),
    )

    if cursor.rowcount == 0:
        connection.close()

        raise ValueError(
            "Transaction not found or already deleted."
        )

    connection.commit()
    connection.close()
def restore_transaction(
    transaction_id: int,
    user_id: int,
) -> None:
    """
    Restore a previously soft-deleted transaction.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE transactions
        SET
            is_deleted = 0,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        AND user_id = ?
        AND is_deleted = 1
        """,
        (
            transaction_id,
            user_id,
        ),
    )

    if cursor.rowcount == 0:
        connection.close()

        raise ValueError(
            "Deleted transaction not found."
        )

    connection.commit()
    connection.close()
def get_transaction_summary(
    user_id: int,
    account_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """
    Return total income, total expenses,
    and net cash flow for a user.
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'income'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_income,

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'expense'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_expense

        FROM transactions

        WHERE user_id = ?
        AND is_deleted = 0
    """

    parameters: list = [user_id]

    if account_id is not None:
        query += """
            AND account_id = ?
        """
        parameters.append(account_id)

    if start_date is not None:
        start_date = validate_transaction_date(
            start_date
        )

        query += """
            AND transaction_date >= ?
        """
        parameters.append(start_date)

    if end_date is not None:
        end_date = validate_transaction_date(
            end_date
        )

        query += """
            AND transaction_date <= ?
        """
        parameters.append(end_date)

    cursor.execute(
        query,
        parameters,
    )

    row = cursor.fetchone()

    connection.close()

    total_income = row["total_income"]
    total_expense = row["total_expense"]

    net_cash_flow = (
        total_income - total_expense
    )

    return {
        "total_income": format_rupees(
            total_income
        ),
        "total_expense": format_rupees(
            total_expense
        ),
        "net_cash_flow": format_rupees(
            net_cash_flow
        ),
    }
def get_category_summary(
    user_id: int,
    transaction_type: str = "expense",
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict]:
    """
    Return transaction totals grouped by category.
    """

    transaction_type = validate_transaction_type(
        transaction_type
    )

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            categories.id AS category_id,
            categories.name AS category_name,
            COALESCE(SUM(transactions.amount), 0)
                AS total_amount

        FROM transactions

        LEFT JOIN categories
            ON transactions.category_id = categories.id

        WHERE transactions.user_id = ?
        AND transactions.transaction_type = ?
        AND transactions.is_deleted = 0
    """

    parameters: list = [
        user_id,
        transaction_type,
    ]

    if start_date is not None:
        start_date = validate_transaction_date(
            start_date
        )

        query += """
            AND transactions.transaction_date >= ?
        """

        parameters.append(start_date)

    if end_date is not None:
        end_date = validate_transaction_date(
            end_date
        )

        query += """
            AND transactions.transaction_date <= ?
        """

        parameters.append(end_date)

    query += """
        GROUP BY
            categories.id,
            categories.name

        ORDER BY total_amount DESC
    """

    cursor.execute(
        query,
        parameters,
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "category_id": row["category_id"],
            "category_name": (
                row["category_name"]
                or "Uncategorized"
            ),
            "total_amount": format_rupees(
                row["total_amount"]
            ),
        }
        for row in rows
    ]

def get_transaction_summary_raw(
    user_id: int,
    account_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """
    Return financial summary in raw paise.

    Intended for analytics and calculations,
    not direct UI display.
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'income'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_income,

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'expense'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_expense

        FROM transactions

        WHERE user_id = ?
        AND is_deleted = 0
    """

    parameters: list = [user_id]

    if account_id is not None:
        query += """
            AND account_id = ?
        """
        parameters.append(account_id)

    if start_date is not None:
        start_date = validate_transaction_date(
            start_date
        )

        query += """
            AND transaction_date >= ?
        """
        parameters.append(start_date)

    if end_date is not None:
        end_date = validate_transaction_date(
            end_date
        )

        query += """
            AND transaction_date <= ?
        """
        parameters.append(end_date)

    cursor.execute(
        query,
        parameters,
    )

    row = cursor.fetchone()

    connection.close()

    total_income = row["total_income"]
    total_expense = row["total_expense"]

    return {
        "total_income_paise": total_income,
        "total_expense_paise": total_expense,
        "net_cash_flow_paise": (
            total_income - total_expense
        ),
    }
def get_category_summary_raw(
    user_id: int,
    transaction_type: str = "expense",
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict]:
    """
    Return category totals in raw paise.

    Intended for analytics and calculations.
    """

    transaction_type = validate_transaction_type(
        transaction_type
    )

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            categories.id AS category_id,
            categories.name AS category_name,
            COALESCE(
                SUM(transactions.amount),
                0
            ) AS total_amount_paise

        FROM transactions

        LEFT JOIN categories
            ON transactions.category_id = categories.id

        WHERE transactions.user_id = ?
        AND transactions.transaction_type = ?
        AND transactions.is_deleted = 0
    """

    parameters: list = [
        user_id,
        transaction_type,
    ]

    if start_date is not None:
        start_date = validate_transaction_date(
            start_date
        )

        query += """
            AND transactions.transaction_date >= ?
        """

        parameters.append(start_date)

    if end_date is not None:
        end_date = validate_transaction_date(
            end_date
        )

        query += """
            AND transactions.transaction_date <= ?
        """

        parameters.append(end_date)

    query += """
        GROUP BY
            categories.id,
            categories.name

        ORDER BY total_amount_paise DESC
    """

    cursor.execute(
        query,
        parameters,
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "category_id": row["category_id"],
            "category_name": (
                row["category_name"]
                or "Uncategorized"
            ),
            "total_amount_paise": row[
                "total_amount_paise"
            ],
        }
        for row in rows
    ]
