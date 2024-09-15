import time

from logger import app_logger
from modules.settings import settings
from .sensor import Sensor


# GPIO Button
_SENSOR_RPiGPIO = False
try:
    import RPi.GPIO as GPIO

    _SENSOR_RPiGPIO = True
except ImportError:
    pass

if _SENSOR_RPiGPIO:
    app_logger.info("GPIO")


class SensorGPIO(Sensor):
    buttonState = {}
    oldButtonState = {}
    interval = 0.01
    interval_inv = int(1 / interval)
    mode = "MAIN"

    def sensor_init(self):
        if _SENSOR_RPiGPIO and settings.DISPLAY in [
            "PiTFT",
            "Papirus",
            "DFRobot_RPi_Display",
        ]:
            for key in self.config.button_config.G_BUTTON_DEF[settings.DISPLAY][
                "MAIN"
            ].keys():
                self.buttonState[key] = False
                self.oldButtonState[key] = True
                if settings.DISPLAY in ("PiTFT", "DFRobot_RPi_Display"):
                    GPIO.setup(key, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                elif settings.DISPLAY in ("Papirus",):
                    GPIO.setup(key, GPIO.IN)

    def my_callback(self, channel):
        sw_counter = 0

        while True:
            sw_status = GPIO.input(channel)

            if sw_status == 0:
                sw_counter = sw_counter + 1
                if (
                    sw_counter
                    >= self.config.button_config.G_BUTTON_LONG_PRESS * self.interval_inv
                ):
                    self.config.button_config.press_button(
                        settings.DISPLAY, channel, 1
                    )  # long press
                    break
            else:
                self.config.button_config.press_button(settings.DISPLAY, channel, 0)
                break
            time.sleep(self.interval)

    def update(self):
        if _SENSOR_RPiGPIO and settings.DISPLAY in (
            "PiTFT",
            "Papirus",
            "DFRobot_RPi_Display",
        ):
            for key in self.config.button_config.G_BUTTON_DEF[settings.DISPLAY][
                "MAIN"
            ].keys():
                GPIO.add_event_detect(
                    key, GPIO.FALLING, callback=self.my_callback, bouncetime=500
                )

    def quit(self):
        if _SENSOR_RPiGPIO:
            GPIO.cleanup()
