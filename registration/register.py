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
    name = input("Enter person's name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    existing = get_person_by_name(name)
    update_mode = False
    target_person_id = None
    existing_sheet_id = None

    if existing:
        print(
            f"\n[Notice] A person named '{name}' is already registered (ID: {existing[0]})."
        )
        print("  [1] Update face embedding for this existing person")
        print("  [2] Cancel registration")
        choice = input("Enter choice [1/2]: ").strip()
        if choice == "1":
            update_mode = True
            target_person_id = existing[0]
            existing_sheet_id = existing[3]
        else:
            print("Registration cancelled.")
            return

    detector = FaceDetector(DETECTOR_MODEL)
    recognizer = FaceRecognizer(RECOGNIZER_MODEL)

    camera = Camera()
    camera.start()

    print("\nLook at the camera.")
    print("Press SPACE or 's' to register.")
    print("Press 'q' to cancel.\n")

    # Save terminal settings to revert later
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        # Set terminal to raw mode to catch single characters without 'Enter'
        tty.setcbreak(sys.stdin.fileno())

        while True:
            frame = camera.read()
            if frame is None:
                continue

            faces = detector.detect(frame)

            # Only do drawing if a display is present
            if gui_available():
                for face in faces:
                    x, y, w, h = face[:4].astype(int)
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)
                cv2.imshow("Face Registration", frame)
                cv2.waitKey(1)

            # Headless-safe input handling
            key = None
            if is_keypress_waiting():
                key = sys.stdin.read(1)

            if key == "q":
                print("\rRegistration cancelled.")
                break

            if key in (" ", "s"):
                if len(faces) != 1:
                    print(
                        f"\r[Error] Exactly one face must be visible. Found: {len(faces)}")
                    continue

                face = faces[0]
                aligned_face = recognizer.align(frame, face)
                embedding = recognizer.get_embedding(aligned_face)
                face_encoding = serialize_embedding(embedding)

                sheet_id = existing_sheet_id
                try:
                    worksheet = create_person_sheet(name, reuse_existing=True)
                    sheet_id = str(worksheet.id)
                    print(
                        f"\rGoogle worksheet linked: {worksheet.title} (ID: {sheet_id})")
                except Exception as e:
                    print(
                        f"\r[Notice] Could not link Google Sheets ({e}). Registration will proceed locally."
                    )

                if update_mode:
                    update_person_face_encoding(
                        target_person_id, face_encoding)
                    if sheet_id and sheet_id != existing_sheet_id:
                        update_sheet_id(target_person_id, sheet_id)
                    print(
                        f"\rSuccessfully updated face embedding for {name} (ID: {target_person_id})"
                    )
                else:
                    person_id = add_person(
                        name,
                        face_encoding,
                        sheet_id=sheet_id,
                    )
                    print(
                        f"\rPerson registered successfully: {name} (ID: {person_id})"
                    )

                break

    finally:
        # Always restore terminal state even if code crashes
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    camera.stop()
    if gui_available():
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
