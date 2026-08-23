from google_sync.sheets import add_attendance_entry


def main():
    add_attendance_entry(
        attendance_id=1,
        sheet_id="1608689730",
        date="2026-08-23",
        entry_time="09:15:00",
        status="IN",
    )

    print("Attendance entry added.")


if __name__ == "__main__":
    main()
