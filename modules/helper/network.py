import os
import datetime
import asyncio
import traceback
import concurrent

from logger import app_logger
from modules.settings import settings
from modules.utils.map import get_maptile_filename
from modules.utils.network import detect_network, download_files


class Network:
    config = None

    def __init__(self, config):
        self.config = config
        asyncio.create_task(self.download_worker())

    @staticmethod
    async def quit():
        await settings.DOWNLOAD_QUEUE.put(None)

    @staticmethod
    async def download_worker():
        failed = []
        # for urls, header, save_paths, params:
        while True:
            q = await settings.DOWNLOAD_QUEUE.get()

            if q is None:
                break

            try:
                res = await download_files(**q)
                settings.DOWNLOAD_QUEUE.task_done()
            except concurrent.futures._base.CancelledError:
                return

            # all False -> give up
            if not any(res) or res is None:
                failed.append((datetime.datetime.now(), q))
                app_logger.error("failed download")
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
                    await settings.DOWNLOAD_QUEUE.put(q)

    # tiles functions
    async def download_maptile(
        self, map_config, map_name, z, tiles, additional_download=False
    ):
        if not detect_network() or map_config[map_name]["url"] is None:
            return False

        map_settings = map_config[map_name]
        urls = []
        save_paths = []
        request_header = {}
        additional_var = {}

        if (
            map_config == settings.HEATMAP_OVERLAY_MAP_CONFIG
            and "strava_heatmap" in map_name
        ):
            additional_var["key_pair_id"] = self.config.G_STRAVA_COOKIE["KEY_PAIR_ID"]
            additional_var["policy"] = self.config.G_STRAVA_COOKIE["POLICY"]
            additional_var["signature"] = self.config.G_STRAVA_COOKIE["SIGNATURE"]
        elif map_config in [
            settings.RAIN_OVERLAY_MAP_CONFIG,
            settings.WIND_OVERLAY_MAP_CONFIG,
        ]:
            if map_settings["basetime"] is None or map_settings["validtime"] is None:
                return False

            additional_var["basetime"] = map_settings["basetime"]
            additional_var["validtime"] = map_settings["validtime"]

        # make header
        if map_settings.get("referer"):
            request_header["Referer"] = map_settings["referer"]

        if map_settings.get("user_agent"):
            request_header["User-Agent"] = settings.PRODUCT

        for tile in tiles:
            os.makedirs(f"maptile/{map_name}/{z}/{tile[0]}/", exist_ok=True)

            url = map_settings["url"].format(
                z=z, x=tile[0], y=tile[1], **additional_var
            )
            save_path = get_maptile_filename(map_name, z, *tile)
            urls.append(url)
            save_paths.append(save_path)

        await settings.DOWNLOAD_QUEUE.put(
            {"urls": urls, "headers": request_header, "save_paths": save_paths}
        )

        if additional_download:
            additional_urls = []
            additional_save_paths = []

            max_zoom_cond = True

            if (
                "max_zoomlevel" in map_settings
                and z + 1 >= map_settings["max_zoomlevel"]
            ):
                max_zoom_cond = False

            min_zoom_cond = True

            if (
                "min_zoomlevel" in map_settings
                and z - 1 <= map_settings["min_zoomlevel"]
            ):
                min_zoom_cond = False

            for tile in tiles:
                if max_zoom_cond:
                    for i in range(2):
                        os.makedirs(
                            f"maptile/{map_name}/{z + 1}/{2 * tile[0] + i}",
                            exist_ok=True,
                        )
                        for j in range(2):
                            url = map_settings["url"].format(
                                z=z + 1,
                                x=2 * tile[0] + i,
                                y=2 * tile[1] + j,
                                **additional_var,
                            )
                            save_path = get_maptile_filename(
                                map_name, z + 1, 2 * tile[0] + i, 2 * tile[1] + j
                            )
                            additional_urls.append(url)
                            additional_save_paths.append(save_path)

                if z - 1 <= 0:
                    continue

                if min_zoom_cond:
                    os.makedirs(
                        f"maptile/{map_name}/{z - 1}/{int(tile[0] / 2)}",
                        exist_ok=True,
                    )
                    zoomout_url = map_settings["url"].format(
                        z=z - 1,
                        x=int(tile[0] / 2),
                        y=int(tile[1] / 2),
                        **additional_var,
                    )
                    if zoomout_url not in additional_urls:
                        additional_urls.append(zoomout_url)
                        additional_save_paths.append(
                            get_maptile_filename(
                                map_name, z - 1, int(tile[0] / 2), int(tile[1] / 2)
                            )
                        )

            if additional_urls:
                await settings.DOWNLOAD_QUEUE.put(
                    {
                        "urls": additional_urls,
                        "headers": request_header,
                        "save_paths": additional_save_paths,
                    }
                )

        return True
