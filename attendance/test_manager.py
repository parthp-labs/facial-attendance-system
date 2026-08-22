from attendance.manager import process_attendance
from database.database import initialize_database
import tempfile
from pathlib import Path


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        database_path = Path(temp_dir) / "test.db"

        initialize_database(database_path)

        person_id = 1
        date = "2026-08-22"

        result = process_attendance(
            person_id,
            date,
            "09:00:00",
            database_path
        )

        print("First:", result)

        result = process_attendance(
            person_id,
            date,
            "17:00:00",
            database_path
        )

        print("Second:", result)

        result = process_attendance(
            person_id,
            date,
            "18:00:00",
            database_path
        )

        print("Third:", result)


if __name__ == "__main__":
    main()
