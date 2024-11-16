import asyncio
import socket
from pathlib import Path

import aiohttp
import aiofiles
import aiofiles.os

from logger import app_logger


def detect_network():
    try:
        socket.setdefaulttimeout(3)
        connect_interface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_interface.connect(("8.8.8.8", 53))
        return connect_interface.getsockname()[0]
    except socket.error:
        return False


async def download_file(session, url, save_path, headers, params):
    try:
        async with session.get(url, headers=headers, params=params) as dl_file:
            if dl_file.status == 200:
                await aiofiles.os.makedirs(Path(save_path).parent, exist_ok=True)

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
    except Exception as e:
        app_logger.warning(f"Failed to download file: {e}")
        return False


async def download_files(urls_with_path, headers=None, params=None, max_concurrency=-1):
    tasks = []

    async with asyncio.Semaphore(max_concurrency):
        async with aiohttp.ClientSession() as session:
            for url, save_path in urls_with_path:
                tasks.append(download_file(session, url, save_path, headers, params))
            res = await asyncio.gather(*tasks)
    return res


async def get_json(url, params=None, headers=None, timeout=10):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url, params=params, headers=headers, timeout=timeout
        ) as res:
            json_resp = await res.json()
            return json_resp


async def post(url, headers=None, params=None, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, params=params, data=data) as res:
            json_resp = await res.json()
            return json_resp
