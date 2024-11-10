import asyncio
import math
from datetime import datetime

import numpy as np

_IMPORT_PSUTIL = False
try:
    import psutil

    _IMPORT_PSUTIL = True
except ImportError:
    pass

from logger import app_logger

app_logger.info("detected sensor modules:")

from modules.constants import ANTDevice
from modules.items.general import (
    HeartRateItemConfig,
    PowerItemConfig,
    WBalNormItemConfig,
)
from modules.items.gps import GPS_AltitudeItemConfig
from modules.items.i2c import I2C_AltitudeItemConfig
from modules.settings import settings
from modules.utils.timer import Timer, log_timers
from .sensor.ant.ant_code import AntDeviceType
from .sensor.gps import SensorGPS
from .sensor.sensor_ant import SensorANT
from .sensor.sensor_gpio import SensorGPIO
from .sensor.sensor_i2c import SensorI2C


class SensorCore:
    config = None
    sensor_gps = None
    sensor_ant = None
    sensor_i2c = None
    sensor_gpio = None
    integrated_value_keys = [
        "heart_rate",
        "speed",
        "cadence",
        "power",
        "distance",
        "accumulated_power",
        "w_prime_balance",
        "w_prime_balance_normalized",
        "w_prime_power_sum",
        "w_prime_power_count",
        "w_prime_t",
        "w_prime_sum",
        "grade",
        "grade_spd",
        "glide_ratio",
        "temperature",
        "cpu_percent",
        "send_time",
    ]
    average_secs = [3, 30, 60]
    average_values = {"heart_rate": {}, "power": {}}
    process = None
    # valid period of sensor [sec]
    time_threshold = {
        ANTDevice.HEART_RATE: 15,
        ANTDevice.SPEED: 5,
        ANTDevice.CADENCE: 3,
        ANTDevice.POWER: 3,
        ANTDevice.TEMPERATURE: 45,
    }
    grade_range = 9
    grade_window_size = 5
    brakelight_spd = []
    brakelight_spd_range = 4
    brakelight_spd_cutoff = 4  # 4*3.6 = 14.4 [km/h]
    diff_keys = [
        "alt_diff",
        "dst_diff",
        "alt_diff_spd",
        "dst_diff_spd",
    ]
    lp = 4

    def __init__(self, config):
        self.config = config
        self.values = {"GPS": {}, "ANT+": {}, "I2C": {}, "integrated": {}}

        # reset
        for key in self.integrated_value_keys:
            self.values["integrated"][key] = np.nan
        self.reset_internal()

        for d in self.diff_keys:
            self.values["integrated"][d] = np.full(self.grade_range, np.nan)
        self.brakelight_spd = [0] * self.brakelight_spd_range
        self.values["integrated"]["CPU_MEM"] = ""

        for s in self.average_secs:
            for v in self.average_values:
                self.average_values[v][s] = []
                self.values["integrated"][f"ave_{v}_{s}s"] = np.nan
        if _IMPORT_PSUTIL:
            self.process = psutil.Process()

        if SensorGPS:
            self.sensor_gps = SensorGPS(config, self.values["GPS"])

        timers = [
            Timer(auto_start=False, text="ANT+ : {0:.3f} sec"),
            Timer(auto_start=False, text="I2C  : {0:.3f} sec"),
        ]

        with timers[0]:
            self.sensor_ant = SensorANT(config, self.values["ANT+"])

        with timers[1]:
            self.sensor_i2c = SensorI2C(config, self.values["I2C"])

        self.sensor_gpio = SensorGPIO(config, None)
        self.sensor_gpio.update()

        app_logger.info("[sensor] Initialize:")
        log_timers(timers)

    def start_coroutine(self):
        asyncio.create_task(self.integrate())
        self.sensor_ant.start_coroutine()
        self.sensor_gps.start_coroutine()
        self.sensor_i2c.start_coroutine()

    async def quit(self):
        self.sensor_ant.quit()
        await self.sensor_gps.quit()
        self.sensor_gpio.quit()

    # reset accumulated values
    def reset(self):
        self.sensor_gps.reset()
        self.sensor_ant.reset()
        self.sensor_i2c.reset()
        self.reset_internal()

    def reset_internal(self):
        self.values["integrated"]["distance"] = 0
        self.values["integrated"]["accumulated_power"] = 0
        self.values["integrated"]["w_prime_balance"] = settings.POWER_W_PRIME
        self.values["integrated"]["w_prime_power_sum"] = 0
        self.values["integrated"]["w_prime_power_count"] = 0
        self.values["integrated"]["w_prime_t"] = 0
        self.values["integrated"]["w_prime_sum"] = 0
        self.values["integrated"]["pwr_mean_under_cp"] = 0
        self.values["integrated"]["tau"] = (
            546 * np.exp(-0.01 * (settings.POWER_CP - 0)) + 316
        )

    async def integrate(self):
        pre_dst = {"ANT+": 0, "GPS": 0}
        pre_ttlwork = {"ANT+": 0}
        pre_alt = {"ANT+": np.nan, "GPS": np.nan}
        pre_alt_spd = {"ANT+": np.nan}
        pre_grade = pre_grade_spd = pre_glide = settings.ANT_NULLVALUE
        diff_sum = {"alt_diff": 0, "dst_diff": 0, "alt_diff_spd": 0, "dst_diff_spd": 0}

        # alias for self.values
        v = {"GPS": self.values["GPS"], "I2C": self.values["I2C"]}
        # loop control
        self.wait_time = settings.SENSOR_INTERVAL
        self.actual_loop_interval = settings.SENSOR_INTERVAL

        try:
            while True:
                await asyncio.sleep(self.wait_time)
                start_time = datetime.now()
                time_profile = [
                    start_time,
                ]

                hr = spd = cdc = pwr = temperature = settings.ANT_NULLVALUE
                grade = grade_spd = glide = settings.ANT_NULLVALUE
                ttlwork_diff = 0
                dst_diff = {"ANT+": 0, "GPS": 0, "USE": 0}
                alt_diff = {"ANT+": 0, "GPS": 0, "USE": 0}
                dst_diff_spd = {"ANT+": 0}
                alt_diff_spd = {"ANT+": 0}
                grade_use = {"ANT+": False, "GPS": False}
                time_profile.append(datetime.now())
                # self.sensor_i2c.update()
                # self.sensor_gps.update()
                self.sensor_ant.update()  # for dummy

                now_time = datetime.now()
                time_profile.append(now_time)

                delta = {
                    ANTDevice.POWER: {
                        0x10: float("inf"),
                        0x11: float("inf"),
                        0x12: float("inf"),
                    },
                    ANTDevice.HEART_RATE: float("inf"),
                    ANTDevice.SPEED: float("inf"),
                    ANTDevice.CADENCE: float("inf"),
                    ANTDevice.TEMPERATURE: float("inf"),
                }

                # need for ANT+ ID update
                for key in [
                    ANTDevice.HEART_RATE,
                    ANTDevice.SPEED,
                    ANTDevice.CADENCE,
                    ANTDevice.POWER,
                    ANTDevice.TEMPERATURE,
                ]:
                    if settings.is_ant_device_enabled(key):
                        device = settings.get_ant_device(key)

                        if device in self.values["ANT+"]:
                            v[key] = self.values["ANT+"][device]

                # make intervals from timestamp
                for key in [
                    ANTDevice.HEART_RATE,
                    ANTDevice.SPEED,
                    ANTDevice.CADENCE,
                    ANTDevice.TEMPERATURE,
                ]:
                    if not settings.is_ant_device_enabled(key):
                        continue

                    _, device_type = settings.get_ant_device(key)

                    if "timestamp" in v[key]:
                        delta[key] = (now_time - v[key]["timestamp"]).total_seconds()

                    # override:
                    # cadence from power
                    if device_type == AntDeviceType.POWER and key == ANTDevice.CADENCE:
                        for page in [0x12, 0x10]:
                            if not "timestamp" in v[key][page]:
                                continue

                            delta[key] = (
                                now_time - v[key][page]["timestamp"]
                            ).total_seconds()
                            break

                    # speed from power
                    elif device_type == AntDeviceType.POWER and key == ANTDevice.SPEED:
                        if not "timestamp" in v[key][0x11]:
                            continue

                        delta[key] = (
                            now_time - v[key][0x11]["timestamp"]
                        ).total_seconds()

                # timestamp(power)
                if settings.is_ant_device_enabled(ANTDevice.POWER):
                    for page in [0x12, 0x11, 0x10]:
                        if not "timestamp" in v[ANTDevice.POWER][page]:
                            continue
                        delta[ANTDevice.POWER][page] = (
                            now_time - v[ANTDevice.POWER][page]["timestamp"]
                        ).total_seconds()
                if "timestamp" in v["GPS"]:
                    delta["GPS"] = (now_time - v["GPS"]["timestamp"]).total_seconds()

                # HeartRate : ANT+
                if settings.is_ant_device_enabled(ANTDevice.HEART_RATE):
                    if (
                        delta[ANTDevice.HEART_RATE]
                        < self.time_threshold[ANTDevice.HEART_RATE]
                    ):
                        hr = v[ANTDevice.HEART_RATE]["heart_rate"]

                # Cadence : ANT+
                if settings.is_ant_device_enabled(ANTDevice.CADENCE):
                    cdc = 0

                    _, device_type = settings.get_ant_device(ANTDevice.CADENCE)

                    # get from cadence or speed&cadence sensor
                    if device_type in [
                        AntDeviceType.SPEED_AND_CADENCE,
                        AntDeviceType.CADENCE,
                    ]:
                        if (
                            delta[ANTDevice.CADENCE]
                            < self.time_threshold[ANTDevice.CADENCE]
                        ):
                            cdc = v[ANTDevice.CADENCE]["cadence"]

                    # get from powermeter
                    elif device_type == ANTDevice.POWER:
                        for page in [0x12, 0x10]:
                            if not "timestamp" in v[ANTDevice.CADENCE][page]:
                                continue
                            if (
                                delta[ANTDevice.CADENCE]
                                < self.time_threshold[ANTDevice.CADENCE]
                            ):
                                cdc = v[ANTDevice.CADENCE][page]["cadence"]
                                break

                # Power : ANT+(assumed crank type > wheel type)
                if settings.is_ant_device_enabled(ANTDevice.POWER):
                    pwr = 0
                    # page18 > 17 > 16, 16simple is not used
                    for page in [0x12, 0x11, 0x10]:
                        if (
                            delta[ANTDevice.POWER][page]
                            < self.time_threshold[ANTDevice.POWER]
                        ):
                            pwr = v[ANTDevice.POWER][page]["power"]
                            break

                # Speed : ANT+(SPD&CDC, (PWR)) > GPS
                if settings.is_ant_device_enabled(ANTDevice.SPEED):
                    spd = 0

                    _, device_type = settings.get_ant_device(ANTDevice.SPEED)
                    if device_type in [
                        AntDeviceType.SPEED_AND_CADENCE,
                        AntDeviceType.SPEED,
                    ]:
                        if (
                            delta[ANTDevice.SPEED]
                            < self.time_threshold[ANTDevice.SPEED]
                        ):
                            spd = v[ANTDevice.SPEED]["speed"]
                    elif device_type == AntDeviceType.POWER:
                        if (
                            delta[ANTDevice.SPEED]
                            < self.time_threshold[ANTDevice.SPEED]
                        ):
                            spd = v[ANTDevice.SPEED][0x11]["speed"]
                    # complement from GPS speed when I2C acc sensor is available (using moving status)
                    if (
                        delta[ANTDevice.SPEED] > self.time_threshold[ANTDevice.SPEED]
                        and spd == 0
                        and v["I2C"]["m_stat"] == 1
                        and v["GPS"]["speed"] > 0
                    ):
                        spd = v["GPS"]["speed"]
                        # print("speed from GPS: delta {}s, {:.1f}km/h".format(delta['SPD'], v['GPS']['speed']*3.6))
                elif "timestamp" in v["GPS"]:
                    spd = 0
                    if (
                        not np.isnan(v["GPS"]["speed"])
                        and delta["GPS"] < self.time_threshold[ANTDevice.SPEED]
                    ):
                        spd = v["GPS"]["speed"]

                # Distance: ANT+(SPD, (PWR)) > GPS
                if settings.is_ant_device_enabled(ANTDevice.SPEED):
                    # normal speed meter
                    _, device_type = settings.get_ant_device(ANTDevice.SPEED)
                    if device_type in [
                        AntDeviceType.SPEED_AND_CADENCE,
                        AntDeviceType.SPEED,
                    ]:
                        if pre_dst["ANT+"] < v[ANTDevice.SPEED]["distance"]:
                            dst_diff["ANT+"] = (
                                v[ANTDevice.SPEED]["distance"] - pre_dst["ANT+"]
                            )
                        pre_dst["ANT+"] = v[ANTDevice.SPEED]["distance"]
                    elif device_type == AntDeviceType.POWER:
                        if pre_dst["ANT+"] < v[ANTDevice.SPEED][0x11]["distance"]:
                            dst_diff["ANT+"] = (
                                v[ANTDevice.SPEED][0x11]["distance"] - pre_dst["ANT+"]
                            )
                        pre_dst["ANT+"] = v[ANTDevice.SPEED][0x11]["distance"]
                    dst_diff["USE"] = dst_diff["ANT+"]
                    grade_use["ANT+"] = True

                if "timestamp" in v["GPS"]:
                    if pre_dst["GPS"] < v["GPS"]["distance"]:
                        dst_diff["GPS"] = v["GPS"]["distance"] - pre_dst["GPS"]
                    pre_dst["GPS"] = v["GPS"]["distance"]

                    if (
                        not settings.is_ant_device_enabled(ANTDevice.SPEED)
                        and dst_diff["GPS"] > 0
                    ):
                        dst_diff["USE"] = dst_diff["GPS"]
                        grade_use["GPS"] = True

                    # ANT+ sensor is not connected from the beginning of the ride
                    elif settings.is_ant_device_enabled(ANTDevice.SPEED):
                        if (
                            delta[ANTDevice.SPEED] == np.inf
                            and dst_diff["ANT+"] == 0
                            and dst_diff["GPS"] > 0
                        ):
                            dst_diff["USE"] = dst_diff["GPS"]
                            grade_use["ANT+"] = False
                            grade_use["GPS"] = True

                # Total Power: ANT+
                if settings.is_ant_device_enabled(ANTDevice.POWER):
                    # both type are not exist in same ID(0x12:crank, 0x11:wheel)
                    # if 0x12 or 0x11 exists, never take 0x10
                    for page in [0x12, 0x11, 0x10]:
                        if "timestamp" in v[ANTDevice.POWER][page]:
                            if (
                                pre_ttlwork["ANT+"]
                                < v[ANTDevice.POWER][page]["accumulated_power"]
                            ):
                                ttlwork_diff = (
                                    v[ANTDevice.POWER][page]["accumulated_power"]
                                    - pre_ttlwork["ANT+"]
                                )
                            pre_ttlwork["ANT+"] = v[ANTDevice.POWER][page][
                                "accumulated_power"
                            ]
                            # never take other powermeter
                            break

                # Temperature : ANT+
                if settings.is_ant_device_enabled(ANTDevice.TEMPERATURE):
                    if (
                        delta[ANTDevice.TEMPERATURE]
                        < self.time_threshold[ANTDevice.TEMPERATURE]
                    ):
                        temperature = v[ANTDevice.TEMPERATURE]["temperature"]
                elif not np.isnan(v["I2C"]["temperature"]):
                    temperature = v["I2C"]["temperature"]

                # altitude
                if not np.isnan(v["I2C"]["pre_altitude"]):
                    alt = v["I2C"]["altitude"]
                    # for grade (distance base)
                    for key in ["ANT+", "GPS"]:
                        if dst_diff[key] > 0:
                            alt_diff[key] = alt - pre_alt[key]
                        pre_alt[key] = alt
                    if settings.is_ant_device_enabled(ANTDevice.SPEED):
                        alt_diff["USE"] = alt_diff["ANT+"]
                    elif (
                        not settings.is_ant_device_enabled(ANTDevice.SPEED)
                        and dst_diff["GPS"] > 0
                    ):
                        alt_diff["USE"] = alt_diff["GPS"]
                    # for grade (speed base)
                    if settings.is_ant_device_enabled(ANTDevice.SPEED):
                        if dst_diff["ANT+"] > 0:
                            alt_diff_spd["ANT+"] = alt - pre_alt_spd["ANT+"]
                        pre_alt_spd["ANT+"] = alt

                # grade (distance base)
                if dst_diff["USE"] > 0:
                    for key in ["alt_diff", "dst_diff"]:
                        self.values["integrated"][key][0:-1] = self.values[
                            "integrated"
                        ][key][1:]
                        self.values["integrated"][key][-1] = eval(key + "['USE']")
                        # diff_sum[key] = np.mean(self.values['integrated'][key][-self.grade_window_size:])
                        diff_sum[key] = np.nansum(
                            self.values["integrated"][key][-self.grade_window_size :]
                        )
                    # set grade
                    gl = settings.ANT_NULLVALUE
                    gr = settings.ANT_NULLVALUE
                    x = settings.ANT_NULLVALUE
                    y = diff_sum["alt_diff"]
                    if grade_use["ANT+"]:
                        x = math.sqrt(
                            abs(diff_sum["dst_diff"] ** 2 - diff_sum["alt_diff"] ** 2)
                        )
                    elif grade_use["GPS"]:
                        x = diff_sum["dst_diff"]
                    if x > 0:
                        # gr = int(round(100 * y / x))
                        gr = self.conv_grade(100 * y / x)
                    if y != 0.0:
                        gl = int(round(-1 * x / y))
                    grade = pre_grade = gr
                    glide = pre_glide = gl
                # for sometimes ANT+ distance is 0 although status is running
                elif dst_diff["USE"] == 0 and self.config.G_STOPWATCH_STATUS == "START":
                    grade = pre_grade
                    glide = pre_glide

                # grade (speed base)
                if settings.is_ant_device_enabled(ANTDevice.SPEED):
                    dst_diff_spd["ANT+"] = spd * self.actual_loop_interval
                    for key in ["alt_diff_spd", "dst_diff_spd"]:
                        self.values["integrated"][key][0:-1] = self.values[
                            "integrated"
                        ][key][1:]
                        self.values["integrated"][key][-1] = eval(key + "['ANT+']")
                        diff_sum[key] = np.mean(
                            self.values["integrated"][key][-self.grade_window_size :]
                        )
                        # diff_sum[key] = np.nansum(self.values['integrated'][key][-self.grade_window_size:])
                    # set grade
                    x = diff_sum["dst_diff_spd"] ** 2 - diff_sum["alt_diff_spd"] ** 2
                    y = diff_sum["alt_diff_spd"]
                    gr = settings.ANT_NULLVALUE
                    if x > 0:
                        x = math.sqrt(x)
                        gr = self.conv_grade(100 * y / x)
                    grade_spd = pre_grade_spd = gr
                # for sometimes speed sensor value is missing in running
                elif (
                    dst_diff_spd["ANT+"] == 0
                    and self.config.G_STOPWATCH_STATUS == "START"
                ):
                    grade_spd = pre_grade_spd

                self.values["integrated"]["heart_rate"] = hr
                self.values["integrated"]["speed"] = spd
                self.values["integrated"]["cadence"] = cdc
                self.values["integrated"]["power"] = pwr
                self.values["integrated"]["distance"] += dst_diff["USE"]
                self.values["integrated"]["accumulated_power"] += ttlwork_diff
                self.values["integrated"]["grade"] = grade
                self.values["integrated"]["grade_spd"] = grade_spd
                self.values["integrated"]["glide_ratio"] = glide
                self.values["integrated"]["temperature"] = temperature

                if settings.is_ant_device_enabled(ANTDevice.POWER):
                    self.calc_w_prime_balance(pwr)

                # update performance graph if initialized
                if performance_graph_widget := self.config.gui.performance_graph_widget:
                    performance_graph_widget.update_value(PowerItemConfig.name, pwr)
                    performance_graph_widget.update_value(HeartRateItemConfig.name, hr)
                    performance_graph_widget.update_value(
                        WBalNormItemConfig.name,
                        self.values["integrated"]["w_prime_balance_normalized"],
                    )

                # update altitude graph if initialized
                if altitude_graph_widget := self.config.gui.altitude_graph_widget:
                    altitude_graph_widget.update_value(
                        I2C_AltitudeItemConfig.name, v["I2C"]["altitude"]
                    )
                    altitude_graph_widget.update_value(
                        GPS_AltitudeItemConfig.name, v["GPS"]["alt"]
                    )

                # average power, heart_rate
                if settings.is_ant_device_enabled(ANTDevice.POWER) and not np.isnan(
                    pwr
                ):
                    self.get_ave_values("power", pwr)
                if settings.is_ant_device_enabled(
                    ANTDevice.HEART_RATE
                ) and not np.isnan(hr):
                    self.get_ave_values("heart_rate", hr)

                time_profile.append(datetime.now())

                # toggle auto stop
                # ANT+ or GPS speed is available
                if not np.isnan(spd) and self.config.G_MANUAL_STATUS == "START":
                    # speed from ANT+ or GPS
                    flag_spd = False
                    if spd >= settings.AUTOSTOP_CUTOFF:
                        flag_spd = True

                    # use moving status of accelerometer because of excluding erroneous speed values when stopping
                    flag_moving = False
                    if v["I2C"]["m_stat"] == 1:
                        flag_moving = True

                    # flag_moving is not considered (set True) as follows,
                    # accelerometer is not available (nan)
                    # ANT+ speed sensor is available
                    if (
                        np.isnan(v["I2C"]["m_stat"])
                        or settings.is_ant_device_enabled(ANTDevice.SPEED)
                        or settings.DUMMY_OUTPUT
                    ):
                        flag_moving = True

                    if (
                        self.config.G_STOPWATCH_STATUS == "STOP"
                        and flag_spd
                        and flag_moving
                        and self.config.logger is not None
                    ):
                        self.config.logger.start_and_stop()
                    elif (
                        self.config.G_STOPWATCH_STATUS == "START"
                        and (not flag_spd or not flag_moving)
                        and self.config.logger is not None
                    ):
                        self.config.logger.start_and_stop()

                # ANT+ or GPS speed is not available
                elif np.isnan(spd) and self.config.G_MANUAL_STATUS == "START":
                    # stop recording if speed is broken
                    if (
                        (
                            settings.is_ant_device_enabled(ANTDevice.SPEED)
                            or "timestamp" in v["GPS"]
                        )
                        and self.config.G_STOPWATCH_STATUS == "START"
                        and self.config.logger is not None
                    ):
                        self.config.logger.start_and_stop()
                # time.sleep(1)

                # auto backlight
                if self.config.display.use_auto_backlight and not np.isnan(
                    v["I2C"]["light"]
                ):
                    if v["I2C"]["light"] <= settings.AUTO_BACKLIGHT_CUTOFF:
                        self.config.display.set_brightness(3)
                        self.sensor_ant.set_light_mode(
                            "FLASH_LOW", auto=True, auto_id="auto_backlight"
                        )
                    else:
                        self.config.display.set_brightness(0)
                        self.sensor_ant.set_light_mode(
                            "OFF", auto=True, auto_id="auto_backlight"
                        )

                # break light
                self.brakelight_spd[:-1] = self.brakelight_spd[1:]
                self.brakelight_spd[-1] = self.values["integrated"]["speed"]
                if all(
                    (s < self.brakelight_spd_cutoff for s in self.brakelight_spd)
                ) or (
                    self.values["integrated"]["speed"] > self.brakelight_spd_cutoff
                    and self.brakelight_spd[0] - self.brakelight_spd[-1]
                    > self.brakelight_spd[0] * 0.05
                ):
                    self.sensor_ant.set_light_mode(
                        "FLASH_LOW", auto=True, auto_id="break_light"
                    )
                else:
                    self.sensor_ant.set_light_mode(
                        "OFF", auto=True, auto_id="break_light"
                    )

                # cpu and memory
                if _IMPORT_PSUTIL:
                    self.values["integrated"]["cpu_percent"] = int(
                        self.process.cpu_percent(interval=None)
                    )
                    self.values["integrated"][
                        "CPU_MEM"
                    ] = "{0:^2.0f}% ({1}) / ALL {2:^2.0f}%,  {3:^2.0f}%".format(
                        self.values["integrated"][
                            "cpu_percent"
                        ],  # self.process.cpu_percent(interval=None),
                        self.process.num_threads(),
                        psutil.cpu_percent(interval=None),
                        self.process.memory_percent(),
                    )

                # adjust loop time
                time_profile.append(datetime.now())
                sec_diff = []
                time_profile_sec = 0

                for i in range(len(time_profile)):
                    if i == 0:
                        continue

                    sec_diff.append(
                        "{0:.6f}".format(
                            (time_profile[i] - time_profile[i - 1]).total_seconds()
                        )
                    )
                    time_profile_sec += (
                        time_profile[i] - time_profile[i - 1]
                    ).total_seconds()
                if time_profile_sec > 1.5 * settings.SENSOR_INTERVAL:
                    app_logger.warning(
                        f"too long loop time: {datetime.now().strftime('%Y%m%d %H:%M:%S')}, sec_diff: {sec_diff}"
                    )

                loop_time = (datetime.now() - start_time).total_seconds()
                d1, d2 = divmod(loop_time, settings.SENSOR_INTERVAL)
                if d1 > settings.SENSOR_INTERVAL * 10:  # [s]
                    app_logger.warning(
                        f"too long loop_time({self.__class__.__name__}):{loop_time:.2f}, interval:{settings.SENSOR_INTERVAL:.1f}"
                    )
                    d1 = d2 = 0
                self.wait_time = settings.SENSOR_INTERVAL - d2
                self.actual_loop_interval = (d1 + 1) * settings.SENSOR_INTERVAL
        except asyncio.CancelledError:
            pass

    @staticmethod
    def conv_grade(gr):
        g = gr
        if -1.5 < g < 1.5:
            g = 0
        return int(g)

    def get_lp_filtered_value(self, value, pre):
        # value must be initialized with None
        if np.isnan(pre):
            o = value
        else:
            o = pre * (self.lp - 1) / self.lp + value / self.lp
        p = value
        return o, p

    def get_ave_values(self, k, v):
        for sec in self.average_secs:
            if len(self.average_values[k][sec]) < sec:
                self.average_values[k][sec].append(v)
            else:
                self.average_values[k][sec][:-1] = self.average_values[k][sec][1:]
                self.average_values[k][sec][-1] = v
            self.values["integrated"]["ave_{}_{}s".format(k, sec)] = int(
                np.mean(self.average_values[k][sec])
            )

    def calc_w_prime_balance(self, pwr):
        # https://medium.com/critical-powers/comparison-of-wbalance-algorithms-8838173e2c15

        v = self.values["integrated"]
        pwr_cp_diff = pwr - settings.POWER_CP
        # Waterworth algorithm
        if settings.POWER_W_PRIME_ALGORITHM == "WATERWORTH":
            if pwr < settings.POWER_CP:
                v["w_prime_power_sum"] = v["w_prime_power_sum"] + pwr
                v["w_prime_power_count"] = v["w_prime_power_count"] + 1
                v["pwr_mean_under_cp"] = (
                    v["w_prime_power_sum"] / v["w_prime_power_count"]
                )
                v["tau"] = (
                    546 * np.exp(-0.01 * (settings.POWER_CP - v["pwr_mean_under_cp"]))
                    + 316
                )
            v["w_prime_sum"] += max(0, pwr_cp_diff) * np.exp(v["w_prime_t"] / v["tau"])
            v["w_prime_t"] += settings.SENSOR_INTERVAL
            v["w_prime_balance"] = settings.POWER_W_PRIME - v["w_prime_sum"] * np.exp(
                -v["w_prime_t"] / v["tau"]
            )

        # Differential algorithm
        elif settings.POWER_W_PRIME_ALGORITHM == "DIFFERENTIAL":
            cp_pwr_diff = -pwr_cp_diff
            if cp_pwr_diff < 0:
                # consume
                v["w_prime_balance"] += cp_pwr_diff
            else:
                # recovery
                v["w_prime_balance"] += (
                    cp_pwr_diff
                    * (settings.POWER_W_PRIME - v["w_prime_balance"])
                    / settings.POWER_W_PRIME
                )

        v["w_prime_balance_normalized"] = round(
            v["w_prime_balance"] / settings.POWER_W_PRIME * 100, 1
        )
