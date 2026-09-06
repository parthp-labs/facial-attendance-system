from RPLCD.i2c import CharLCD


class LCD:
    def __init__(self, address=0x27):
        self.lcd = CharLCD(
            i2c_expander='PCF8574',
            address=address,
            port=1,
            cols=16,
            rows=2,
            charmap='A00'
        )

        # Cache last displayed content to skip redundant I2C writes (~70ms each)
        self._last_line1 = None
        self._last_line2 = None

    def clear(self):
        self.lcd.clear()
        self._last_line1 = None
        self._last_line2 = None

    def show(self, line1="", line2=""):
        line1 = line1[:16]
        line2 = line2[:16]

        # Skip writing if the display already shows the same content
        if line1 == self._last_line1 and line2 == self._last_line2:
            return

        self.lcd.clear()

        self.lcd.cursor_pos = (0, 0)
        self.lcd.write_string(line1)

        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(line2)

        self._last_line1 = line1
        self._last_line2 = line2

    def show_ready(self):
        self.show(
            "Attendance",
            "System Ready"
        )

    def show_detected(self, name):
        self.show(
            "Detected:",
            name
        )

    def show_recognizing(self):
        self.show("Waiting For", "Detection")

    def show_unknown(self):
        self.show("Unknown Face", "Access Denied")

    def show_welcome(self, name):
        self.show(
            "Welcome",
            name
        )

    def show_entry(self):
        self.show(
            "Attendance",
            "Entry Recorded"
        )

    def show_exit(self):
        self.show(
            "Attendance",
            "Exit Recorded"
        )

    def show_already_entered(self):
        self.show(
            "Already Marked",
            "Today"
        )

    def show_error(self):
        self.show(
            "System Error",
            "Try Again"
        )

    def show_syncing(self):
        self.show(
            "Google Sheets",
            "Syncing..."
        )

    def show_sync_success(self):
        self.show(
            "Google Sheets",
            "Sync Complete"
        )

    def show_sync_failed(self):
        self.show(
            "Google Sheets",
            "Sync Failed"
        )

    def show_offline(self):
        self.show(
            "Internet",
            "Offline Mode"
        )

    def close(self):
        self.lcd.clear()
        self._last_line1 = None
        self._last_line2 = None
