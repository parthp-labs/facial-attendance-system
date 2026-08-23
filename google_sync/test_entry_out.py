from google_sync.sheets import update_attendance_exit


def main():
    success = update_attendance_exit(
        attendance_id="out",
        sheet_id="1608689730",
        date="2026-08-23",
        exit_time="17:42:03",
    )

    print("Exit updated:", success)


if __name__ == "__main__":
    main()
