from database.database import initialize_database


def main():
    print("Initializing database...")

    initialize_database()

    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
