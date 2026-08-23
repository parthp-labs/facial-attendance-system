import cv2

from camera.camera import Camera
from recognition.detector import FaceDetector
from utils.display import gui_available


MODEL_PATH = (
    "models/face_detection/"
    "face_detection_yunet_2023mar.onnx"
)


def main():
    camera = Camera()
    detector = FaceDetector(MODEL_PATH)

    camera.start()

    print("Face detector started.")
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

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (255, 0, 0),
                    2,
                )

            if gui_available:
                cv2.imshow(
                    "Face Detection",
                    frame
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        camera.stop()
        if gui_available:
            cv2.destroyAllWindows()

        print("Face detector stopped.")


if __name__ == "__main__":
    main()
