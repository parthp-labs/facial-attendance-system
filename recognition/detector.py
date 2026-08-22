import cv2


class FaceDetector:
    def __init__(
        self,
        model_path,
        input_size=(320, 320),
        score_threshold=0.9,
        nms_threshold=0.3,
    ):
        self.detector = cv2.FaceDetectorYN.create(
            model_path,
            "",
            input_size,
            score_threshold,
            nms_threshold,
        )

        self.input_size = input_size

    def detect(self, frame):
        height, width = frame.shape[:2]

        self.detector.setInputSize((width, height))

        _, faces = self.detector.detect(frame)

        if faces is None:
            return []

        return faces
