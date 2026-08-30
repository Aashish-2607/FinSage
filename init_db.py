from app.database.models import initialize_database


def main() -> None:
    initialize_database()

    print("FinSage database initialized successfully.")


if __name__ == "__main__":
    main()