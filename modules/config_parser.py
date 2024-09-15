import configparser
import json
import os
import struct

import numpy as np


class ConfParser:
    config = None
    config_parser = None

    # config file (store user specified values. readable and editable.)
    config_file = "setting.conf"

    def __init__(self, config):
        self.config = config
        self.config_parser = configparser.ConfigParser()

        if os.path.exists(self.config_file):
            self.read()

    def read(self):
        self.config_parser.read(self.config_file)

        if "ANT" in self.config_parser:
            for key in self.config_parser["ANT"]:
                if key.upper() == "STATUS":
                    self.config.G_ANT["STATUS"] = self.config_parser["ANT"].getboolean(
                        key
                    )
                    continue

                i = key.rfind("_")

                if i < 0:
                    continue

                key1 = key[0:i]
                key2 = key[i + 1 :]
                try:
                    k1 = key1.upper()
                    k2 = key2.upper()
                except:
                    continue
                if (
                    k1 == "USE" and k2 in self.config.G_ANT["ID"].keys()
                ):  # ['HR','SPD','CDC','PWR']:
                    try:
                        self.config.G_ANT[k1][k2] = self.config_parser[
                            "ANT"
                        ].getboolean(key)
                    except:
                        pass
                elif (
                    k1 in ["ID", "TYPE"] and k2 in self.config.G_ANT["ID"].keys()
                ):  # ['HR','SPD','CDC','PWR']:
                    try:
                        self.config.G_ANT[k1][k2] = self.config_parser["ANT"].getint(
                            key
                        )
                    except:
                        pass
            for key in self.config.G_ANT["ID"].keys():  # ['HR','SPD','CDC','PWR']:
                if (
                    not (0 <= self.config.G_ANT["ID"][key] <= 0xFFFF)
                    or not self.config.G_ANT["TYPE"][key]
                    in self.config.G_ANT["TYPES"][key]
                ):
                    self.config.G_ANT["USE"][key] = False
                    self.config.G_ANT["ID"][key] = 0
                    self.config.G_ANT["TYPE"][key] = 0
                if (
                    self.config.G_ANT["ID"][key] != 0
                    and self.config.G_ANT["TYPE"][key] != 0
                ):
                    self.config.G_ANT["ID_TYPE"][key] = struct.pack(
                        "<HB",
                        self.config.G_ANT["ID"][key],
                        self.config.G_ANT["TYPE"][key],
                    )

        if "STRAVA_API" in self.config_parser:
            for k in self.config.G_STRAVA_API.keys():
                if k in self.config_parser["STRAVA_API"]:
                    self.config.G_STRAVA_API[k] = self.config_parser["STRAVA_API"][k]

        if "STRAVA_COOKIE" in self.config_parser:
            for k in self.config.G_STRAVA_COOKIE.keys():
                if k in self.config_parser["STRAVA_COOKIE"]:
                    self.config.G_STRAVA_COOKIE[k] = self.config_parser[
                        "STRAVA_COOKIE"
                    ][k]

    def write_config(self):
        self.config_parser["GENERAL"] = {}
        self.config_parser["GENERAL"]["DISPLAY"] = self.config.G_DISPLAY
        self.config_parser["GENERAL"]["AUTOSTOP_CUTOFF"] = "UNKNOWN: TO BE FIXED"
        self.config_parser["GENERAL"]["WHEEL_CIRCUMFERENCE"] = str(
            int(self.config.G_WHEEL_CIRCUMFERENCE * 1000)
        )
        self.config_parser["GENERAL"]["GROSS_AVE_SPEED"] = "UNKNOWN: TO BE FIXED"
        self.config_parser["GENERAL"]["AUTO_BACKLIGHT_CUTOFF"] = "UNKNOWN: TO BE FIXED"
        self.config_parser["GENERAL"]["LANG"] = "UNKNOWN: TO BE FIXED"
        self.config_parser["GENERAL"]["FONT_FILE"] = "UNKNOWN: TO BE FIXED"
        self.config_parser["GENERAL"]["MAP"] = "UNKNOWN: TO BE FIXED"

        self.config_parser["POWER"] = {}
        self.config_parser["POWER"]["CP"] = str(int(self.config.G_POWER_CP))
        self.config_parser["POWER"]["W_PRIME"] = str(int(self.config.G_POWER_W_PRIME))

        if not self.config.G_DUMMY_OUTPUT:
            self.config_parser["ANT"] = {}
            self.config_parser["ANT"]["STATUS"] = str(self.config.G_ANT["STATUS"])
            for key1 in ["USE", "ID", "TYPE"]:
                for key2 in self.config.G_ANT[key1]:
                    if (
                        key2 in self.config.G_ANT["ID"].keys()
                    ):  # ['HR','SPD','CDC','PWR']:
                        self.config_parser["ANT"][key1 + "_" + key2] = str(
                            self.config.G_ANT[key1][key2]
                        )

        self.config_parser["SENSOR_IMU"] = {}
        self.config_parser["SENSOR_IMU"]["AXIS_SWAP_XY_STATUS"] = str(
            self.config.G_IMU_AXIS_SWAP_XY["STATUS"]
        )
        self.config_parser["SENSOR_IMU"]["AXIS_CONVERSION_STATUS"] = str(
            self.config.G_IMU_AXIS_CONVERSION["STATUS"]
        )
        self.config_parser["SENSOR_IMU"]["AXIS_CONVERSION_COEF"] = str(
            self.config.G_IMU_AXIS_CONVERSION["COEF"].tolist()
        )
        self.config_parser["SENSOR_IMU"]["MAG_AXIS_SWAP_XY_STATUS"] = str(
            self.config.G_IMU_MAG_AXIS_SWAP_XY["STATUS"]
        )
        self.config_parser["SENSOR_IMU"]["MAG_AXIS_CONVERSION_STATUS"] = str(
            self.config.G_IMU_MAG_AXIS_CONVERSION["STATUS"]
        )
        self.config_parser["SENSOR_IMU"]["MAG_AXIS_CONVERSION_COEF"] = str(
            self.config.G_IMU_MAG_AXIS_CONVERSION["COEF"].tolist()
        )
        self.config_parser["SENSOR_IMU"]["MAG_DECLINATION"] = str(
            int(self.config.G_IMU_MAG_DECLINATION)
        )

        self.config_parser["DISPLAY_PARAM"] = {}
        self.config_parser["DISPLAY_PARAM"]["SPI_CLOCK"] = str(
            int(self.config.G_DISPLAY_PARAM["SPI_CLOCK"])
        )

        self.config_parser["GPSD_PARAM"] = {}
        self.config_parser["GPSD_PARAM"]["EPX_EPY_CUTOFF"] = str(
            self.config.G_GPSD_PARAM["EPX_EPY_CUTOFF"]
        )
        self.config_parser["GPSD_PARAM"]["EPV_CUTOFF"] = str(
            self.config.G_GPSD_PARAM["EPV_CUTOFF"]
        )
        self.config_parser["GPSD_PARAM"]["SP1_EPV_CUTOFF"] = str(
            self.config.G_GPSD_PARAM["SP1_EPV_CUTOFF"]
        )
        self.config_parser["GPSD_PARAM"]["SP1_USED_SATS_CUTOFF"] = str(
            self.config.G_GPSD_PARAM["SP1_USED_SATS_CUTOFF"]
        )

        self.config_parser["STRAVA_API"] = {}
        for k in self.config.G_STRAVA_API.keys():
            self.config_parser["STRAVA_API"][k] = self.config.G_STRAVA_API[k]

        self.config_parser["STRAVA_COOKIE"] = {}
        for k in self.config.G_STRAVA_COOKIE.keys():
            self.config_parser["STRAVA_COOKIE"][k] = self.config.G_STRAVA_COOKIE[k]

        with open(self.config_file, "w") as file:
            self.config_parser.write(file)
