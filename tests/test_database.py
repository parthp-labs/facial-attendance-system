import pytest
from database.database import (
    initialize_database,
    add_person,
    get_person,
    get_person_by_name,
    update_person_face_encoding,
    delete_person,
    PersonAlreadyExistsError,
    PersonNotFoundError,
)


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_db.db"
    initialize_database(db_file)
    return db_file


def test_add_person_success(test_db):
    person_id = add_person("Alice", b"encoding_1", test_db)
    assert person_id is not None
    person = get_person(person_id, test_db)
    assert person[1] == "Alice"
    assert person[2] == b"encoding_1"
    assert person[3] is None


def test_add_person_duplicate_name_raises_error(test_db):
    add_person("Bob", b"encoding_bob", test_db)
    with pytest.raises(PersonAlreadyExistsError):
        add_person("Bob", b"encoding_bob_2", test_db)


def test_add_person_duplicate_name_allowed_flag(test_db):
    id1 = add_person("Charlie", b"enc_1", test_db)
    id2 = add_person("Charlie", b"enc_2", test_db, allow_duplicate=True)
    assert id1 != id2


def test_add_person_empty_name_raises_error(test_db):
    with pytest.raises(ValueError):
        add_person("   ", b"enc", test_db)


def test_update_person_face_encoding(test_db):
    person_id = add_person("Dave", b"old_enc", test_db)
    update_person_face_encoding(person_id, b"new_enc", test_db)
    person = get_person(person_id, test_db)
    assert person[2] == b"new_enc"


def test_update_nonexistent_person_raises_error(test_db):
    with pytest.raises(PersonNotFoundError):
        update_person_face_encoding(9999, b"enc", test_db)


def test_delete_person(test_db):
    person_id = add_person("Eve", b"enc_eve", test_db)
    assert get_person(person_id, test_db) is not None
    delete_person(person_id, test_db)
    assert get_person(person_id, test_db) is None


def test_delete_nonexistent_person_raises_error(test_db):
    with pytest.raises(PersonNotFoundError):
        delete_person(9999, test_db)
