from google_sync.sheets import create_person_sheet


def main():
    worksheet = create_person_sheet("Test Person")

    print("Worksheet created successfully.")
    print("Title:", worksheet.title)
    print("ID:", worksheet.id)


if __name__ == "__main__":
    main()
