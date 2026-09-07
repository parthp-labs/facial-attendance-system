from database.database import (
    get_unsynced_attendance,
    mark_attendance_synced,
    update_sheet_id,
)

from google_sync.sheets import (
    add_attendance_entry,
    update_attendance_exit,
    create_person_sheet,
    SheetNotFoundError,
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
            try:
                worksheet = create_person_sheet(name, reuse_existing=True)
                sheet_id = str(worksheet.id)
                update_sheet_id(person_id, sheet_id)
                print(f"-> Linked sheet ID {sheet_id} for {name}")
            except Exception as sheet_err:
                print(
                    f"-> No sheet ID for {name} and could not link Google Sheet: {sheet_err}, "
                    f"skipping attendance {attendance_id}"
                )
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

        except SheetNotFoundError:
            # Worksheet ID was deleted or changed in Google Sheets; re-link by name
            print(f"-> Sheet ID {sheet_id} for {name} missing. Re-linking worksheet...")
            try:
                worksheet = create_person_sheet(name, reuse_existing=True)
                new_sheet_id = str(worksheet.id)
                update_sheet_id(person_id, new_sheet_id)

                if exit_time is None:
                    add_attendance_entry(
                        new_sheet_id, attendance_id, date, entry_time, status="IN")
                else:
                    success = update_attendance_exit(
                        new_sheet_id, attendance_id, exit_time, status="OUT")
                    if not success:
                        add_attendance_entry(
                            new_sheet_id, attendance_id, date, entry_time, exit_time, status="OUT")

                mark_attendance_synced(attendance_id)
                print(f"-> Re-linked sheet ID {new_sheet_id} and synced attendance {attendance_id} for {name}")
            except Exception as retry_err:
                print(f"-> Failed to re-link and sync attendance {attendance_id}: {retry_err}")

        except Exception as error:
            print(
                f"-> Failed to sync attendance "
                f"{attendance_id}: {error}"
            )
