import pytest

from database.database import (
    initialize_database,
    add_person,
    get_today_attendance,
)

from attendance.manager import process_attendance


@pytest.fixture
def database(tmp_path):
    database_path = tmp_path / "test.db"

    initialize_database(database_path)

    return database_path


@pytest.fixture
def person(database):
    return add_person(
        "Rahul",
        b"fake-face-encoding",
        database
    )


def test_first_recognition_records_in(database, person):
    result = process_attendance(
        person,
        "2026-08-22",
        "09:00:00",
        database
    )

    assert result[0] == "IN"


def test_second_recognition_records_out(database, person):
    process_attendance(
        person,
        "2026-08-22",
        "09:00:00",
        database
    )

    result = process_attendance(
        person,
        "2026-08-22",
        "17:00:00",
        database
    )

    assert result[0] == "OUT"


def test_third_recognition_is_ignored(database, person):
    process_attendance(
        person,
        "2026-08-22",
        "09:00:00",
        database
    )

    process_attendance(
        person,
        "2026-08-22",
        "17:00:00",
        database
    )

    result = process_attendance(
        person,
        "2026-08-22",
        "18:00:00",
        database
    )

    assert result[0] == "IGNORE"


def test_new_day_allows_new_entry(database, person):
    process_attendance(
        person,
        "2026-08-22",
        "09:00:00",
        database
    )

    process_attendance(
        person,
        "2026-08-22",
        "17:00:00",
        database
    )

    result = process_attendance(
        person,
        "2026-08-23",
        "09:00:00",
        database
    )

    assert result[0] == "IN"


def test_entry_and_exit_times_are_stored(database, person):
    process_attendance(
        person,
        "2026-08-22",
        "09:00:00",
        database
    )

    process_attendance(
        person,
        "2026-08-22",
        "17:00:00",
        database
    )

    attendance = get_today_attendance(
        person,
        "2026-08-22",
        database
    )

    assert attendance[3] == "09:00:00"
    assert attendance[4] == "17:00:00"
