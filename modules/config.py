import asyncio
import json
import logging
import os
import shutil
from datetime import datetime
from glob import glob

from logger import CustomRotatingFileHandler, app_logger
from modules.button_config import Button_Config
from modules.state import AppState
from modules.utils.cmd import (
    exec_cmd,
    exec_cmd_return_value,
    is_running_as_service,
)
from modules.settings import settings
from modules.utils.map import check_map_dir
from modules.utils.timer import Timer

BOOT_FILE = "/boot/config.txt"


class Config:
    #######################
    # configurable values #
    #######################

    # stopwatch state
    G_MANUAL_STATUS = "INIT"
    G_STOPWATCH_STATUS = "INIT"  # with Auto Pause

    # ANT+ setting (overwritten with setting.conf)
    # [Todo] multiple pairing(2 or more riders), ANT+ ctrl(like edge remote)
    G_ANT = {
        # ANT+ interval internal variable: 0:4Hz(0.25s), 1:2Hz(0.5s), 2:1Hz(1.0s)
        # initialized by settings.ANT_INTERVAL in __init()__
        "INTERVAL": 2,
        "STATUS": True,
        "USE": {
            "HR": False,
            "SPD": False,
            "CDC": False,
            "PWR": False,
            "LGT": False,
            "CTRL": False,
            "TEMP": False,
        },
        "NAME": {
            "HR": "HeartRate",
            "SPD": "Speed",
            "CDC": "Cadence",
            "PWR": "Power",
            "LGT": "Light",
            "CTRL": "Control",
            "TEMP": "Temperature",
        },
        "ID": {
            "HR": 0,
            "SPD": 0,
            "CDC": 0,
            "PWR": 0,
            "LGT": 0,
            "CTRL": 0,
            "TEMP": 0,
        },
        "TYPE": {
            "HR": 0,
            "SPD": 0,
            "CDC": 0,
            "PWR": 0,
            "LGT": 0,
            "CTRL": 0,
            "TEMP": 0,
        },
        "ID_TYPE": {
            "HR": 0,
            "SPD": 0,
            "CDC": 0,
            "PWR": 0,
            "LGT": 0,
            "CTRL": 0,
            "TEMP": 0,
        },
        "TYPES": {
            "HR": (0x78,),
            "SPD": (0x79, 0x7B),
            "CDC": (0x79, 0x7A, 0x0B),
            "PWR": (0x0B,),
            "LGT": (0x23,),
            "CTRL": (0x10,),
            "TEMP": (0x19,),
        },
    }

    # Bluetooth tethering
    G_BT_ADDRESSES = {}
    G_BT_USE_ADDRESS = ""

    #######################
    # class objects       #
    #######################
    logger = None
    display = None
    network = None
    api = None
    bt_pan = None
    ble_uart = None
    setting = None
    state = None
    gui_class = None
    gui = None
    gui_config = None
    boot_time = 0

    def __init__(self):
        if settings.DEBUG:
            app_logger.setLevel(logging.DEBUG)

        # read setting.conf and state.pickle
        self.state = AppState()

        # make sure all folders exist
        os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
        os.makedirs(settings.LOG_DIR, exist_ok=True)

        if settings.LOG_DEBUG_FILE:
            delay = not os.path.exists(settings.LOG_DEBUG_FILE)
            fh = CustomRotatingFileHandler(settings.LOG_DEBUG_FILE, delay=delay)
            fh.doRollover()
            fh_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            fh.setFormatter(fh_formatter)
            app_logger.addHandler(fh)

        # layout file
        if not os.path.exists(settings.LAYOUT_FILE):
            default_layout_file = os.path.join("layouts", "layout-cycling.yaml")
            shutil.copy(default_layout_file, settings.LAYOUT_FILE)

        if settings.CURRENT_MAP.get("use_mbtiles") and not os.path.exists(
            os.path.join("maptile", f"{settings.MAP}.mbtiles")
        ):
            settings.CURRENT_MAP["use_mbtiles"] = False

        check_map_dir()

        # set ant interval. 0:4Hz(0.25s), 1:2Hz(0.5s), 2:1Hz(1.0s)
        if settings.ANT_INTERVAL == 0.25:
            self.G_ANT["INTERVAL"] = 0
        elif settings.ANT_INTERVAL == 0.5:
            self.G_ANT["INTERVAL"] = 1
        else:
            self.G_ANT["INTERVAL"] = 2

        # coroutine loop
        self.init_loop()

        self.log_time = datetime.now()

        self.button_config = Button_Config(self)

    def init_loop(self, call_from_gui=False):
        if settings.GUI_MODE == "PyQt":
            if call_from_gui:
                # workaround for latest qasync and older version(~0.24.0)
                asyncio.events._set_running_loop(self.loop)
                asyncio.set_event_loop(self.loop)
                self.start_coroutine()
        else:
            self.loop = asyncio.get_event_loop()

    def import_gui(self):
        if settings.GUI_MODE == "PyQt":
            from modules.gui_pyqt import GUI_PyQt

            self.gui_class = GUI_PyQt
        else:
            raise ValueError(f"{settings.GUI_MODE} mode not supported")

    def start_gui(self):
        if self.gui_class:
            self.gui_class(self)

    def start_coroutine(self):
        self.logger.start_coroutine()
        self.display.start_coroutine()

        # delay init start
        asyncio.create_task(self.delay_init())

    async def delay_init(self):
        await asyncio.sleep(0.01)
        t = Timer(auto_start=True, auto_log=True, text="delay init: {0:.3f} sec")

        # network
        await self.gui.set_boot_status("initialize network modules...")
        from modules.helper.api import Api
        from modules.helper.network import Network

        self.api = Api(self)
        self.network = Network(self)

        # bluetooth
        if settings.IS_RASPI:
            await self.gui.set_boot_status("initialize bluetooth modules...")

            from modules.helper.bt_pan import (
                BTPanDbus,
                BTPanDbusNext,
                HAS_DBUS_NEXT,
                HAS_DBUS,
            )

            if HAS_DBUS_NEXT:
                self.bt_pan = BTPanDbusNext()
            elif HAS_DBUS:
                self.bt_pan = BTPanDbus()
            if HAS_DBUS_NEXT or HAS_DBUS:
                is_available = await self.bt_pan.check_dbus()
                if is_available:
                    self.G_BT_ADDRESSES = await self.bt_pan.find_bt_pan_devices()

        # logger, sensor
        await self.gui.set_boot_status("initialize sensor...")
        self.logger.delay_init()

        # GadgetBridge (has to be before gui but after sensors for proper init state of buttons)
        if settings.IS_RASPI:
            try:
                from modules.helper.ble_gatt_server import GadgetbridgeService

                self.ble_uart = GadgetbridgeService(
                    settings.PRODUCT,
                    self.logger.sensor.sensor_gps,
                    self.gui,
                    (
                        self.state.get_value("GB", False),
                        self.state.get_value("GB_gps", False),
                    ),
                )

            except Exception as e:  # noqa
                app_logger.info(f"Gadgetbridge service not initialized: {e}")

        # gui
        await self.gui.set_boot_status("initialize screens...")
        self.gui.delay_init()

        if settings.HEADLESS:
            asyncio.create_task(self.keyboard_check())

        # resume BT
        if settings.IS_RASPI:
            self.G_BT_USE_ADDRESS = self.state.get_value(
                "G_BT_USE_ADDRESS", self.G_BT_USE_ADDRESS
            )
            # resume BT tethering
            if self.G_BT_USE_ADDRESS:
                await self.bluetooth_tethering()

        delta = t.stop()
        self.boot_time += delta

        await self.logger.resume_start_stop()

    async def keyboard_check(self):
        try:
            while True:
                app_logger.info(
                    "s:start/stop, l: lap, r:reset, p: previous screen, n: next screen, q: quit"
                )
                key = await asyncio.get_running_loop().run_in_executor(
                    None, input, "> "
                )

                if key == "s":
                    self.logger.start_and_stop_manual()
                elif key == "l":
                    self.logger.count_laps()
                elif key == "r":
                    self.logger.reset_count()
                elif key == "n" and self.gui:
                    self.gui.scroll_next()
                elif key == "p" and self.gui:
                    self.gui.scroll_prev()
                elif key == "q" and self.gui:
                    await self.quit()
                ##### temporary #####
                # test hardware key signals
                elif key == "m" and self.gui:
                    self.gui.enter_menu()
                elif key == "v" and self.gui:
                    self.gui.press_space()
                elif key == "," and self.gui:
                    self.gui.press_tab()
                elif key == "." and self.gui:
                    self.gui.press_shift_tab()
                elif key == "b" and self.gui:
                    self.gui.back_menu()
                elif key == "c" and self.gui:
                    self.gui.get_screenshot()
        except asyncio.CancelledError:
            pass

    def set_logger(self, logger):
        self.logger = logger

    def set_display(self, display, display_name):
        self.display = display
        settings.update_setting("DISPLAY", display_name)

    async def kill_tasks(self):
        tasks = asyncio.all_tasks()
        current_task = asyncio.current_task()
        for task in tasks:
            if settings.GUI_MODE == "PyQt":
                if task == current_task or task.get_coro().__name__ in [
                    "update_display"
                ]:
                    continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                app_logger.info(f"cancel task {task.get_coro().__qualname__}")
            else:
                pass

    async def quit(self):
        app_logger.info("quit")
        if self.ble_uart is not None:
            await self.ble_uart.quit()
        await self.network.quit()

        if self.G_MANUAL_STATUS == "START":
            self.logger.start_and_stop_manual()
        self.display.quit()

        await self.logger.quit()
        settings.save()
        self.state.delete()

        await asyncio.sleep(0.5)
        await self.kill_tasks()
        self.logger.remove_handler()
        app_logger.info("quit done")

    @staticmethod
    def poweroff():
        # TODO
        #  should be replaced by quit() with power_off option
        #  keep the logic for now but remove the shutdown service eg:
        #  if we are running through a service, stop it and issue power-off command (on rasp-pi only)

        # this returns 0 if active

        if is_running_as_service():
            exec_cmd(["sudo", "systemctl", "stop", "pizero_bikecomputer"])
        if settings.IS_RASPI:
            exec_cmd(["sudo", "poweroff"])

    @staticmethod
    def reboot():
        if settings.IS_RASPI:
            exec_cmd(["sudo", "reboot"])

    def update_application(self):
        if settings.IS_RASPI:
            exec_cmd(["git", "pull", "origin", "master"])
            self.restart_application()

    @staticmethod
    def restart_application():
        if settings.IS_RASPI:
            exec_cmd(["sudo", "systemctl", "restart", "pizero_bikecomputer"])

    @staticmethod
    def hardware_wifi_bt(status):
        app_logger.info(f"Hardware Wifi/BT: {status}")
        if settings.IS_RASPI:
            with open(BOOT_FILE, "r") as f:
                data = f.read()
            for dev in ["wifi", "bt"]:
                disable = f"dtoverlay=disable-{dev}"
                if status:
                    if disable in data and f"#{disable}" not in data:
                        # comment it
                        exec_cmd(
                            [
                                "sudo",
                                "sed",
                                "-i",
                                rf"s/^dtoverlay\=disable\-{dev}/\#dtoverlay\=disable\-{dev}/",
                                BOOT_FILE,
                            ],
                            False,
                        )
                    # else nothing to do it's not disabled then (not present or commented)
                else:
                    if f"#{disable}" in data:
                        # uncomment it, so it's disabled
                        exec_cmd(
                            [
                                "sudo",
                                "sed",
                                "-i",
                                rf"s/^\#dtoverlay\=disable\-{dev}/dtoverlay\=disable\-{dev}/",
                                BOOT_FILE,
                            ],
                            False,
                        )
                    elif disable in data:
                        # do nothing it's already the proper state...
                        pass
                    else:
                        exec_cmd(
                            ["sudo", "sed", "-i", f"$a{disable}", BOOT_FILE], False
                        )
            # UART configuration will change if we disable bluetooth
            # https://www.raspberrypi.com/documentation/computers/configuration.html#primary-and-secondary-uart
            if status:
                exec_cmd(
                    [
                        "sudo",
                        "sed",
                        "-i",
                        "-e",
                        r's/^\#DEVICES\="\/dev\/ttyS0"/DEVICES\="\/dev\/ttyS0"/',
                        "/etc/default/gpsd",
                    ],
                    False,
                )
                exec_cmd(
                    [
                        "sudo",
                        "sed",
                        "-i",
                        "-e",
                        r's/^DEVICES\="\/dev\/ttyAMA0"/\#DEVICES\="\/dev\/ttyAMA0"/',
                        "/etc/default/gpsd",
                    ],
                    False,
                )
            else:
                exec_cmd(
                    [
                        "sudo",
                        "sed",
                        "-i",
                        "-e",
                        r's/^DEVICES\="\/dev\/ttyS0"/\#DEVICES\="\/dev\/ttyS0"/',
                        "/etc/default/gpsd",
                    ],
                    False,
                )
                exec_cmd(
                    [
                        "sudo",
                        "sed",
                        "-i",
                        "-e",
                        r's/^\#DEVICES\="\/dev\/ttyAMA0"/DEVICES\="\/dev\/ttyAMA0"/',
                        "/etc/default/gpsd",
                    ],
                    False,
                )

    def get_wifi_bt_status(self):
        if not settings.IS_RASPI:
            return False, False

        status = {"wlan": False, "bluetooth": False}
        try:
            # json option requires raspbian buster
            raw_status = exec_cmd_return_value(
                ["sudo", "rfkill", "--json"], cmd_print=False
            )
            json_status = json.loads(raw_status)
            # "": Raspberry Pi OS, "rfkilldevices":
            self.parse_wifi_bt_json(json_status, status, ["", "rfkilldevices"])
        except Exception as e:
            app_logger.warning(f"Exception occurred trying to get wifi/bt status: {e}")
        return status["wlan"], status["bluetooth"]

    @staticmethod
    def parse_wifi_bt_json(json_status, status, keys):
        get_status = False
        for k in keys:
            if k not in json_status:
                continue
            for device in json_status[k]:
                if "type" not in device or device["type"] not in ["wlan", "bluetooth"]:
                    continue
                if device["soft"] == "unblocked" and device["hard"] == "unblocked":
                    status[device["type"]] = True
                    get_status = True
            if get_status:
                return

    def onoff_wifi_bt(self, key=None):
        # in the future, manage with pycomman
        if not settings.IS_RASPI:
            return

        onoff_cmd = {
            "Wifi": {
                True: ["sudo", "rfkill", "block", "wifi"],
                False: ["sudo", "rfkill", "unblock", "wifi"],
            },
            "Bluetooth": {
                True: ["sudo", "rfkill", "block", "bluetooth"],
                False: ["sudo", "rfkill", "unblock", "bluetooth"],
            },
        }
        status = {}
        status["Wifi"], status["Bluetooth"] = self.get_wifi_bt_status()
        exec_cmd(onoff_cmd[key][status[key]])

    async def bluetooth_tethering(self, disconnect=False):
        if not settings.IS_RASPI or not self.G_BT_USE_ADDRESS or not self.bt_pan:
            return

        if not disconnect:
            res = await self.bt_pan.connect_tethering(
                self.G_BT_ADDRESSES[self.G_BT_USE_ADDRESS]
            )
        else:
            res = await self.bt_pan.disconnect_tethering(
                self.G_BT_ADDRESSES[self.G_BT_USE_ADDRESS]
            )
        return bool(res)

    @staticmethod
    def get_courses():
        dirs = sorted(
            glob(os.path.join(settings.COURSE_DIR, "*.tcx")),
            key=lambda f: os.stat(f).st_mtime,
            reverse=True,
        )

        # heavy: delayed updates required
        # def get_course_info(c):
        #   pattern = {
        #       "name": re.compile(r"<Name>(?P<text>[\s\S]*?)</Name>"),
        #       "distance_meters": re.compile(
        #           r"<DistanceMeters>(?P<text>[\s\S]*?)</DistanceMeters>"
        #       ),
        #       # "track": re.compile(r'<Track>(?P<text>[\s\S]*?)</Track>'),
        #       # "altitude": re.compile(r'<AltitudeMeters>(?P<text>[^<]*)</AltitudeMeters>'),
        #   }
        #   info = {}
        #   with open(c, "r", encoding="utf-8_sig") as f:
        #       tcx = f.read()
        #       match_name = pattern["name"].search(tcx)
        #       if match_name:
        #           info["name"] = match_name.group("text").strip()
        #
        #       match_distance_meter = pattern["distance_meters"].search(tcx)
        #       if match_distance_meter:
        #           info["distance"] = float(match_distance_meter.group("text").strip())
        #   return info

        return [
            {
                "path": f,
                "name": os.path.basename(f),
                # **get_course_info(f)
            }
            for f in dirs
            if os.path.isfile(f) and f != settings.COURSE_FILE_PATH
        ]
