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
