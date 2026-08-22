import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "attendance.db"


def get_connection(database_path=DATABASE_PATH):
    return sqlite3.connect(DATABASE_PATH)


def initialize_database(database_path=DATABASE_PATH):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            face_encoding BLOB NOT NULL
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
    connection.close()


def add_person(name, face_encoding, database_path=DATABASE_PATH):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO persons (name, face_encoding)
        VALUES (?, ?)
        """,
        (name, face_encoding)
    )

    person_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return person_id


def get_person(person_id, database_path=DATABASE_PATH):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, face_encoding
        FROM persons
        WHERE id = ?
        """,
        (person_id,)
    )

    person = cursor.fetchone()

    connection.close()

    return person


def get_person_by_name(name, database_path=DATABASE_PATH):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, face_encoding
        FROM persons
        WHERE name = ?
        """,
        (name,)
    )

    person = cursor.fetchone()

    connection.close()

    return person


def get_all_persons(database_path=DATABASE_PATH):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, face_encoding
        FROM persons
        ORDER BY id
        """
    )

    persons = cursor.fetchall()

    connection.close()

    return persons


def get_today_attendance(person_id, date, database_path=DATABASE_PATH):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, person_id, date, entry_time, exit_time, synced
        FROM attendance
        WHERE person_id = ? AND date = ?
        """,
        (person_id, date)
    )

    attendance = cursor.fetchone()

    connection.close()

    return attendance


def create_entry(person_id, date, entry_time, database_path=DATABASE_PATH):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO attendance (
            person_id,
            date,
            entry_time
        )
        VALUES (?, ?, ?)
        """,
        (person_id, date, entry_time)
    )

    attendance_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return attendance_id


def create_exit(attendance_id, exit_time, database_path=DATABASE_PATH):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE attendance
        SET exit_time = ?, synced = 0
        WHERE id = ?
        """,
        (exit_time, attendance_id)
    )

    connection.commit()
    connection.close()
