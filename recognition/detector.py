import cv2


class FaceDetector:
    def __init__(
        self,
        model_path,
        input_size=(320, 240),
        score_threshold=0.9,
        nms_threshold=0.3,
    ):
        self.input_size = input_size
        self.detector = cv2.FaceDetectorYN.create(
            model_path,
            "",
            input_size,
            score_threshold,
            nms_threshold,
        )

    def detect(self, frame):
        if frame is None or frame.size == 0:
            return []

        orig_h, orig_w = frame.shape[:2]
        det_w, det_h = self.input_size

        # If frame is larger than detection size, downscale for faster inference
        if (orig_w, orig_h) != (det_w, det_h):
            resized_frame = cv2.resize(frame, (det_w, det_h))
            self.detector.setInputSize((det_w, det_h))
            _, faces = self.detector.detect(resized_frame)

            if faces is None or len(faces) == 0:
                return []

            # Scale bounding boxes and landmark coordinates back to original resolution
            scale_x = orig_w / det_w
            scale_y = orig_h / det_h

            faces = faces.copy()
            # Bounding box: x, y, width, height
            faces[:, [0, 2]] *= scale_x
            faces[:, [1, 3]] *= scale_y
            # 5 facial landmarks: 5 pairs of (x, y) coordinates
            faces[:, 4:14:2] *= scale_x
            faces[:, 5:14:2] *= scale_y

            return faces
        else:
            self.detector.setInputSize((orig_w, orig_h))
            _, faces = self.detector.detect(frame)

            if faces is None or len(faces) == 0:
                return []

            return faces
