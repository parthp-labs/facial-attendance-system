import cv2

from camera.camera import Camera


def main():
    camera = Camera()

    camera.start()

    print("Camera started.")
    print("Press 'q' to quit.")

    try:
        while True:
            frame = camera.read()

            cv2.imshow("Attendance Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.stop()
        cv2.destroyAllWindows()

        print("Camera stopped.")


if __name__ == "__main__":
    main()
