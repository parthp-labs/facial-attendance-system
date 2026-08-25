from database.database import initialize_database, get_all_persons
from attendance.manager import process_attendance
from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.recognizer import FaceRecognizer
from recognition.recognize import *
import cv2
from utils.display import gui_available
from utils.network import is_internet_available
from google_sync.sync import sync_database
from hardware.lcd import LCD

DETECTOR_MODEL = (
    "models/face_detection/"
    "face_detection_yunet_2023mar.onnx"
)

RECOGNIZER_MODEL = (
    "models/face_recognition/"
    "face_recognition_sface_2021dec.onnx"
)


def main():
    lcd = LCD(address=0x27)

    print("-> Starting Attendance System")
    lcd.show_ready()

    initialize_database()
    print("-> Database initialized successfully.")

    if is_internet_available():
        print("-> Internet available.")
        sync_database()
    else:
        print("-> Internet unavailable. Running offline.")

    persons = get_all_persons()
    camera = Camera()

    detector = FaceDetector(DETECTOR_MODEL)
    recognizer = FaceRecognizer(RECOGNIZER_MODEL)

    display_detected = gui_available()
    camera.start()
    print("-> Camera Started")

    if not display_detected:
        print("-> GUI not detected, running headless")
    try:
        while True:
            frame = camera.read()
            faces = detector.detect(frame)

            for face in faces:
                camera.draw_rect(face, frame)

                lcd.show_recognizing()

                # Aligning Face
                aligned_face = recognizer.align(frame, face)

                # Getting Face Embedding
                embedding = recognizer.get_embedding(aligned_face)

                # Finding a person whose embedding matches
                person, similarity = find_best_match(
                    embedding, persons, recognizer)

                if person is not None:
                    person_id, name, blob, sheet_id = person

                    lcd.show_person(name)
                    date = get_current_date()
                    current_time = get_current_time()

                    lcd.show_welcome(name)

                    # Updating local database
                    action, attendance_id = process_attendance(
                        person_id, date, current_time)

                    label = (
                        f"{name} "
                        f"{similarity:.2f} "
                        f"{action}"
                    )
                    print(
                        f"Recognized: {name} "f"(similarity={similarity:.3f}) "f"Action={action}")

                    if action == "IN":
                        lcd.show_entry()

                    elif action == "OUT":
                        lcd.show_exit()

                    elif action == "IGNORE":
                        pass

                    camera.show_label(face, frame, "label")
                else:
                    label = (f"Unknown "f"{similarity:.2f}")
                    lcd.show_unknown()
                    camera.show_label(face, frame, label)
                    print(label)

            if display_detected:
                cv2.imshow("Attendance", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            # Syncing with Google Sheets
            if cv2.waitKey(1) & 0xFF == ord("s"):
                if is_internet_available():
                    print("-> Internet available.")
                    sync_database()
                else:
                    print("-> Internet unavailable. Running offline.")

    finally:
        camera.stop()
        lcd.close()
        if display_detected:
            cv2.destroyAllWindows()
        print("-> Camera stopped")


if __name__ == "__main__":
    main()
