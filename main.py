from database.database import (
    initialize_database,
    add_person,
    get_person,
    get_person_by_name,
    get_all_persons,
)


def main():
    initialize_database()

    # Dummy face encoding for testing
    fake_encoding = b"fake-face-encoding"

    person_id = add_person("Rahul", fake_encoding)

    print("Created person:", person_id)

    person = get_person(person_id)
    print("Person by ID:", person)

    person = get_person_by_name("Rahul")
    print("Person by name:", person)

    persons = get_all_persons()
    print("All persons:")

    for person in persons:
        print(person)


if __name__ == "__main__":
    main()
