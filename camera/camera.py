import cv2


class Camera:
    def __init__(self, camera_index=0, width=640, height=480, fps=15):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.capture = None

    def start(self):
        self.capture = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)

        if not self.capture.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_index}")

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)

        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Request FPS (15 FPS cuts MJPEG decoding CPU load in half compared to 30 FPS)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)

        # Request minimal driver buffer size to reduce frame latency
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Use MJPEG if supported by the camera.
        # This reduces USB bandwidth.
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

        # Print actual camera settings
        actual_width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = self.capture.get(cv2.CAP_PROP_FPS)

        print(
            f"-> Camera: "f"{int(actual_width)}x{int(actual_height)} "f"@ {actual_fps:.1f} FPS")

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

    def flush(self, count=5):
        if self.capture is not None and self.capture.isOpened():
            for _ in range(count):
                self.capture.grab()

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
