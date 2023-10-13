import abc
import asyncio
import re
from datetime import datetime, time, timedelta

import numpy as np
from dateutil import parser, tz
from timezonefinder import TimezoneFinder

from modules.sensor.sensor import Sensor
from modules.utils.cmd import exec_cmd, exec_cmd_return_value
from modules.utils.geo import get_dist_on_earth, get_track_str
from logger import app_logger

USED_SAT_CUTOFF = 3
HDOP_CUTOFF_MODERATE = 10.0
HDOP_CUTOFF_FAIR = 20.0

NMEA_MODE_UNKNOWN = 0
NMEA_MODE_NO_FIX = 1
NMEA_MODE_2D = 2
NMEA_MODE_3D = 3


class AbstractSensorGPS(Sensor, metaclass=abc.ABCMeta):
    elements = [
        "lat",
        "lon",
        "alt",
        "raw_lat",
        "raw_lon",
        "pre_lat",
        "pre_lon",
        "pre_alt",
        "pre_track",
        "speed",
        "track",
        "track_str",
        "used_sats",
        "total_sats",
        "used_sats_str",
        "epx",
        "epy",
        "epv",
        "pdop",
        "hdop",
        "vdop",
        "time",
        "utctime",
        "mode",
    ]
    is_time_modified = False
    is_fixed = False
    is_altitude_modified = False
    course_index_check = []
    azimuth_cutoff = [0, 360]
    time_format = "%Y/%m/%d %H:%M:%S +0000"

    NULL_VALUE = "n/a"

    valid_cutoff_dof = (99.0, 99.0, 99.0)

    # Gadget bridge settings
    gb_timediff_from_utc = timedelta(hours=0)

    @property
    def is_real(self):
        return True  # only dummy is not a real GPS

    def sensor_init(self):
        # TODO, we set a global variable, this should be proscribed !!
        self.config.G_GPS_NULLVALUE = self.NULL_VALUE

        self.reset()
        for element in self.elements:
            self.values[element] = np.nan

        self.azimuth_cutoff = [
            self.config.G_GPS_AZIMUTH_CUTOFF,
            360 - self.config.G_GPS_AZIMUTH_CUTOFF,
        ]

    def reset(self):
        self.values["distance"] = 0

    async def quit(self):
        await self.sleep()

    def start_coroutine(self):
        asyncio.create_task(self.start())

    async def start(self):
        await self.update()

    @abc.abstractmethod
    async def update(self):
        pass

    def is_null_value(self, value):
        return value == self.NULL_VALUE

    def init_values(self):
        # backup values
        if not np.isnan(self.values["lat"]) and not np.isnan(self.values["lon"]):
            self.values["pre_lat"] = self.values["lat"]
            self.values["pre_lon"] = self.values["lon"]
            self.values["pre_alt"] = self.values["alt"]
            self.values["pre_track"] = self.values["track"]
        # initialize
        for element in self.elements:
            if element in ["pre_lat", "pre_lon", "pre_alt", "pre_track"]:
                continue
            self.values[element] = np.nan

    def is_position_valid(self, lat, lon, mode, dop, satellites, error=None):
        valid = True
        if (
            lat is None
            or lon is None
            or abs(lat) > 90
            or abs(lon) > 180
            or mode is None
            or mode < NMEA_MODE_3D
            or None in dop
            or any([x >= self.valid_cutoff_dof[i] for i, x in enumerate(dop)])
            or satellites[0] <= USED_SAT_CUTOFF
        ):
            valid = False

        return valid

    async def get_basic_values(
        self, lat, lon, alt, speed, track, mode, error, dop, satellites
    ):
        # TODO, this probably has to go in the long term
        self.init_values()

        # our first task is to align the format for each null value, we do it only for GPS
        # that do not use None as NULL_VALUE already, else the values are already correct.
        # (Maybe it could be done on the sensor implementation itself)
        if self.NULL_VALUE is not None:

            def id_or_none(value):
                if isinstance(value, list):
                    return [id_or_none(x) for x in value]
                else:
                    return value if not self.is_null_value(value) else None

            lat = id_or_none(lat)
            lon = id_or_none(lon)
            alt = id_or_none(alt)
            speed = id_or_none(speed)
            track = id_or_none(track)
            mode = id_or_none(mode)
            error = id_or_none(error)
            dop = id_or_none(dop)
            # no need to check for satellites, manually computed

        # coordinate
        valid_pos = self.is_position_valid(lat, lon, mode, dop, satellites, error)

        # special condition #2
        # if not valid_pos and self.values['mode'] == 3 and self.values['used_sats'] >= 10 \
        #  and np.all(np.array([self.values['pdop'], self.values['hdop'], self.values['vdop']]) < np.array([3.0, 3.0, 3.0])) \
        #  :
        #  valid_pos = True

        if valid_pos:
            self.values["lat"] = lat
            self.values["lon"] = lon
        else:  # copy from pre value
            self.values["lat"] = self.values["pre_lat"]
            self.values["lon"] = self.values["pre_lon"]

        # altitude
        if valid_pos and alt is not None:
            # floor
            if alt < -500:
                self.values["alt"] = -500
            else:
                self.values["alt"] = alt
        else:  # copy from pre value
            self.values["alt"] = self.values["pre_alt"]

        # GPS distance
        if self.config.G_STOPWATCH_STATUS == "START" and not np.any(
            np.isnan(
                [
                    self.values["pre_lon"],
                    self.values["pre_lat"],
                    self.values["lon"],
                    self.values["lat"],
                ]
            )
        ):
            # 2D distance : (x1, y1), (x2, y2)
            dist = get_dist_on_earth(
                self.values["pre_lon"],
                self.values["pre_lat"],
                self.values["lon"],
                self.values["lat"],
            )
            # need 3D distance? : (x1, y1, z1), (x2, y2, z2)

            # unit: m
            self.values["distance"] += dist

        # speed
        if valid_pos and speed is not None:
            # unit m/s
            if speed <= self.config.G_GPS_SPEED_CUTOFF:
                self.values["speed"] = 0.0
            else:
                self.values["speed"] = speed

        # track
        if (
            track is not None
            and speed is not None
            and speed > self.config.G_GPS_SPEED_CUTOFF
        ):
            self.values["track"] = int(track)
            self.values["track_str"] = get_track_str(self.values["track"])
        else:
            self.values["track"] = self.values["pre_track"]

        self.course.get_index(
            self.values["lat"],
            self.values["lon"],
            self.values["track"],
            self.config.G_GPS_SEARCH_RANGE,
            self.config.G_GPS_ON_ROUTE_CUTOFF,
            self.azimuth_cutoff,
        )

        # timezone
        if not self.is_fixed and valid_pos and mode == NMEA_MODE_3D:
            self.is_fixed = self.set_timezone(lat, lon)

        # modify altitude with course
        if (
            not self.is_altitude_modified
            and self.course.index.on_course_status
            and len(self.course.altitude)
        ):
            await self.config.logger.sensor.sensor_i2c.update_sealevel_pa(
                self.config.logger.course.altitude[self.course.index.value]
            )
            self.is_altitude_modified = True

        # finally set the values object

        # timestamp
        self.values["timestamp"] = datetime.now()
        # raw coordinates
        self.values["raw_lat"] = lat
        self.values["raw_lon"] = lon

        self.values["mode"] = mode

        # DOP
        for i, key in enumerate(["pdop", "hdop", "vdop"]):
            self.values[key] = dop[i]

        self.values["used_sats"] = satellites[0]
        self.values["total_sats"] = satellites[1]

        # TODO, save error for gpsd, could be improved, not very resilient
        if error:
            for i, key in enumerate(["epx", "epy", "epv"]):
                self.values[key] = error[i]

        if satellites[1] is not None:
            self.values["used_sats_str"] = f"{satellites[0]} / {satellites[1]}"
        else:
            self.values["used_sats_str"] = f"{satellites[0]}"

    def get_utc_time(self, gps_time):
        if isinstance(gps_time, (datetime, time)):
            gps_time = gps_time.strftime(self.time_format)

        # UTC time
        if self.is_null_value(gps_time):
            return

        self.values["time"] = gps_time
        self.values["utctime"] = self.values["time"][11:16]  # [11:19] for HH:MM:SS

        # for ublox error
        # ValueError: ('Unknown string format:', '1970-01-01T00:00:00(null')
        # if self.values['time'].find('1970-01-01') >= 0:
        if (
            self.values["time"][0:4].isdecimal()
            and int(self.values["time"][0:4]) < 2000
        ):
            return

        if not self.is_time_modified:
            self.is_time_modified = self.set_time()

    def set_time(self):
        app_logger.info("try to modify time by gps...")
        l_time = parser.parse(self.values["time"])
        # kernel version date
        kernel_date = datetime(2019, 1, 1, 0, 0, 0, 0, tz.tzutc())
        kernel_date_str = exec_cmd_return_value(["uname", "-v"], cmd_print=False)
        # "#1253 Thu Aug 15 11:37:30 BST 2019"
        if len(kernel_date_str) >= 34:
            m = re.search(r"^.+(\w{3}) (\d+).+(\d{4})$", kernel_date_str)
            if m:
                time_str = f"{m.group(3)} {m.group(1)} {m.group(2)} 00:00:00 UTC"
                kernel_date = parser.parse(time_str)
        if l_time < kernel_date:
            return False
        exec_cmd(
            ["sudo", "date", "-u", "--set", l_time.strftime("%Y/%m/%d %H:%M:%S")],
            cmd_print=False,
        )
        return True

    def set_timezone(self, lat, lon):
        app_logger.info("try to modify timezone by gps...")

        tz_finder = TimezoneFinder()

        try:
            tz_str = tz_finder.timezone_at(lng=lon, lat=lat)

            if tz_str is None:
                # certain_timezone_at is deprecated since timezonefinder 6.2.0
                tz_str = tz_finder.certain_timezone_at(lng=lon, lat=lat)

            if tz_str is not None:
                ret_code = exec_cmd(
                    ["sudo", "timedatectl", "set-timezone", tz_str], cmd_print=False
                )
                if not ret_code:  # 0 = success
                    self.config.G_TIMEZONE = tz_str
            return True
        except TypeError as e:
            app_logger.exception(f"Incorrect lat, lon passed: {e}")
            return False
        except Exception as e:
            app_logger.warning(f"Could not set timezone: {e}")
            return False

    # manual update/GB
    async def update_manual(self, message):
        lat = lon = alt = speed = track = hdop = mode = timestamp = self.NULL_VALUE
        if "lat" in message and "lon" in message:
            lat = float(message["lat"])
            lon = float(message["lon"])
        if "alt" in message:
            alt = float(message["alt"])
        if "speed" in message:
            speed = float(message["speed"])  # m/s
        if "course" in message:
            track = int(message["course"])
        if "time" in message:
            timestamp = (
                datetime.fromtimestamp(message["time"] // 1000)
                - self.gb_timediff_from_utc
            )
        if "hdop" in message:
            hdop = float(message["hdop"])
            if hdop < HDOP_CUTOFF_MODERATE:
                mode = NMEA_MODE_3D
            elif hdop < HDOP_CUTOFF_FAIR:
                mode = NMEA_MODE_2D
            else:
                mode = NMEA_MODE_NO_FIX

        await self.get_basic_values(
            lat,
            lon,
            alt,
            speed,
            track,
            mode,
            None,
            [hdop, hdop, hdop],
            (int(message.get("satellites", 0)), None),
        )
        self.get_utc_time(timestamp)

    def set_gb_timediff_from_utc(self, timediff):
        self.gb_timediff_from_utc = timediff
