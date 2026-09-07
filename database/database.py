import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "attendance.db"


class DatabaseError(Exception):
    """General database error."""
    pass


class AttendanceAlreadyExistsError(DatabaseError):
    """Attendance already exists for this person and date."""
    pass


class PersonAlreadyExistsError(DatabaseError):
    """Person with this name already exists."""
    pass


class PersonNotFoundError(DatabaseError):
    """Person with the given ID or name was not found."""
    pass


def get_connection(database_path=DATABASE_PATH):
    try:
        connection = sqlite3.connect(database_path, timeout=10.0)
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection
    except sqlite3.Error as e:
        raise DatabaseError(f"Could not connect to database: {e}") from e


def initialize_database(database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                face_encoding BLOB NOT NULL,
                sheet_id TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                synced INTEGER NOT NULL DEFAULT 0,

                FOREIGN KEY (person_id)
                    REFERENCES persons(id),

                UNIQUE (person_id, date)
            )
        """)

        connection.commit()

    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        raise DatabaseError(
            f"Failed to initialize database: {e}"
        ) from e

    finally:
        if connection:
            connection.close()


def get_unsynced_attendance(database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                attendance.id,
                attendance.person_id,
                attendance.date,
                attendance.entry_time,
                attendance.exit_time,
                persons.name,
                persons.sheet_id
            FROM attendance
            JOIN persons
                ON attendance.person_id = persons.id
            WHERE attendance.synced = 0
            ORDER BY attendance.id
        """)

        return cursor.fetchall()

    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to get unsynced attendance: {e}") from e
    finally:
        if connection:
            connection.close()


def mark_attendance_synced(attendance_id, database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE attendance
            SET synced = 1
            WHERE id = ?
        """, (attendance_id,))

        connection.commit()

    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        raise DatabaseError(
            f"Failed to mark attendance as synced: {e}"
        ) from e

    finally:
        if connection:
            connection.close()


def add_person(name, face_encoding, database_path=DATABASE_PATH, sheet_id=None, allow_duplicate=False):
    name = str(name).strip()
    if not name:
        raise ValueError("Person name cannot be empty.")

    if not allow_duplicate:
        existing = get_person_by_name(name, database_path)
        if existing:
            raise PersonAlreadyExistsError(
                f"Person with name '{name}' already exists (ID: {existing[0]})."
            )

    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO persons (
                name,
                face_encoding,
                sheet_id
            )
            VALUES (?, ?, ?)
        """, (name, face_encoding, sheet_id))

        person_id = cursor.lastrowid

        connection.commit()

        return person_id

    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        raise DatabaseError(
            f"Failed to add person: {e}"
        ) from e

    finally:
        if connection:
            connection.close()


def update_person_face_encoding(person_id, face_encoding, database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE persons
            SET face_encoding = ?
            WHERE id = ?
        """, (face_encoding, person_id))

        if cursor.rowcount == 0:
            raise PersonNotFoundError(f"Person ID {person_id} does not exist.")

        connection.commit()

    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        raise DatabaseError(
            f"Failed to update face encoding for person {person_id}: {e}"
        ) from e

    finally:
        if connection:
            connection.close()


def delete_person(person_id, database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM persons WHERE id = ?", (person_id,))

        if cursor.rowcount == 0:
            raise PersonNotFoundError(f"Person ID {person_id} does not exist.")

        connection.commit()

    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        raise DatabaseError(
            f"Failed to delete person {person_id}: {e}"
        ) from e

    finally:
        if connection:
            connection.close()


def get_person(person_id, database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                face_encoding,
                sheet_id
            FROM persons
            WHERE id = ?
        """, (person_id,))

        return cursor.fetchone()
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to get person: {e}"
        ) from e
    finally:
        if connection:
            connection.close()


def get_person_by_name(name, database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                face_encoding,
                sheet_id
            FROM persons
            WHERE name = ?
        """, (name,))

        return cursor.fetchone()
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to get person by name: {e}"
        ) from e
    finally:
        if connection:
            connection.close()


def get_all_persons(database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                face_encoding,
                sheet_id
            FROM persons
            ORDER BY id
        """)

        return cursor.fetchall()
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to get persons: {e}"
        ) from e
    finally:
        if connection:
            connection.close()


def get_today_attendance(person_id, date, database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                person_id,
                date,
                entry_time,
                exit_time,
                synced
            FROM attendance
            WHERE person_id = ?
            AND date = ?
        """, (person_id, date))

        return cursor.fetchone()
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to get today's attendance: {e}"
        ) from e
    finally:

        if connection:
            connection.close()


def create_entry(person_id, date, entry_time, database_path=DATABASE_PATH):
    connection = None
    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO attendance (
                person_id,
                date,
                entry_time
            )
            VALUES (?, ?, ?)
        """, (
            person_id,
            date,
            entry_time
        ))

        attendance_id = cursor.lastrowid
        connection.commit()
        return attendance_id
    except sqlite3.IntegrityError as e:
        if connection:
            connection.rollback()

        # UNIQUE(person_id, date)
        if "UNIQUE constraint failed" in str(e):
            raise AttendanceAlreadyExistsError(
                "Attendance already exists for "f"person {person_id} on {date}") from e

        raise DatabaseError(f"Database integrity error: {e}") from e

    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        raise DatabaseError(f"Failed to create entry: {e}") from e
    finally:
        if connection:
            connection.close()


def create_exit(attendance_id, exit_time, database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE attendance
            SET
                exit_time = ?,
                synced = 0
            WHERE id = ?
        """, (exit_time, attendance_id))

        if cursor.rowcount == 0:
            raise DatabaseError(
                f"Attendance ID {attendance_id} ""does not exist.")

        connection.commit()

    except DatabaseError:
        if connection:
            connection.rollback()
        raise

    except sqlite3.Error as e:

        if connection:
            connection.rollback()

        raise DatabaseError(f"Failed to create exit: {e}") from e

    finally:
        if connection:
            connection.close()


def update_sheet_id(person_id, sheet_id, database_path=DATABASE_PATH):
    connection = None

    try:
        connection = get_connection(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE persons
            SET sheet_id = ?
            WHERE id = ?
        """, (
            sheet_id,
            person_id
        ))

        if cursor.rowcount == 0:
            raise DatabaseError(
                f"Person ID {person_id} does not exist."
            )

        connection.commit()
    except DatabaseError:
        if connection:
            connection.rollback()
        raise
    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        raise DatabaseError(f"Failed to update sheet ID: {e}") from e

    finally:
        if connection:
            connection.close()
