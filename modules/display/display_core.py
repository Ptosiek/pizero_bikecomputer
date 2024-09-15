import os

from logger import app_logger
from modules.settings import settings

DEFAULT_RESOLUTION = (400, 240)

SUPPORTED_DISPLAYS = {
    # display name, resolution, colors if different from its class default
    "None": None,  # DEFAULT_RESOLUTION
    # MIP Reflective color/mono LCD
    "MIP_JDI_color_400x240": (DEFAULT_RESOLUTION, 8),  # JDI LPM027M128C/LPM027M128B
    "MIP_JDI_color_640x480": ((640, 480), 8),  # JDI LPM044M141A
    "MIP_Azumo_color_272x451": ((272, 451), 64),  # Azumo 14793-06
    "MIP_Sharp_mono_400x240": (DEFAULT_RESOLUTION, 2),  # Sharp LS027B7DH01
    "MIP_Sharp_mono_320x240": ((320, 240), 2),  # Sharp LS044Q7DH01
    "PiTFT": None,
    "Papirus": None,
    "DFRobot_RPi_Display": None,
}


# default display (X window)
class Display:
    has_backlight = False
    has_color = True
    has_touch = True
    send = False

    # current auto brightness status (on/off)
    use_auto_backlight = False
    brightness_index = 0
    brightness_table = None

    def __init__(self, config):
        self.config = config

        if self.has_backlight:
            # set initial status
            self.use_auto_backlight = settings.USE_AUTO_BACKLIGHT

            # set index properly if on
            if self.use_auto_backlight:
                self.brightness_index = len(self.brightness_table)

    @property
    def resolution(self):
        return getattr(self, "size", DEFAULT_RESOLUTION)

    def start_coroutine(self):
        pass

    def quit(self):
        pass

    def update(self, buf, direct_update):
        pass

    def screen_flash_long(self):
        pass

    def screen_flash_short(self):
        pass

    # We can not have auto brightness and an empty brightness table
    def change_brightness(self):
        if self.brightness_table:
            if self.has_backlight:
                self.brightness_index = (self.brightness_index + 1) % (
                    len(self.brightness_table) + 1
                )

                # switch on use_auto_backlight
                if self.brightness_index == len(self.brightness_table):
                    self.use_auto_backlight = True
                # switch off use_auto_backlight and set requested brightness
                else:
                    self.use_auto_backlight = False
                    self.set_brightness(self.brightness_table[self.brightness_index])
            else:
                # else we just loop over the brightness table
                self.brightness_index = (self.brightness_index + 1) % len(
                    self.brightness_table
                )
                self.set_brightness(self.brightness_table[self.brightness_index])

    def set_brightness(self, b):
        pass

    def change_color_low(self):
        pass

    def change_color_high(self):
        pass


def detect_display():
    hatdir = "/proc/device-tree/hat"
    product_file = f"{hatdir}/product"
    vendor_file = f"{hatdir}/vendor"
    if os.path.exists(product_file) and os.path.exists(vendor_file):
        with open(product_file) as f:
            p = f.read()
        with open(vendor_file) as f:
            v = f.read()
        app_logger.info(f"{product_file}: {p}")
        app_logger.info(f"{vendor_file}: {v}")
        # set display
        if p.find("Adafruit PiTFT HAT - 2.4 inch Resistive Touch") == 0:
            return "PiTFT"
        elif (p.find("PaPiRus ePaper HAT") == 0) and (v.find("Pi Supply") == 0):
            return "Papirus"
    return None


def init_display(config):
    # default dummy display

    display, display_name = Display(config), settings.DISPLAY

    if not settings.IS_RASPI:
        display_name = "None"
    else:
        auto_detect = detect_display()

        if auto_detect is not None:
            display_name = auto_detect

        if display_name == "PiTFT":
            from .pitft_28_r import _SENSOR_DISPLAY, PiTFT28r

            if _SENSOR_DISPLAY:
                display = PiTFT28r(config)
        elif display_name.startswith("MIP_"):
            from .mip_display_pigpio import _SENSOR_DISPLAY, MipDisplayPigpio

            if _SENSOR_DISPLAY:
                display = MipDisplayPigpio(config, SUPPORTED_DISPLAYS[display_name])
        elif display_name == "Papirus":
            from .papirus_display import _SENSOR_DISPLAY, PapirusDisplay

            if _SENSOR_DISPLAY:
                display = PapirusDisplay(config)
        elif display_name == "DFRobot_RPi_Display":
            from .dfrobot_rpi_display import _SENSOR_DISPLAY, DFRobotRPiDisplay

            if _SENSOR_DISPLAY:
                display = DFRobotRPiDisplay(config)

    return display, display_name
