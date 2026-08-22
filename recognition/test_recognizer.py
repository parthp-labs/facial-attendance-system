import cv2

from recognition.recognizer import FaceRecognizer


MODEL_PATH = (
    "models/face_recognition/"
    "face_recognition_sface_2021dec_int8bq.onnx"
)


def main():
    recognizer = FaceRecognizer(MODEL_PATH)

    image1 = cv2.imread("test_images/img1.jpg")
    image2 = cv2.imread("test_images/img2.jpg")

    if image1 is None:
        raise RuntimeError("Could not load person1_a.jpg")

    if image2 is None:
        raise RuntimeError("Could not load person1_b.jpg")

    # For this first test, face detections are needed.
    # These will be added in the next step.

    print("SFace model loaded successfully.")


if __name__ == "__main__":
    main()
