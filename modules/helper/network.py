import os
from datetime import datetime
import asyncio
import json
import concurrent

import aiohttp
import aiofiles

from modules.utils.map import get_maptile_filename
from modules.utils.network import detect_network
from modules.utils.cmd import (
    exec_cmd,
    exec_cmd_return_value,
)

from logger import app_logger

COROUTINE_SEM = 100
BT_TETHERING_TIMEOUT_SEC = 15
BOOT_FILE = "/boot/config.txt"


async def get_json(url, params=None, headers=None, timeout=10):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url, params=params, headers=headers, timeout=timeout
        ) as res:
            json = await res.json()
            return json


async def post(url, headers=None, params=None, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, headers=headers, params=params, data=data
        ) as res:
            json = await res.json()
            return json


async def get_http_request(session, url, save_path, headers, params):
    try:
        async with session.get(url, headers=headers, params=params) as dl_file:
            if dl_file.status == 200:
                async with aiofiles.open(save_path, mode="wb") as f:
                    await f.write(await dl_file.read())
                return True
            else:
                app_logger.info(
                    f"dl_file status {dl_file.status}: {dl_file.reason}\n{url}"
                )
                return False
    except asyncio.CancelledError:
        return False
    except:
        return False


async def download_files(urls, save_paths, headers=None, params=None):
    tasks = []
    async with asyncio.Semaphore(COROUTINE_SEM):
        async with aiohttp.ClientSession() as session:
            for url, save_path in zip(urls, save_paths):
                tasks.append(
                    get_http_request(session, url, save_path, headers, params)
                )
            res = await asyncio.gather(*tasks)
    return res


class Network:
    config = None
    bt_cmd_lock = False
    bt_tethering_status = {}
    bt_tethering_last_close_time = None

    def __init__(self, config):
        self.config = config

        self.download_queue = asyncio.Queue()
        asyncio.create_task(self.download_worker())

    async def quit(self):
        await self.download_queue.put(None)

    async def download_worker(self):
        failed = []
        f_name = self.download_worker.__name__
        # for urls, header, save_paths, params:
        while True:
            if self.download_queue.qsize() == 0:
                await self.close_bt_tethering(f_name)
            q = await self.download_queue.get()
            if q is None:
                break

            res = None
            try:
                await self.open_bt_tethering(f_name)
                # app_logger.info(f"start download files({len(q['urls'])}), {q['urls'][0]} / {self.download_queue.qsize()}")
                res = await download_files(**q)
                # app_logger.info(res)
                self.download_queue.task_done()
            except concurrent.futures._base.CancelledError:
                return

            # all False -> give up
            if not any(res) or res is None:
                failed.append((datetime.now(), q))
                app_logger.error(f"failed download ({len(q['urls'])}), {bool(detect_network())}")
                app_logger.debug(q["urls"])
            # retry
            elif not all(res) and len(q["urls"]) and len(q["urls"]) == len(res):
                retry_urls = []
                retry_save_paths = []
                for url, save_path, status in zip(q["urls"], q["save_paths"], res):
                    if not status:
                        retry_urls.append(url)
                        retry_save_paths.append(save_path)
                if len(retry_urls):
                    q["urls"] = retry_urls
                    q["save_paths"] = retry_save_paths
                    await self.download_queue.put(q)

    # tiles functions
    async def download_maptile(
        self, map_config, map_name, z, tiles, additional_download=False
    ):
        if not self.config.G_AUTO_BT_TETHERING and not detect_network():
            return False

        map_settings = map_config[map_name]
        urls = []
        save_paths = []
        request_header = {}
        additional_var = {}

        # for overlay map(heatmap)
        if (
            map_config == self.config.G_HEATMAP_OVERLAY_MAP_CONFIG
            and "strava_heatmap" in map_name
        ):
            additional_var["key_pair_id"] = self.config.G_STRAVA_COOKIE["KEY_PAIR_ID"]
            additional_var["policy"] = self.config.G_STRAVA_COOKIE["POLICY"]
            additional_var["signature"] = self.config.G_STRAVA_COOKIE["SIGNATURE"]
        # for overlay map (rainmap/windmap)
        elif map_config in [
            self.config.G_RAIN_OVERLAY_MAP_CONFIG,
            self.config.G_WIND_OVERLAY_MAP_CONFIG,
        ]:
            if map_settings["basetime"] is None or map_settings["validtime"] is None:
                return False
            additional_var["basetime"] = map_settings["basetime"]
            additional_var["validtime"] = map_settings["validtime"]
            if map_name.startswith("jpn_scw"):
                if map_settings["subdomain"] is None:
                    return False
                additional_var["subdomain"] = map_settings["subdomain"]

        # make header
        if map_settings.get("referer"):
            request_header["Referer"] = map_settings["referer"]
        if map_settings.get("user_agent"):
            request_header["User-Agent"] = self.config.G_PRODUCT

        basetime = additional_var.get("basetime", None)
        validtime = additional_var.get("validtime", None)

        for tile in tiles:
            self.make_maptile_dir(map_name, z, tile[0], basetime, validtime)
            url = map_settings["url"].format(
                z=z, x=tile[0], y=tile[1], **additional_var
            )
            save_path = get_maptile_filename(
                map_name, z, *tile, basetime=basetime, validtime=validtime
            )
            urls.append(url)
            save_paths.append(save_path)

        await self.download_queue.put(
            {"urls": urls, "headers": request_header, "save_paths": save_paths}
        )

        if not additional_download:
            return True
        
        additional_urls = []
        additional_save_paths = []
        z_p = z + 1 # z plus 1
        z_m = z - 1 # z minus 1

        max_zoom_cond = True
        if "max_zoomlevel" in map_settings and z_p >= map_settings["max_zoomlevel"]:
            max_zoom_cond = False

        min_zoom_cond = True
        if "min_zoomlevel" in map_settings and z_m <= map_settings["min_zoomlevel"]:
            min_zoom_cond = False

        for tile in tiles:
            if max_zoom_cond:
                for i in range(2):
                    x = 2 * tile[0] + i
                    self.make_maptile_dir(map_name, z_p, x, basetime, validtime)
                    for j in range(2):
                        y = 2 * tile[1] + j
                        url = map_settings["url"].format(z=z_p, x=x, y=y, **additional_var)
                        save_path = get_maptile_filename(
                            map_name, z_p, x, y, basetime=basetime, validtime=validtime
                        )
                        additional_urls.append(url)
                        additional_save_paths.append(save_path)

            if z_m <= 0:
                continue

            if min_zoom_cond:
                x = int(tile[0] / 2)
                y = int(tile[1] / 2)
                self.make_maptile_dir(map_name, z_m, x, basetime, validtime)
                url = map_settings["url"].format(z=z_m, x=x, y=y, **additional_var)
                if url not in additional_urls:
                    save_path = get_maptile_filename(
                        map_name, z_m, x, y, basetime=basetime, validtime=validtime
                    )
                    additional_urls.append(url)
                    additional_save_paths.append(save_path)

        if additional_urls:
            await self.download_queue.put(
                {
                    "urls": additional_urls,
                    "headers": request_header,
                    "save_paths": additional_save_paths,
                }
            )

        return True

    @staticmethod
    def make_maptile_dir(map_name, z, y, basetime, validtime):
        if basetime is not None and validtime is not None:
            map_dir = f"maptile/{map_name}/{basetime}/{validtime}/{z}/{y}/"
        else:
            map_dir = f"maptile/{map_name}/{z}/{y}/"
        os.makedirs(map_dir, exist_ok=True)

    async def bluetooth_tethering(self, disconnect=False):
        if (
            not self.config.G_IS_RASPI
            or not self.config.G_BT_USE_ADDRESS
            or not self.config.bt_pan
        ):
            return

        if not disconnect:
            res = await self.config.bt_pan.connect_tethering(
                self.config.G_BT_ADDRESSES[self.config.G_BT_USE_ADDRESS]
            )
        else:
            res = await self.config.bt_pan.disconnect_tethering(
                self.config.G_BT_ADDRESSES[self.config.G_BT_USE_ADDRESS]
            )
        return bool(res)

    async def open_bt_tethering(self, f_name):

        if not self.config.G_AUTO_BT_TETHERING:
            return True

        if self.bt_cmd_lock:
            return detect_network()
        
        if detect_network():
            self.bt_tethering_status[f_name] = True
            return True

        self.bt_cmd_lock = True
        bt_pan_status = await self.bluetooth_tethering()
        count = 0

        while (
            bt_pan_status
            and not detect_network()
            and count < BT_TETHERING_TIMEOUT_SEC
        ):
            await asyncio.sleep(2)
            count += 2

        if not bt_pan_status or count >= BT_TETHERING_TIMEOUT_SEC:
            if bt_pan_status:
                await self.bluetooth_tethering(disconnect=True)
            await asyncio.sleep(5)
            self.bt_cmd_lock = False
            app_logger.error(f"[BT] connect error, network: {bool(detect_network())}({count}s), f_name: {f_name}")
            return False

        await asyncio.sleep(5)
        self.bt_tethering_status[f_name] = True
        app_logger.info(f"[BT] connect, network: {bool(detect_network())}({count}s), f_name: {f_name}")
        
        return True

    async def close_bt_tethering(self, f_name):

        if not self.config.G_AUTO_BT_TETHERING:
            return True

        self.bt_tethering_status[f_name] = False
        if any(self.bt_tethering_status.values()):
            return True

        await self.bluetooth_tethering(disconnect=True)
        await asyncio.sleep(5)
        self.bt_cmd_lock = False
        self.bt_tethering_last_close_time = datetime.now()
        network_status = bool(detect_network())
        app_logger.info(f"[BT] disconnect, network: {network_status}, f_name: {f_name}")
        return not network_status
    
    def get_wifi_bt_status(self):
        if not self.config.G_IS_RASPI:
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
        if not self.config.G_IS_RASPI:
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

    def hardware_wifi_bt(self, status):
        app_logger.info(f"Hardware Wifi/BT: {status}")
        if self.config.G_IS_RASPI:
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
