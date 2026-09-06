import smbus2
from datetime import datetime

"""
0x00 → seconds
0x01 → minutes
0x02 → hours
0x03 → day of week
0x04 → day
0x05 → month
0x06 → year
"""


class RTC:
    DS3231_ADDRESS = 0x68

    def __init__(self, bus_number=1):
        self.bus = smbus2.SMBus(bus_number)

    def _bcd_to_decimal(self, value):
        return (value >> 4) * 10 + (value & 0x0F)

    def _decimal_to_bcd(self, value):
        return ((value // 10) << 4) | (value % 10)

    def get_datetime(self):
        data = self.bus.read_i2c_block_data(self.DS3231_ADDRESS, 0x00, 7)

        second = self._bcd_to_decimal(data[0] & 0x7F)
        minute = self._bcd_to_decimal(data[1] & 0x7F)
        hour = self._bcd_to_decimal(data[2] & 0x3F)

        day = self._bcd_to_decimal(data[4] & 0x3F)
        month = self._bcd_to_decimal(data[5] & 0x1F)
        year = self._bcd_to_decimal(data[6])

        year += 2000

        return datetime(year, month, day, hour, minute, second)

    def get_date(self):
        dt = self.get_datetime()
        return dt.strftime("%Y-%m-%d")

    def get_time(self):
        dt = self.get_datetime()
        return dt.strftime("%H:%M:%S")

    def set_datetime(self, dt):
        data = [self._decimal_to_bcd(dt.second), self._decimal_to_bcd(dt.minute), self._decimal_to_bcd(dt.hour), self._decimal_to_bcd(
            dt.isoweekday()), self._decimal_to_bcd(dt.day), self._decimal_to_bcd(dt.month), self._decimal_to_bcd(dt.year - 2000)]

        self.bus.write_i2c_block_data(self.DS3231_ADDRESS, 0x00, data)

    def close(self):
        self.bus.close()
