from decimal import Decimal, InvalidOperation


def rupees_to_paise(amount: str | int | float | Decimal) -> int:
    """
    Convert rupees to paise for database storage.
    """

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid monetary amount.")

    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    return int(amount * 100)


def paise_to_rupees(amount: int) -> Decimal:
    """
    Convert paise from the database into rupees.
    """

    return Decimal(amount) / Decimal("100")


def format_rupees(amount: int) -> str:
    """
    Convert paise into a user-friendly rupee string.

    Example:
        2500000 -> ₹25,000.00
    """

    rupees = paise_to_rupees(amount)

    return f"₹{rupees:,.2f}"