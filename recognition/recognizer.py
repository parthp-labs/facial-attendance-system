import cv2


class FaceRecognizer:
    def __init__(self, model_path):
        self.recognizer = cv2.FaceRecognizerSF.create(
            model_path,
            ""
        )

    def align(self, frame, face):
        return self.recognizer.alignCrop(
            frame,
            face
        )

    def get_embedding(self, aligned_face):
        return self.recognizer.feature(
            aligned_face
        )

    def compare(self, embedding1, embedding2):
        return self.recognizer.match(
            embedding1,
            embedding2,
            cv2.FaceRecognizerSF_FR_COSINE
        )