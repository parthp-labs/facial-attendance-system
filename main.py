from database.database import (
    initialize_database,
    add_person,
)

from attendance.manager import process_attendance


def main():
    initialize_database()

    person_id = add_person(
        "Rahul",
        b"fake-face-encoding"
    )

    print("Person ID:", person_id)

    result = process_attendance(
        person_id,
        "2026-08-22",
        "09:00:00"
    )

    print("First recognition:", result)

    result = process_attendance(
        person_id,
        "2026-08-22",
        "17:00:00"
    )

    print("Second recognition:", result)

    result = process_attendance(
        person_id,
        "2026-08-22",
        "18:00:00"
    )

    print("Third recognition:", result)


if __name__ == "__main__":
    main()
