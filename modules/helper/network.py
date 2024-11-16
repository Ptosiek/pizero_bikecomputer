import asyncio
import concurrent
import datetime

from logger import app_logger
from modules.utils.network import download_files


class Network:
    # asyncio semaphore and queues
    COROUTINE_SEM = 100

    def __init__(self, queue):
        asyncio.create_task(self.download_worker())
        self.queue = queue

    async def quit(self):
        await self.queue.put(None)

    async def download_worker(self):
        failed = []
        # for urls, header, save_paths, params:
        while True:
            q = await self.queue.get()

            if q is None:
                break

            try:
                res = await download_files(**q, max_concurrency=self.COROUTINE_SEM)
                self.queue.task_done()
            except concurrent.futures._base.CancelledError:
                return

            # all False -> give up
            if not any(res) or res is None:
                failed.append((datetime.datetime.now(), q))
                app_logger.error("failed download")
                app_logger.debug(q["urls_with_path"])
            # retry
            elif (
                not all(res)
                and len(q["urls_with_path"])
                and len(q["urls_with_path"]) == len(res)
            ):
                retry_urls_with_path = []
                for url_with_path, status in zip(q["urls_with_path"], res):
                    if not status:
                        retry_urls_with_path.append(url_with_path)
                if len(retry_urls_with_path):
                    q["urls_with_path"] = retry_urls_with_path
                    await self.queue.put(q)
