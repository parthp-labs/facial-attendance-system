import cv2

from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.recognizer import FaceRecognizer
from recognition.encoding import serialize_embedding
from database.database import add_person


DETECTOR_MODEL = (
    "models/face_detection/"
    "face_detection_yunet_2023mar.onnx"
)

RECOGNIZER_MODEL = (
    "models/face_recognition/"
    "face_recognition_sface_2021dec.onnx"
)


def main():
    name = input("Enter person's name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    detector = FaceDetector(DETECTOR_MODEL)
    recognizer = FaceRecognizer(RECOGNIZER_MODEL)

    camera = Camera()
    camera.start()

    print("Look at the camera.")
    print("Press SPACE to register.")
    print("Press Q to cancel.")

    while True:
        frame = camera.read()

        if frame is None:
            continue

        faces = detector.detect(frame)

        for face in faces:
            x, y, w, h = face[:4].astype(int)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        cv2.imshow("Face Registration", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("Registration cancelled.")
            break

        if key == ord(" "):
            if len(faces) != 1:
                print("Exactly one face must be visible.")
                continue

            face = faces[0]

            aligned_face = recognizer.align(
                frame,
                face
            )

            embedding = recognizer.get_embedding(
                aligned_face
            )

            face_encoding = serialize_embedding(
                embedding
            )

            person_id = add_person(
                name,
                face_encoding
            )

            print(
                f"Person registered successfully."
                f" ID: {person_id}"
            )

            break

    camera.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
