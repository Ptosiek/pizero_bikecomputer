import asyncio
import datetime
import random

import numpy as np

from logger import app_logger
from modules.constants import ANTDevice
from modules.settings import settings
from .ant.ant_code import AntDeviceType
from .sensor import Sensor
from .ant.ant_device_ctrl import ANT_Device_CTRL
from .ant.ant_device_heartrate import ANT_Device_HeartRate
from .ant.ant_device_light import ANT_Device_Light
from .ant.ant_device_power import ANT_Device_Power
from .ant.ant_device_search import ANT_Device_Search
from .ant.ant_device_speed_cadence import (
    ANT_Device_Cadence,
    ANT_Device_Speed,
    ANT_Device_Speed_Cadence,
)
from .ant.ant_device_temperature import ANT_Device_Temperature


# ANT+
_SENSOR_ANT = False

try:
    from ant.easy.node import Node
    from ant.base.driver import find_driver, DriverNotFound

    # device test
    _driver = find_driver()
    _SENSOR_ANT = True
except ImportError:
    pass
except DriverNotFound:
    pass


if _SENSOR_ANT:
    app_logger.info("ANT")


class SensorANT(Sensor):
    # for openant
    node = None
    NETWORK_KEY = [0xB9, 0xA5, 0x21, 0xFB, 0xBD, 0x72, 0xC3, 0x45]
    NETWORK_NUM = 0x00
    CHANNEL = 0x00
    DEVICE_ALL = 0
    scanner = None
    searcher = None
    devices = None

    def sensor_init(self):
        self.devices = {}

        if settings.ANT_STATUS and not _SENSOR_ANT:
            settings.update_setting("ANT_STATUS", False)

        if settings.ANT_STATUS:
            self.node = Node()
            self.node.set_network_key(self.NETWORK_NUM, self.NETWORK_KEY)

        # initialize scan channel (reserve ch0)
        if _SENSOR_ANT:
            app_logger.info("detected ANT+ sensors")

        self.searcher = ANT_Device_Search(self.node, self.config, self.values)

        # auto connect ANT+ sensor from setting.conf
        if settings.ANT_STATUS and not settings.DUMMY_OUTPUT:
            for key in ANTDevice.keys():
                device_id, device_type = settings.get_ant_device(key)

                if settings.is_ant_device_enabled(key) and device_id:
                    self.connect_ant_sensor(key, device_id, device_type, False)
            return
        # otherwise, initialize
        else:
            for key in ANTDevice.keys():
                settings.set_ant_device_status(key, False)

                # TODO, should not do that, this seems to reset the settings when deactivating ant+ ?
                # this is basically doing setting.set_ant_device(key, None)
                # self.config.G_ANT["ID"][key] = 0
                # self.config.G_ANT["TYPE"][key] = 0

        # for dummy output
        # TODO, it should be reworked as it override the settings
        #  (original code prevented writing it to setting.conf with a check during write..)
        if not settings.ANT_STATUS and settings.DUMMY_OUTPUT:
            for key in ANTDevice.keys():
                # TODO, fix later (it's from original code)
                if key == ANTDevice.TEMPERATURE:
                    settings.set_ant_device_status(key, False)
                else:
                    settings.set_ant_device_status(key, True)

            settings.set_ant_device(ANTDevice.HEART_RATE, (0, AntDeviceType.HEART_RATE))
            settings.set_ant_device(
                ANTDevice.SPEED, (0, AntDeviceType.SPEED_AND_CADENCE)
            )
            settings.set_ant_device(
                ANTDevice.CADENCE, (0, AntDeviceType.SPEED_AND_CADENCE)
            )
            settings.set_ant_device(ANTDevice.POWER, (0, AntDeviceType.POWER))

            # init values
            self.values[(0, AntDeviceType.HEART_RATE)] = {}
            self.values[(0, AntDeviceType.SPEED_AND_CADENCE)] = {"distance": 0}
            self.values[(0, AntDeviceType.POWER)] = {}

            for key in [0x10, 0x11, 0x12]:
                self.values[(0, AntDeviceType.POWER)][key] = {"accumulated_power": 0}

        self.reset()

    def start_coroutine(self):
        asyncio.create_task(self.start())

    async def start(self):
        if settings.ANT_STATUS:
            await asyncio.get_running_loop().run_in_executor(None, self.node.start)

    def update(self):
        if settings.DUMMY_OUTPUT:
            hr_value = random.randint(70, 150)
            speed_value = random.randint(5, 30) / 3.6  # 5 - 30km/h [unit:m/s]
            cad_value = random.randint(60, 100)
            power_value = random.randint(0, 250)
            timestamp = datetime.datetime.now()

            cadence_device = settings.get_ant_device(ANTDevice.CADENCE)
            hear_rate_device = settings.get_ant_device(ANTDevice.HEART_RATE)
            speed_device = settings.get_ant_device(ANTDevice.SPEED)
            power_device = settings.get_ant_device(ANTDevice.POWER)

            if cadence_device in self.values:
                self.values[cadence_device]["cadence"] = cad_value
            if hear_rate_device in self.values:
                self.values[hear_rate_device].update(
                    {"heart_rate": hr_value, "timestamp": timestamp}
                )
            if speed_device in self.values:
                self.values[speed_device].update(
                    {"speed": speed_value, "timestamp": timestamp}
                )
            if power_device in self.values:
                self.values[power_device][0x10].update(
                    {"power": power_value, "timestamp": timestamp}
                )

            # DISTANCE, TOTAL_WORK
            if self.config.G_MANUAL_STATUS == "START":
                # DISTANCE: unit: m
                if not np.isnan(self.values[speed_device]["speed"]):
                    self.values[speed_device]["distance"] += (
                        self.values[speed_device]["speed"] * settings.SENSOR_INTERVAL
                    )
                # TOTAL_WORK: unit: j
                if not np.isnan(self.values[power_device][0x10]["power"]):
                    self.values[power_device][0x10]["accumulated_power"] += (
                        self.values[power_device][0x10]["power"]
                        * settings.SENSOR_INTERVAL
                    )

    def reset(self):
        for device in self.devices.values():
            device.reset_value()

    def quit(self):
        if not settings.ANT_STATUS:
            return

        self.searcher.set_wait_quick_mode()

        for device in self.devices.values():
            device.ant_state = "quit"
            device.disconnect(isCheck=True, isChange=False)  # USE: True -> True
        self.searcher.stop_search(resetWait=False)
        self.node.stop()

    def connect_ant_sensor(self, ant_name, device_id, device_type, status):
        if not settings.ANT_STATUS:
            return

        device = (device_id, device_type)

        # TODO move this to update AFTER connection succeeded instead
        settings.set_ant_device(ant_name, (device_id, device_type))

        self.searcher.stop_search(resetWait=False)

        settings.set_ant_device_status(ant_name, True)

        self.searcher.set_wait_normal_mode()

        # existing connection
        if status:
            return

        # reconnect
        if device in self.devices:
            # USE: True -> True
            self.devices[device].connect(isCheck=False, isChange=False)
            self.devices[device].ant_state = "connect_ant_sensor"
            self.devices[device].init_after_connect()
            return

        # newly connect
        self.values[device] = {}

        if device_type == AntDeviceType.HEART_RATE:
            self.devices[device] = ANT_Device_HeartRate(
                self.node, self.config, self.values[device], ant_name, device_id
            )
        elif device_type == AntDeviceType.SPEED_AND_CADENCE:
            self.devices[device] = ANT_Device_Speed_Cadence(
                self.node, self.config, self.values[device], ant_name, device_id
            )
        elif device_type == AntDeviceType.CADENCE:
            self.devices[device] = ANT_Device_Cadence(
                self.node, self.config, self.values[device], ant_name, device_id
            )
        elif device_type == AntDeviceType.SPEED:
            self.devices[device] = ANT_Device_Speed(
                self.node, self.config, self.values[device], ant_name, device_id
            )
        elif device_type == AntDeviceType.POWER:
            self.devices[device] = ANT_Device_Power(
                self.node, self.config, self.values[device], ant_name, device_id
            )
        elif device_type == AntDeviceType.LIGHT:
            self.devices[device] = ANT_Device_Light(
                self.node, self.config, self.values[device], ant_name, device_id
            )
        elif device_type == AntDeviceType.CONTROL:
            self.devices[device] = ANT_Device_CTRL(
                self.node, self.config, self.values[device], ant_name, device_id
            )
        elif device_type == AntDeviceType.TEMPERATURE:
            self.devices[device] = ANT_Device_Temperature(
                self.node, self.config, self.values[device], ant_name, device_id
            )
        self.devices[device].ant_state = "connect_ant_sensor"
        self.devices[device].init_after_connect()

    def disconnect_ant_sensor(self, ant_name):
        device = settings.get_ant_device(ant_name)

        if device in self.devices:
            self.devices[device].ant_state = "disconnect_ant_sensor"
            self.devices[device].disconnect(isCheck=True, isChange=True)

        for k in ANTDevice.keys():
            status = settings.is_ant_device_enabled(k)

            if status and settings.get_ant_device(k) == device:
                settings.set_ant_device(k, None)
                settings.set_ant_device_status(k, False)

    def set_light_mode(self, mode, auto=False, auto_id=None):
        if settings.is_ant_device_enabled(ANTDevice.LIGHT):
            return

        device = settings.get_ant_device(ANTDevice.LIGHT)

        if auto and (
            not settings.USE_AUTO_LIGHT or self.config.G_MANUAL_STATUS != "START"
        ):
            return
        self.devices[device].send_light_mode(mode, auto, auto_id)
