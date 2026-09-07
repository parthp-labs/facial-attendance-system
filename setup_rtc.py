from hardware.rtc import RTC
from datetime import datetime

rtc = RTC()

now = datetime.now()
rtc.set_datetime(now)

print("RTC set to:", rtc.get_datetime())

rtc.close()
