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

    def clear(self):
        self.lcd.clear()

    def show(self, line1="", line2=""):
        self.lcd.clear()

        self.lcd.cursor_pos = (0, 0)
        self.lcd.write_string(line1[:16])

        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(line2[:16])

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
        self.show(
            "Face Detected",
            "Recognizing..."
        )

    def show_unknown(self):
        self.show(
            "Unknown Face",
            "Access Denied"
        )

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
