from app.database.connection import get_connection
from app.utils.money import format_rupees


def get_account_balance(
    account_id: int,
    user_id: int,
) -> dict:
    """
    Calculate the current balance of an account.

    Balance =
        opening balance
        + income
        - expenses
    """

    connection = get_connection()
    cursor = connection.cursor()

    # Get the account's opening balance.
    cursor.execute(
        """
        SELECT
            opening_balance
        FROM accounts
        WHERE id = ?
        AND user_id = ?
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
            "Account not found or does not belong to the user."
        )

    opening_balance = account["opening_balance"]

    # Calculate total income.
    cursor.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total_income
        FROM transactions
        WHERE account_id = ?
        AND user_id = ?
        AND transaction_type = 'income'
        AND is_deleted = 0
        """,
        (
            account_id,
            user_id,
        ),
    )

    total_income = cursor.fetchone()["total_income"]

    # Calculate total expenses.
    cursor.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total_expense
        FROM transactions
        WHERE account_id = ?
        AND user_id = ?
        AND transaction_type = 'expense'
        AND is_deleted = 0
        """,
        (
            account_id,
            user_id,
        ),
    )

    total_expense = cursor.fetchone()["total_expense"]

    connection.close()

    current_balance = (
        opening_balance
        + total_income
        - total_expense
    )

    return {
        "account_id": account_id,
        "opening_balance": format_rupees(
            opening_balance
        ),
        "total_income": format_rupees(
            total_income
        ),
        "total_expense": format_rupees(
            total_expense
        ),
        "current_balance": format_rupees(
            current_balance
        ),
    }