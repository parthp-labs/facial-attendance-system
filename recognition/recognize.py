import cv2

from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.recognizer import FaceRecognizer
from recognition.encoding import deserialize_embedding
from database.database import get_all_persons
from attendance.manager import process_attendance
from utils.time import get_current_date, get_current_time
from utils.display import gui_available

DETECTOR_MODEL = (
    "models/face_detection/"
    "face_detection_yunet_2023mar.onnx"
)

RECOGNIZER_MODEL = (
    "models/face_recognition/"
    "face_recognition_sface_2021dec.onnx"
)

SIMILARITY_THRESHOLD = 0.50


def find_best_match(embedding, persons, recognizer):
    best_person = None
    best_similarity = -1.0

    for person in persons:
        person_id, name, face_encoding, sheet_id = person

        stored_embedding = deserialize_embedding(face_encoding)

        similarity = recognizer.compare(embedding, stored_embedding)

        if similarity > best_similarity:
            best_similarity = similarity
            best_person = person

    if (best_person is not None and best_similarity >= SIMILARITY_THRESHOLD):
        return best_person, best_similarity

    return None, best_similarity


def main():
    persons = get_all_persons()

    if not persons:
        print("No registered persons found.")
        return

    detector = FaceDetector(DETECTOR_MODEL)
    recognizer = FaceRecognizer(RECOGNIZER_MODEL)

    camera = Camera()
    camera.start()

    print("Face recognition started.")
    print("Press 'q' to quit.")

    while True:
        frame = camera.read()

        if frame is None:
            continue

        faces = detector.detect(frame)

        for face in faces:
            x, y, w, h = face[:4].astype(int)

            aligned_face = recognizer.align(
                frame,
                face
            )

            embedding = recognizer.get_embedding(
                aligned_face
            )

            person, similarity = find_best_match(
                embedding,
                persons,
                recognizer
            )

            if person is not None:
                person_id, name, _, sheet_id = person

                date = get_current_date()
                current_time = get_current_time()

                action, attendance_id = process_attendance(person_id, date,
                                                           current_time
                                                           )

                label = (f"{name} "f"{similarity:.2f} " f"{action}")

                print(
                    f"Recognized: {name} "f"(similarity={similarity:.3f}) "f"Action={action}")

            else:
                label = (
                    f"Unknown "
                    f"{similarity:.2f}"
                )

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        if gui_available:
            cv2.imshow("Face Recognition", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    camera.stop()
    if gui_available:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
