import argparse
import asyncio
import json
import logging
import os
import yaml
from configparser import ConfigParser
from dataclasses import dataclass

import numpy as np

from logger import app_logger

from .maps import (
    MAP_CONFIG,
    HEATMAP_OVERLAY_MAP_CONFIG,
    RAIN_OVERLAY_MAP_CONFIG,
    WIND_OVERLAY_MAP_CONFIG,
)
from .maps.utils import MapDict

_IS_RASPI = False
UNIT_ID = 0x1A2B3C4D
SETTINGS_FILE = "setting.conf"

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    _IS_RASPI = True

    model = unit = ""

    # Extract serial from cpuinfo file
    with open("/proc/cpuinfo", "r") as f:
        for line in f:
            if line[0:6] == "Serial":
                # include char, not number only
                unit_id = (line.split(":")[1]).replace(" ", "").strip()[-8:]
                UNIT_ID = int(unit_id, 16)
            if line[0:5] == "Model":
                model = (line.split(":")[1]).strip()
            if line[0:8] == "Hardware":
                unit = (line.split(":")[1]).replace(" ", "").strip()

    model_path = "/proc/device-tree/model"
    if model == "" and os.path.exists(model_path):
        with open(model_path, "r") as f:
            model = f.read().replace("\x00", "").strip()

except ImportError:
    pass


@dataclass(frozen=True)
class SettingsNamespace:
    config_parser = ConfigParser(
        default_section="GENERAL",
        converters={
            "lower": lambda x: x.lower(),
            "nparray": lambda x: np.array(json.loads(x)),
            "speed": lambda x: int(x) / 3.6,
            "upper": lambda x: x.upper(),
        },
    )

    IS_RASPI = _IS_RASPI

    #######################
    #  command line args  #
    #######################
    DEBUG = False
    DUMMY_OUTPUT = False
    FULLSCREEN = False
    HEADLESS = False
    LAYOUT_FILE = "layout.yaml"
    VERTICAL = False

    #######################
    # configurable values #
    #######################

    # display type (in h setting.conf)
    DISPLAY = "None"  # PiTFT, MIP, MIP_640, Papirus, MIP_Sharp, MIP_Sharp_320, DFRobot_RPi_Display

    LANG = "EN"
    FONT_FILE = ""

    # loop interval
    SENSOR_INTERVAL = 1.0  # [s] for sensor_core
    ANT_INTERVAL = 1.0  # [s] for ANT+. 0.25, 0.5, 1.0 only.
    I2C_INTERVAL = 1.0  # 0.2 #[s] for I2C (altitude, accelerometer, etc)
    GPS_INTERVAL = 1.0  # [s] for GPS
    DRAW_INTERVAL = 1000  # [ms] for GUI (QtCore.QTimer)
    LOGGING_INTERVAL = 1.0  # [s] for logger_core (log interval)
    REALTIME_GRAPH_INTERVAL = 1000  # 200 #[ms] for pyqt_graph

    # calculate index on course
    COURSE_INDEXING = True

    # average including ZERO when logging
    AVERAGE_INCLUDING_ZERO = {"cadence": False, "power": True}

    # wheel circumference [mm] (overwritten from menu)
    # 700x23c: 2096, 700x25c: 2105, 700x28c: 2136
    WHEEL_CIRCUMFERENCE = 2105

    # auto light: brightness sensor and brake(speed(ANT+/GPS))
    USE_AUTO_LIGHT = False

    # W'bal
    POWER_CP = 150
    POWER_W_PRIME = 15000
    POWER_W_PRIME_ALGORITHM = "WATERWORTH"  # WATERWORTH, DIFFERENTIAL

    ###########################
    # fixed or pointer values #
    ###########################

    # product name, version
    PRODUCT = "Pizero Bikecomputer"
    UNIT_ID = UNIT_ID

    # GUI mode
    GUI_MODE = "PyQt"

    # log setting
    LOG_DIR = "log"
    LOG_DB = os.path.join(LOG_DIR, "log.db")
    LOG_DEBUG_FILE = os.path.join(LOG_DIR, "debug.log")

    # log format switch
    LOG_WRITE_CSV = True
    LOG_WRITE_FIT = True

    # asyncio semaphore and queues
    COROUTINE_SEM = 100
    DOWNLOAD_QUEUE = asyncio.Queue()

    # for map dummy center: Tokyo station in Japan
    DUMMY_POS_X = 139.764710814819
    DUMMY_POS_Y = 35.68188106919333

    # auto backlight
    USE_AUTO_BACKLIGHT = True
    AUTO_BACKLIGHT_CUTOFF = 10

    # external input of maps
    MAP_LIST = "map.yaml"

    # screenshot dir
    SCREENSHOT_DIR = "screenshots"

    # ANT Null value
    ANT_NULLVALUE = np.nan

    # courses
    COURSE_DIR = "courses"
    COURSE_FILE_PATH = os.path.join(COURSE_DIR, ".current")
    CUESHEET_DISPLAY_ON_MAP = True
    CUESHEET_SCROLL = False

    # Graph color by slope
    CLIMB_DISTANCE_CUTOFF = 0.3  # [km]
    CLIMB_GRADE_CUTOFF = 2  # [%]
    SLOPE_CUTOFF = (1, 3, 6, 9, 12, float("inf"))  # by grade
    SLOPE_COLOR = (
        (128, 128, 128),  # gray(base)
        (0, 255, 0),  # green
        (255, 255, 0),  # yellow
        (255, 128, 0),  # orange
        (255, 0, 0),  # red
        (128, 0, 0),  # dark red
    )
    CLIMB_CATEGORY = [
        {"volume": 8000, "name": "Cat4"},
        {"volume": 16000, "name": "Cat3"},
        {"volume": 32000, "name": "Cat2"},
        {"volume": 64000, "name": "Cat1"},
        {"volume": 80000, "name": "HC"},
    ]

    # for search point on course
    GPS_ON_ROUTE_CUTOFF = 50  # [m] TODO generate from course
    GPS_SEARCH_RANGE = 6  # [km] #100km/h -> 27.7m/s
    # degree(30/45/90): 0~GPS_AZIMUTH_CUTOFF, (360-GPS_AZIMUTH_CUTOFF)~GPS_AZIMUTH_CUTOFF
    GPS_AZIMUTH_CUTOFF = (60, 300)
    # for keeping on course seconds
    GPS_KEEP_ON_COURSE_CUTOFF = int(60 / GPS_INTERVAL)  # [s]

    # PerformanceGraph:
    # 1st: POWER
    # 2nd: HR or W_BAL
    GUI_PERFORMANCE_GRAPH_DISPLAY_ITEM = ("POWER", "W_BAL")
    GUI_PERFORMANCE_GRAPH_DISPLAY_RANGE = int(5 * 60 / SENSOR_INTERVAL)  # [s]
    GUI_MIN_HR = 40
    GUI_MAX_HR = 200
    GUI_MIN_POWER = 30
    GUI_MAX_POWER = 300
    GUI_MIN_W_BAL = 0
    GUI_MAX_W_BAL = 100
    # acceleration graph (AccelerationGraphWidget)
    GUI_ACC_TIME_RANGE = int(1 * 60 / (REALTIME_GRAPH_INTERVAL / 1000))  # [s]

    # gross average speed (in setting.conf)
    GROSS_AVE_SPEED = 15  # [km/h]

    # auto pause cutoff [m/s] (in setting.conf)
    AUTOSTOP_CUTOFF = 4.0 * 1000 / 3600

    # GPS speed cutoff (the distance in 1 seconds at 0.36km/h is 10cm)
    GPS_SPEED_CUTOFF = AUTOSTOP_CUTOFF  # m/s

    # GPSd error handling
    GPSD_PARAM_EPX_EPY_CUTOFF = 100.0
    GPSD_PARAM_EPV_CUTOFF = 100.0
    GPSD_PARAM_SP1_EPV_CUTOFF = 100.0
    GPSD_PARAM_SP1_USED_SATS_CUTOFF = 3

    DISPLAY_PARAM_SPI_CLOCK = 2000000

    # default maps
    MAP = "wikimedia"  # settings.conf
    HEATMAP_OVERLAY_MAP = "rwg_heatmap"
    RAIN_OVERLAY_MAP = "rainviewer"
    WIND_OVERLAY_MAP = "openportguide"

    MAP_CONFIG = MAP_CONFIG

    HEATMAP_OVERLAY_MAP_CONFIG = HEATMAP_OVERLAY_MAP_CONFIG
    RAIN_OVERLAY_MAP_CONFIG = RAIN_OVERLAY_MAP_CONFIG
    WIND_OVERLAY_MAP_CONFIG = WIND_OVERLAY_MAP_CONFIG

    # IMU axis conversion
    #  X: to North (up rotation is plus)
    #  Y: to West (up rotation is plus)
    #  Z: to down (default is plus)
    IMU_AXIS_SWAP_XY_STATUS = False  # Y->X, X->Y
    IMU_AXIS_CONVERSION_STATUS = False
    IMU_AXIS_CONVERSION_COEF = np.ones(3)  # X, Y, Z
    # sometimes axes of magnetic sensor are different from acc or gyro
    IMU_MAG_AXIS_SWAP_XY_STATUS = False  # Y->X, X->Y
    IMU_MAG_AXIS_CONVERSION_STATUS = False
    IMU_MAG_AXIS_CONVERSION_COEF = np.ones(3)  # X, Y, Z
    IMU_MAG_DECLINATION = 0

    # LAST FILE GENERATED
    UPLOAD_FILE = ""

    # Ride with GPS
    RWGPS_APIKEY = "pizero_bikercomputer"
    RWGPS_TOKEN = ""
    RWGS_ROUTE_DOWNLOAD_DIR = os.path.join(COURSE_DIR, "ridewithgps")

    @property
    def CURRENT_MAP(self):
        return self.MAP_CONFIG[self.MAP]

    @property
    def WHEEL_CIRCUMFERENCE_M(self):
        return self.WHEEL_CIRCUMFERENCE / 1000

    def __post_init__(self):
        if self.IS_RASPI:
            app_logger.info(f"{model}({unit}), serial:{hex(self.UNIT_ID)}")

        # load extra maps first
        self.read_map_list()

        # read and load local config file, set config_parser with default values too
        self.load_settings_from_file(SETTINGS_FILE)

        # cli
        self.hand_cli_arguments()

    def _set_config_value(
        self,
        config_section,
        key,
        getter=None,
        write_transform=str,
        validator=None,
    ):
        setting_key = (
            key
            if config_section.name == self.config_parser.default_section
            else f"{config_section.name}_{key}"
        )

        try:
            if getter:
                value = getattr(config_section, getter)(key)
            else:
                value = config_section[key]

            if validator and not validator(value):
                raise ValueError

        # key just no present, default to default value from settings
        except KeyError:
            value = getattr(self, setting_key)
        except ValueError:
            app_logger.warning(f"{value} is not a valid value for {key}")
            value = getattr(self, setting_key)

        self.update_setting(setting_key, value)
        config_section[key] = write_transform(value)

    def hand_cli_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--fullscreen", action="store_true", default=False)
        parser.add_argument("-d", "--debug", action="store_true", default=False)
        parser.add_argument("--demo", action="store_true", default=False)
        parser.add_argument("--headless", action="store_true", default=False)
        parser.add_argument("--layout")
        parser.add_argument("--version", action="version", version="%(prog)s 0.1")
        parser.add_argument("--vertical", action="store_true", default=False)

        args = parser.parse_args()

        if args.debug:
            app_logger.setLevel(logging.DEBUG)
        if args.fullscreen:
            self.update_setting("FULLSCREEN", True)
        if args.demo:
            self.update_setting("DUMMY_OUTPUT", True)
        if args.layout and os.path.exists(args.layout):
            self.update_setting("LAYOUT_FILE", args.layout)
        if args.headless:
            self.update_setting("HEADLESS", True)
        if args.vertical:
            self.update_setting("VERTICAL", True)

    def load_settings_from_file(self, filename):
        cf = self.config_parser

        if os.path.exists(filename):
            cf.read(filename)

        if cf.default_section in cf:
            section = cf[cf.default_section]

            self._set_config_value(section, "DISPLAY")

            self._set_config_value(
                section,
                "AUTOSTOP_CUTOFF",
                "getspeed",
                lambda x: str(int(x * 3.6)),
            )

            # make sure GPS_SPEED_CUTOFF is set accordingly
            self.update_setting("GPS_SPEED_CUTOFF", self.AUTOSTOP_CUTOFF)

            self.update_setting("WHEEL_CIRCUMFERENCE", self.WHEEL_CIRCUMFERENCE)

            # GROSS_AVE_SPEED
            self._set_config_value(section, "GROSS_AVE_SPEED", "getint")

            self._set_config_value(section, "AUTO_BACKLIGHT_CUTOFF", "getint")
            self._set_config_value(section, "LANG", "getupper")
            self._set_config_value(section, "FONT_FILE")
            self._set_config_value(
                section,
                "MAP",
                "getlower",
                validator=lambda x: x in list(self.MAP_CONFIG.keys()),
            )

        else:
            cf[cf.default_section] = {
                "DISPLAY": "None",
                "AUTOSTOP_CUTOFF": str(int(self.AUTOSTOP_CUTOFF * 3.6)),
                "WHEEL_CIRCUMFERENCE": str(int(2.105 * 1000)),
                "GROSS_AVE_SPEED": str(self.GROSS_AVE_SPEED),
                "AUTO_BACKLIGHT_CUTOFF": str(self.AUTO_BACKLIGHT_CUTOFF),
                "LANG": self.LANG,
                "FONT_FILE": self.FONT_FILE,
                "MAP": self.MAP,
            }

        if "POWER" in cf:
            section = cf["POWER"]

            self._set_config_value(section, "CP", "getint")
            self._set_config_value(section, "W_PRIME", "getint")
        else:
            cf["POWER"] = {
                "CP": str(self.POWER_CP),
                "W_PRIME": str(self.POWER_W_PRIME),
            }

        if "IMU" in cf:
            section = cf["IMU"]

            self._set_config_value(section, "AXIS_SWAP_XY_STATUS", "getboolean")
            self._set_config_value(section, "AXIS_CONVERSION_STATUS", "getboolean")
            self._set_config_value(
                section,
                "AXIS_CONVERSION_COEF",
                "getnparray",
                lambda x: str(list(x)),
                # validator TODO (np.sum((coef == 1) | (coef == -1)) == n ??)
            )
            self._set_config_value(section, "MAG_AXIS_SWAP_XY_STATUS", "getboolean")
            self._set_config_value(section, "MAG_AXIS_CONVERSION_STATUS", "getboolean")
            self._set_config_value(
                section,
                "MAG_AXIS_CONVERSION_COEF",
                "getnparray",
                lambda x: str(list(x)),
                # validator TODO (np.sum((coef == 1) | (coef == -1)) == n ??)
            )
            self._set_config_value(section, "MAG_DECLINATION", "getint")
        else:
            cf["IMU"] = {
                "AXIS_SWAP_XY_STATUS": str(self.IMU_AXIS_SWAP_XY_STATUS),
                "AXIS_CONVERSION_STATUS": str(self.IMU_AXIS_CONVERSION_STATUS),
                "AXIS_CONVERSION_COEF": str(list(self.IMU_AXIS_CONVERSION_COEF)),
                "MAG_AXIS_SWAP_XY_STATUS": str(self.IMU_MAG_AXIS_SWAP_XY_STATUS),
                "MAG_AXIS_CONVERSION_STATUS": str(self.IMU_MAG_AXIS_CONVERSION_STATUS),
                "MAG_AXIS_CONVERSION_COEF": str(
                    list(self.IMU_MAG_AXIS_CONVERSION_COEF)
                ),
                "MAG_DECLINATION": str(self.IMU_MAG_DECLINATION),
            }

        if "DISPLAY_PARAM" in cf:
            self._set_config_value(cf["DISPLAY_PARAM"], "SPI_CLOCK", "getint")
        else:
            cf["DISPLAY_PARAM"] = {
                "SPI_CLOCK": str(self.DISPLAY_PARAM_SPI_CLOCK),
            }

        if "GPSD_PARAM" in cf:
            section = cf["GPSD_PARAM"]

            self._set_config_value(section, "EPX_EPY_CUTOFF", "getfloat")
            self._set_config_value(section, "EPV_CUTOFF", "getfloat")
            self._set_config_value(section, "SP1_EPV_CUTOFF", "getfloat")
            self._set_config_value(section, "SP1_USED_SATS_CUTOFF", "getint")
        else:
            cf["GPSD_PARAM"] = {
                "EPX_EPY_CUTOFF": str(self.GPSD_PARAM_EPX_EPY_CUTOFF),
                "EPV_CUTOFF": str(self.GPSD_PARAM_EPV_CUTOFF),
                "SP1_EPV_CUTOFF": str(self.GPSD_PARAM_SP1_EPV_CUTOFF),
                "SP1_USED_SATS_CUTOFF": str(self.GPSD_PARAM_SP1_EPV_CUTOFF),
            }

        if "RWGPS" in cf:
            section = cf["RWGPS"]
            self._set_config_value(section, "APIKEY")
            self._set_config_value(section, "TOKEN")
        else:
            cf["RWGPS"] = {
                "APIKEY": str(self.RWGPS_APIKEY),
                "TOKEN": str(self.RWGPS_TOKEN),
            }

    def read_map_list(self):
        try:
            with open(self.MAP_LIST) as file:
                text = file.read()
                map_dict = yaml.safe_load(text)

                if map_dict is None:
                    return

                self.MAP_CONFIG.update({k: MapDict(v) for k, v in map_dict.items()})
        except FileNotFoundError:
            pass

    def save(self):
        with open(SETTINGS_FILE, "w") as file:
            self.config_parser.write(file)

    # should be only called on user action (or on init)
    def update_setting(self, key, value):
        if not hasattr(self, key):
            raise AttributeError(f"Unknown setting: {key}")

        object.__setattr__(self, key, value)


settings = SettingsNamespace()
