import asyncio
import concurrent
import datetime

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
    async def download_maptiles(self, map_info, z, tiles, additional_download=False):
        if not detect_network() or not map_info.url:
            return False

        urls = []
        save_paths = []
        request_header = {}
        additional_var = {}

        if map_info.time_based:
            if not map_info.basetime or not map_info.validtime:
                return False

            additional_var["basetime"] = map_info.basetime
            additional_var["validtime"] = map_info.validtime

        # make header
        if map_info.referer:
            request_header["Referer"] = map_info.referer

        if map_info.user_agent:
            request_header["User-Agent"] = settings.PRODUCT

        for tile in tiles:
            p = settings.MAPTILE_DIR / map_info.name / str(z) / str(tile[0])
            p.mkdir(parents=True, exist_ok=True)

            url = map_info.url.format(z=z, x=tile[0], y=tile[1], **additional_var)
            save_path = get_maptile_filename(map_info.name, z, *tile)
            urls.append(url)
            save_paths.append(save_path)

        await settings.DOWNLOAD_QUEUE.put(
            {"urls": urls, "headers": request_header, "save_paths": save_paths}
        )

        if additional_download:
            additional_urls = []
            additional_save_paths = []

            max_zoom_cond = True

            if z + 1 >= map_info.max_zoomlevel:
                max_zoom_cond = False

            min_zoom_cond = True

            if z - 1 <= map_info.min_zoomlevel:
                min_zoom_cond = False

            for tile in tiles:
                if max_zoom_cond:
                    for i in range(2):
                        p = (
                            settings.MAPTILE_DIR
                            / map_info.name
                            / str(z + 1)
                            / str(2 * tile[0] + i)
                        )
                        p.mkdir(parents=True, exist_ok=True)

                        for j in range(2):
                            url = map_info.url.format(
                                z=z + 1,
                                x=2 * tile[0] + i,
                                y=2 * tile[1] + j,
                                **additional_var,
                            )
                            save_path = get_maptile_filename(
                                map_info.name,
                                z + 1,
                                2 * tile[0] + i,
                                2 * tile[1] + j,
                            )
                            additional_urls.append(url)
                            additional_save_paths.append(save_path)

                if z - 1 <= 0:
                    continue

                if min_zoom_cond:
                    p = (
                        settings.MAPTILE_DIR
                        / map_info.name
                        / str(z - 1)
                        / str(int(tile[0] / 2))
                    )
                    p.mkdir(parents=True, exist_ok=True)

                    zoomout_url = map_info.url.format(
                        z=z - 1,
                        x=int(tile[0] / 2),
                        y=int(tile[1] / 2),
                        **additional_var,
                    )
                    if zoomout_url not in additional_urls:
                        additional_urls.append(zoomout_url)
                        additional_save_paths.append(
                            get_maptile_filename(
                                map_info.name,
                                z - 1,
                                int(tile[0] / 2),
                                int(tile[1] / 2),
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
