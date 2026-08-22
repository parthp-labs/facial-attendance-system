import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "attendance.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
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


def add_person(name, face_encoding):
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


def get_person(person_id):
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


def get_person_by_name(name):
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


def get_all_persons():
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
