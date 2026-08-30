VALID_ACCOUNT_TYPES = {
    "savings",
    "current",
    "credit_card",
    "cash",
    "wallet",
    "investment",
}


def validate_account_type(account_type: str) -> str:
    """
    Validate and normalize an account type.
    """

    account_type = account_type.strip().lower()

    if account_type not in VALID_ACCOUNT_TYPES:
        raise ValueError(
            f"Invalid account type: {account_type}"
        )

    return account_type