from gpiozero import LED


class LEDs:
    def __init__(self, red_pin=17, blue_pin=27, green_pin=22):
        self.red = LED(red_pin)
        self.blue = LED(blue_pin)
        self.green = LED(green_pin)

    def all_on(self):
        self.red.on()
        self.blue.on()
        self.green.on()

    def all_off(self):
        self.red.off()
        self.blue.off()
        self.green.off()

    def red_on(self):
        self.red.on()

    def blue_on(self):
        self.blue.on()

    def green_on(self):
        self.green.on()

    def close(self):
        self.all_off()
