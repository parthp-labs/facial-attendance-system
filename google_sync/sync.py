from database.database import (
    get_unsynced_attendance,
    mark_attendance_synced,
)

from google_sync.sheets import (
    add_attendance_entry,
    update_attendance_exit,
)


def sync_database():
    records = get_unsynced_attendance()

    if not records:
        return

    print(f"-> Syncing {len(records)} attendance record(s)...")

    for record in records:
        (attendance_id, person_id, date, entry_time,
         exit_time, name, sheet_id) = record

        if not sheet_id:
            print(
                f"-> No sheet ID for {name}, "f"skipping attendance {attendance_id}")

            continue

        try:
            if exit_time is None:
                add_attendance_entry(
                    sheet_id, attendance_id, date, entry_time, status="IN")

            else:
                success = update_attendance_exit(
                    sheet_id, attendance_id, exit_time, status="OUT",)

                if not success:
                    add_attendance_entry(
                        sheet_id, attendance_id, date, entry_time, exit_time, status="OUT")

            mark_attendance_synced(attendance_id)

            print(
                f"-> Synced attendance {attendance_id} "
                f"for {name}"
            )

        except Exception as error:
            print(
                f"-> Failed to sync attendance "
                f"{attendance_id}: {error}"
            )
