from datetime import date


VALID_TRANSACTION_TYPES = {
    "income",
    "expense",
}


def validate_transaction_type(
    transaction_type: str,
) -> str:
    """Validate and normalize a transaction type."""

    transaction_type = transaction_type.strip().lower()

    if transaction_type not in VALID_TRANSACTION_TYPES:
        raise ValueError(
            f"Invalid transaction type: {transaction_type}"
        )

    return transaction_type


def validate_amount(amount: str | int | float) -> str:
    """
    Validate a monetary amount.

    The actual conversion to paise is handled
    by the money utility.
    """

    if amount is None:
        raise ValueError("Amount is required.")

    amount = str(amount).strip()

    if not amount:
        raise ValueError("Amount is required.")

    return amount


def validate_transaction_date(
    transaction_date: str,
) -> str:
    """Validate an ISO-format transaction date."""

    try:
        date.fromisoformat(transaction_date)
    except ValueError:
        raise ValueError(
            "Invalid date. Expected format: YYYY-MM-DD."
        )

    return transaction_date