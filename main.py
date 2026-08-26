from database.database import initialize_database, get_all_persons
from attendance.manager import process_attendance
from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.recognizer import FaceRecognizer
from recognition.recognize import *
import cv2
from utils.display import gui_available
from utils.network import is_internet_available
from google_sync.sync import sync_database
from hardware.lcd import LCD
from time import sleep, time
from hardware.led import LEDs
from gpiozero import Button

DETECTOR_MODEL = (
    "models/face_detection/"
    "face_detection_yunet_2023mar.onnx"
)

RECOGNIZER_MODEL = (
    "models/face_recognition/"
    "face_recognition_sface_2021dec.onnx"
)


def main():
    lcd = LCD(address=0x27)
    leds = LEDs(red_pin=17, blue_pin=27, green_pin=22)
    button = Button(10)

    leds.red_on()
    print("-> Starting Attendance System")
    lcd.show_ready()

    # Initializing database
    initialize_database()
    print("-> Database initialized successfully.")

    leds.blue_on()

    # Initiating Google Sheets sync
    if is_internet_available():
        print("-> Internet available.")
        lcd.show_syncing()
        sync_database()
        lcd.show_sync_success()
    else:
        print("-> Internet unavailable. Running offline.")
        lcd.show_offline()

    leds.green_on()
    sleep(2)

    # Loading persons
    lcd.show_ready()

    persons = get_all_persons()
    print(f"-> Loaded {len(persons)} persons.")

    # Initializing Camera
    camera = Camera()

    detector = FaceDetector(DETECTOR_MODEL)
    recognizer = FaceRecognizer(RECOGNIZER_MODEL)

    display_detected = gui_available()

    if not display_detected:
        print("-> GUI not detected, running headless")

    leds.all_off()
    lcd.show_ready()

    try:
        while True:
            # Waiting for button press
            lcd.show_ready()
            print("-> Waiting for button...")
            button.wait_for_press()

            print("-> Button pressed")

            # Starting Camera
            camera.start()
            print("-> Camera Started")

            # Starting recognizing session
            session_start = time()
            session_duration = 30
            session_active = True

            lcd.show_recognizing()
            print("-> Recognition started")

            # Capturing and detecting
            while session_active and time() - session_start < session_duration:
                frame = camera.read()
                faces = detector.detect(frame)
                if len(faces) == 0:
                    print("-> No face detected")
                    lcd.show("Detection Started", "No face")
                    leds.red_on()
                    sleep(2)
                    leds.all_off()
                    continue

                # ------------------------------------------
                # Process detected face
                # ------------------------------------------
                person_recognized = False
                for face in faces:
                    camera.draw_rect(face, frame)

                    # Aligning Face
                    aligned_face = recognizer.align(frame, face)

                    # Getting Face Embedding
                    embedding = recognizer.get_embedding(aligned_face)

                    # Finding a person whose embedding matches
                    person, similarity = find_best_match(
                        embedding, persons, recognizer)

                    # When person is detected
                    if person is not None:
                        person_id, name, blob, sheet_id = person
                        person_recognized = True
                        date = get_current_date()
                        current_time = get_current_time()

                        # Updating local database
                        action, attendance_id, state = process_attendance(
                            person_id, date, current_time)

                        label = (
                            f"{name} "
                            f"{similarity:.2f} "
                            f"{action}"
                        )
                        print(
                            f"Recognized: {name} "f"(similarity={similarity:.3f}) "f"Action={action}")

                        if action == "IN":
                            leds.green_on()
                            lcd.show_welcome(name)
                            sleep(2)
                            lcd.show_entry()
                            sleep(5)
                            session_active = False
                        elif action == "OUT":
                            leds.blue_on()
                            lcd.show_exit()
                            sleep(5)
                            session_active = False
                        elif action == "IGNORE":
                            leds.green_on()
                            if state == "INSIDE":
                                lcd.show("Already Inside", name)
                            elif state == "EXITED":
                                lcd.show("Already Exited", name)

                            sleep(3)
                            session_active = False
                        elif action == "ERROR":
                            leds.red_on()
                            lcd.show_error()
                            sleep(2)
                            print(f"Attendance error for {name}")
                            session_active = False

                        camera.show_label(face, frame, label)
                    else:
                        label = (f"Unknown "f"{similarity:.2f}")
                        camera.show_label(face, frame, label)
                        sleep(2)
                        print(label)
                        lcd.show_unknown()
                        leds.red_on()
                        sleep(2)
                        break

                # Displaying camera frame
                if display_detected:
                    cv2.imshow("Attendance", frame)
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord("q"):
                        break

                    # Syncing with Google Sheets
                    if key == ord("s"):
                        if is_internet_available():
                            print("-> Internet available.")
                            lcd.show_syncing()

                            try:
                                sync_database()
                                lcd.show_sync_success()

                            except Exception as e:
                                print(f"-> Sync failed: {e}")
                                lcd.show_sync_failed()
                        else:
                            print("-> Internet unavailable. Running offline.")
                            lcd.show_offline()

            leds.all_off()
            lcd.show_ready()

            # Stopping camera
            camera.stop()
            print("-> Camera Stopped")

            if display_detected:
                cv2.destroyWindow("Attendance")

            print("-> Recognition session finished")
    finally:
        camera.stop()
        lcd.close()
        button.close()
        if display_detected:
            cv2.destroyAllWindows()
        print("-> Camera stopped")


if __name__ == "__main__":
    main()
