import sys
import select
import tty
import termios
import cv2

from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.recognizer import FaceRecognizer
from recognition.encoding import serialize_embedding
from database.database import (
    add_person,
    update_sheet_id,
    get_person_by_name,
    update_person_face_encoding,
)
from utils.display import gui_available
from google_sync.sheets import create_person_sheet

DETECTOR_MODEL = "models/face_detection/face_detection_yunet_2023mar.onnx"
RECOGNIZER_MODEL = "models/face_recognition/face_recognition_sface_2021dec.onnx"


def is_keypress_waiting():
    # Returns True if terminal has a key waiting to be read.
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def main():
    detector = FaceDetector(DETECTOR_MODEL)
    recognizer = FaceRecognizer(RECOGNIZER_MODEL)

    camera = Camera()
    camera.start()
    print("-> Camera initialized.")

    display_detected = gui_available()

    # Save terminal settings to revert later
    old_settings = termios.tcgetattr(sys.stdin)

    try:
        registered_count = 0

        while True:
            # Ensure terminal is in canonical mode for input()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            termios.tcflush(sys.stdin, termios.TCIFLUSH)

            print("\n" + "=" * 45)
            print("         PERSON REGISTRATION")
            print("=" * 45)
            name = input(
                "Enter person's name (or press Enter / 'q' to quit): ").strip()

            if not name or name.lower() == "q":
                print("\nRegistration session finished.")
                print(
                    f"Total persons registered/updated this session: {registered_count}")
                break

            existing = get_person_by_name(name)
            update_mode = False
            target_person_id = None
            existing_sheet_id = None

            if existing:
                print(
                    f"\n[Notice] A person named '{name}' is already registered (ID: {existing[0]})."
                )
                print("  [1] Update face embedding for this existing person")
                print("  [2] Enter a different name")
                print("  [3] Cancel and return to menu")
                choice = input("Enter choice [1/2/3]: ").strip()
                if choice == "1":
                    update_mode = True
                    target_person_id = existing[0]
                    existing_sheet_id = existing[3]
                elif choice == "2":
                    continue
                else:
                    print("Registration skipped for this person.")
                    continue

            print(f"\nRegistering: {name}")
            print("Look at the camera.")
            print("Press SPACE or 's' to capture & register.")
            print("Press 'q' to cancel and return to menu.\n")

            # Flush stale frames so camera captures live view immediately
            camera.flush()

            try:
                # Set terminal to raw mode to catch single characters without 'Enter'
                tty.setcbreak(sys.stdin.fileno())

                while True:
                    frame = camera.read()
                    if frame is None:
                        continue

                    faces = detector.detect(frame)

                    # Only do drawing if a display is present
                    if display_detected:
                        for face in faces:
                            x, y, w, h = face[:4].astype(int)
                            cv2.rectangle(
                                frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.imshow("Face Registration", frame)
                        gui_key = cv2.waitKey(1) & 0xFF
                    else:
                        gui_key = 255

                    # Input handling from terminal or GUI window
                    key = None
                    if is_keypress_waiting():
                        key = sys.stdin.read(1)
                    elif gui_key in (ord(" "), ord("s")):
                        key = "s"
                    elif gui_key in (ord("q"), 27):  # 27 is ESC
                        key = "q"

                    if key == "q":
                        print(f"\rRegistration cancelled for {name}.")
                        break

                    if key in (" ", "s"):
                        if len(faces) != 1:
                            print(
                                f"\r[Error] Exactly one face must be visible. Found: {len(faces)}"
                            )
                            continue

                        face = faces[0]
                        aligned_face = recognizer.align(frame, face)
                        embedding = recognizer.get_embedding(aligned_face)
                        face_encoding = serialize_embedding(embedding)

                        sheet_id = existing_sheet_id
                        try:
                            worksheet = create_person_sheet(
                                name, reuse_existing=True)
                            sheet_id = str(worksheet.id)
                            print(
                                f"\rGoogle worksheet linked: {worksheet.title} (ID: {sheet_id})"
                            )
                        except Exception as e:
                            print(
                                f"\r[Notice] Could not link Google Sheets ({e}). Registration will proceed locally.")

                        if update_mode:
                            update_person_face_encoding(
                                target_person_id, face_encoding
                            )
                            if sheet_id and sheet_id != existing_sheet_id:
                                update_sheet_id(target_person_id, sheet_id)
                            print(
                                f"\rSuccessfully updated face embedding for {name} (ID: {target_person_id})")
                        else:
                            person_id = add_person(
                                name, face_encoding, sheet_id=sheet_id,)
                            print(
                                f"\rPerson registered successfully: {name} (ID: {person_id})")

                        registered_count += 1
                        break

            finally:
                # Restore terminal state after each capture session
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                termios.tcflush(sys.stdin, termios.TCIFLUSH)

    except KeyboardInterrupt:
        print("\n\nRegistration interrupted by user.")

    finally:
        # Always restore terminal state even if code crashes or is interrupted
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        camera.stop()
        if display_detected:
            cv2.destroyAllWindows()
        print("-> Camera stopped. Done.")


if __name__ == "__main__":
    main()
