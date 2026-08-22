import cv2


class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.capture = None

    def start(self):
        self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():
            raise RuntimeError(
                f"Could not open camera {self.camera_index}"
            )

    def draw_rect(self, face, frame, color=(255, 0, 0)):
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

    def show_label(self, face, frame, label):
        x, y, width, height = face[:4]

        x = int(x)
        y = int(y)
        width = int(width)
        self.draw_rect(face, frame)

        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    def read(self):
        if self.capture is None:
            raise RuntimeError("Camera has not been started")

        success, frame = self.capture.read()

        if not success:
            raise RuntimeError("Could not read frame from camera")

        return frame

    def stop(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
