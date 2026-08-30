from app.database.connection import get_connection
from app.utils.money import format_rupees, rupees_to_paise
from app.accounts.validators import validate_account_type


def create_institution(
    user_id: int,
    name: str,
) -> int:
    """
    Create an institution for a user.

    If the institution already exists for that user,
    return the existing institution ID.
    """

    name = name.strip()

    if not name:
        raise ValueError("Institution name cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM institutions
        WHERE user_id = ?
        AND LOWER(name) = LOWER(?)
        """,
        (user_id, name),
    )

    existing = cursor.fetchone()

    if existing:
        connection.close()
        return existing["id"]

    cursor.execute(
        """
        INSERT INTO institutions (
            user_id,
            name
        )
        VALUES (?, ?)
        """,
        (user_id, name),
    )

    institution_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return institution_id


def create_account(
    user_id: int,
    institution_id: int,
    name: str,
    account_type: str,
    opening_balance: str | int | float = 0,
) -> int:
    """
    Create a financial account.

    The balance is accepted in rupees and
    stored internally as paise.
    """

    name = name.strip()
    account_type = validate_account_type(account_type)

    if not name:
        raise ValueError("Account name cannot be empty.")

    if not account_type:
        raise ValueError("Account type cannot be empty.")

    opening_balance_paise = rupees_to_paise(
        opening_balance
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO accounts (
            user_id,
            institution_id,
            name,
            account_type,
            opening_balance,
            is_active
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            institution_id,
            name,
            account_type,
            opening_balance_paise,
            1,
        ),
    )

    account_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return account_id


def get_accounts(user_id: int) -> list[dict]:
    """
    Return all accounts belonging to a user.

    Monetary values are returned in rupees
    formatted for user display.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            accounts.id,
            institutions.name AS institution_name,
            accounts.name AS account_name,
            accounts.account_type,
            accounts.opening_balance,
            accounts.created_at

        FROM accounts

        JOIN institutions
            ON accounts.institution_id = institutions.id

        WHERE accounts.user_id = ?
        AND accounts.is_active = 1

        ORDER BY accounts.created_at
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "institution_name": row["institution_name"],
            "account_name": row["account_name"],
            "account_type": row["account_type"],
            "opening_balance": format_rupees(
                row["opening_balance"]
            ),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
def update_account(
    account_id: int,
    user_id: int,
    name: str | None = None,
    account_type: str | None = None,
) -> None:
    """
    Update account details.

    Only the fields provided by the caller are changed.
    """

    if name is not None:
        name = name.strip()

        if not name:
            raise ValueError("Account name cannot be empty.")

    if account_type is not None:
        account_type = account_type.strip()

        if not account_type:
            raise ValueError("Account type cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET
            name = COALESCE(?, name),
            account_type = COALESCE(?, account_type)
        WHERE id = ?
        AND user_id = ?
        """,
        (
            name,
            account_type,
            account_id,
            user_id,
        ),
    )

    if cursor.rowcount == 0:
        connection.close()

        raise ValueError(
            "Account not found or does not belong to the user."
        )

    connection.commit()
    connection.close()
def deactivate_account(
    account_id: int,
    user_id: int,
) -> None:
    """
    Deactivate an account without deleting financial history.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET is_active = 0
        WHERE id = ?
        AND user_id = ?
        AND is_active = 1
        """,
        (
            account_id,
            user_id,
        ),
    )

    if cursor.rowcount == 0:
        connection.close()

        raise ValueError(
            "Active account not found or does not belong to the user."
        )

    connection.commit()
    connection.close()