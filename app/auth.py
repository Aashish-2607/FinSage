import hashlib
import os

from app.database.connection import get_connection
from app.categories.manager import create_default_categories


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256."""

    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000,
    )

    return (
        salt.hex()
        + ":"
        + password_hash.hex()
    )


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:
    """Verify a password against its stored hash."""

    try:
        salt_hex, hash_hex = stored_hash.split(":")
    except ValueError:
        return False

    salt = bytes.fromhex(salt_hex)

    expected_hash = bytes.fromhex(hash_hex)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000,
    )

    return password_hash == expected_hash


def register_user(
    name: str,
    email: str,
    password: str,
) -> int:
    """Create a new user and return their user ID."""

    name = name.strip()
    email = email.strip().lower()

    if not name:
        raise ValueError(
            "Name cannot be empty."
        )

    if not email:
        raise ValueError(
            "Email cannot be empty."
        )

    if len(password) < 6:
        raise ValueError(
            "Password must be at least 6 characters."
        )

    password_hash = hash_password(password)

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password_hash,
            ),
        )

        user_id = cursor.lastrowid

        connection.commit()
        connection.close()

        create_default_categories(
            user_id=user_id
        )

        return user_id

    except Exception as error:
        connection.rollback()

        if "UNIQUE constraint failed" in str(error):
            raise ValueError(
                "An account with this email already exists."
            )

        raise

    finally:
        try:
            connection.close()
        except Exception:
            pass


def login_user(
    email: str,
    password: str,
) -> dict | None:
    """Authenticate a user."""

    email = email.strip().lower()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash
        FROM users
        WHERE email = ?
        """,
        (email,),
    )

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return None

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
    }