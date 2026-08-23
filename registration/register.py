import sys
import select
import tty
import termios
import cv2

from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.recognizer import FaceRecognizer
from recognition.encoding import serialize_embedding
from database.database import add_person, update_sheet_id
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
            print(gui_available)
            # Only do drawing if a display is present
            if gui_available:
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

                person_id = add_person(name, face_encoding)
                worksheet = create_person_sheet(name)
                update_sheet_id(person_id, str(worksheet.id))

                print(f"\rRegistered {name}")
                print(f"Google worksheet created: {worksheet.title}")
                print(f"Sheet ID: {worksheet.id}")
                print(f"Person registered successfully. ID: {person_id}")
                break

    finally:
        # Always restore terminal state even if code crashes
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    camera.stop()
    if gui_available:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
