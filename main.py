from database.database import (
    initialize_database,
    get_all_persons,

)

from attendance.manager import process_attendance
from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.recognizer import FaceRecognizer
from recognition.recognize import *
import cv2

DETECTOR_MODEL = (
    "models/face_detection/"
    "face_detection_yunet_2023mar.onnx"
)

RECOGNIZER_MODEL = (
    "models/face_recognition/"
    "face_recognition_sface_2021dec.onnx"
)


def main():
    print("-> Starting Attendance System")

    initialize_database()
    print("-> Database initialized successfully.")

    persons = get_all_persons()
    camera = Camera()

    detector = FaceDetector(DETECTOR_MODEL)
    recognizer = FaceRecognizer(RECOGNIZER_MODEL)

    camera.start()
    print("-> Camera Started")
    try:
        while True:
            frame = camera.read()
            faces = detector.detect(frame)

            for face in faces:
                camera.draw_rect(face, frame)

                # Aligning Face
                aligned_face = recognizer.align(frame, face)

                # Getting Face Embedding
                embedding = recognizer.get_embedding(aligned_face)

                # Finding a person whose embedding matches
                person, similarity = find_best_match(
                    embedding, persons, recognizer)

                if person is not None:
                    person_id, name, blob = person

                    date = get_current_date()
                    current_time = get_current_time()

                    action, attendance_id = process_attendance(
                        person_id, date, current_time)

                    label = (
                        f"{name} "
                        f"{similarity:.2f} "
                        f"{action}"
                    )
                    print(
                        f"Recognized: {name} "f"(similarity={similarity:.3f}) "f"Action={action}")

                    camera.show_label(face, frame, label)
                else:
                    label = (f"Unknown "f"{similarity:.2f}")
                    camera.show_label(face, frame, label)
                    print(label)

            cv2.imshow("Attendance", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.stop()
        cv2.destroyAllWindows()
        print("-> Camera stopped")


if __name__ == "__main__":
    main()
