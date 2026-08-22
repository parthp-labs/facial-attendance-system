import cv2

from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.recognizer import FaceRecognizer


DETECTOR_MODEL = (
    "models/face_detection/"
    "face_detection_yunet_2023mar.onnx"
)

RECOGNIZER_MODEL = (
    "models/face_recognition/"
    "face_recognition_sface_2021dec.onnx"
)


def main():
    camera = Camera()

    detector = FaceDetector(
        DETECTOR_MODEL
    )

    recognizer = FaceRecognizer(
        RECOGNIZER_MODEL
    )

    camera.start()

    print("Face embedding test started.")
    print("Press 'q' to quit.")

    try:
        while True:
            frame = camera.read()

            faces = detector.detect(frame)

            for face in faces:
                x, y, width, height = face[:4]

                x = int(x)
                y = int(y)
                width = int(width)
                height = int(height)

                aligned_face = recognizer.align(
                    frame,
                    face
                )

                embedding = recognizer.get_embedding(
                    aligned_face
                )

                print(
                    "Embedding shape:",
                    embedding.shape
                )

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (255, 0, 0),
                    2,
                )

            cv2.imshow(
                "Face Embedding",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.stop()
        cv2.destroyAllWindows()

        print("Face embedding test stopped.")


if __name__ == "__main__":
    main()
