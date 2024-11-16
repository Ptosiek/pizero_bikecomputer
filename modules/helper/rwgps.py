import json

import aiofiles

from logger import app_logger
from modules.settings import settings
from modules.utils.network import detect_network, get_json, post


BASE_URL = "https://ridewithgps.com"
LIMIT = 10


class RWGPS:
    current_offset = 0
    nb_routes = None
    user_id = None

    @property
    def get_params(self):
        return {
            "apikey": settings.RWGPS_APIKEY,
            "version": "2",
            "auth_token": settings.RWGPS_TOKEN,
        }

    @staticmethod
    def check_files(route_id, first_download=False):
        save_paths = [
            settings.RWGS_ROUTE_DOWNLOAD_DIR / f"course-{route_id}.json",
            settings.RWGS_ROUTE_DOWNLOAD_DIR / f"preview-{route_id}.png",
        ]

        if not first_download:
            save_paths += [
                settings.RWGS_ROUTE_DOWNLOAD_DIR / f"elevation_profile-{route_id}.jpg",
                settings.RWGS_ROUTE_DOWNLOAD_DIR / f"course-{route_id}.tcx",
            ]

        for filename in save_paths:
            if not filename.exists() or not filename.stat().st_size:
                return False

        return True

    @staticmethod
    def get_route_privacycode(route_id):
        filename = settings.RWGS_ROUTE_DOWNLOAD_DIR / f"course-{route_id}.json"

        with filename.open() as json_file:
            json_contents = json.load(json_file)

            return json_contents["route"].get("privacy_code", None)

    async def get_route_files(self, route_id, with_privacy_code=False):
        params = self.get_params

        if not with_privacy_code:
            urls_with_path = (
                (
                    f"{BASE_URL}/routes/{route_id}.json",
                    settings.RWGS_ROUTE_DOWNLOAD_DIR / f"course-{route_id}.json",
                ),
                (
                    f"{BASE_URL}/routes/{route_id}/hover_preview.png",
                    settings.RWGS_ROUTE_DOWNLOAD_DIR / f"preview-{route_id}.png",
                ),
            )
        else:
            urls_with_path = (
                (
                    f"{BASE_URL}/routes/{route_id}/elevation_profile.jpg",
                    settings.RWGS_ROUTE_DOWNLOAD_DIR
                    / f"elevation_profile-{route_id}.jpg",
                ),
                (
                    f"{BASE_URL}/routes/{route_id}.tcx",
                    settings.RWGS_ROUTE_DOWNLOAD_DIR / f"course-{route_id}.tcx",
                ),
            )

            privacy_code = self.get_route_privacycode(route_id)

            if privacy_code:
                params = {**self.get_params, "privacy_code": privacy_code}

        await settings.DOWNLOAD_QUEUE.put(
            {
                "urls_with_path": urls_with_path,
                "params": params,
            }
        )
        return True

    async def list_routes(self, reset=False):
        results = []
        if not detect_network() or not settings.RWGPS_TOKEN:
            return None

        if reset:
            self.current_offset = 0
            self.nb_routes = None

        # get user id
        if not self.user_id:
            response = await get_json(
                f"{BASE_URL}/users/current.json",
                params=self.get_params,
            )
            user = response.get("user")

            if user is not None:
                self.user_id = user.get("id")
            else:
                app_logger.warning(f"Could not get routes {response}")
                return

        # get count of user routes
        if self.nb_routes is None:
            response = await get_json(
                f"{BASE_URL}/users/{self.user_id}/routes.json",
                params={**self.get_params, "offset": 0, "limit": LIMIT},
            )
            self.nb_routes = response["results_count"]

        if self.nb_routes and self.current_offset < self.nb_routes:
            response = await get_json(
                f"{BASE_URL}/users/{self.user_id}/routes.json",
                params={
                    **self.get_params,
                    "offset": self.current_offset,
                    "limit": LIMIT,
                },
            )
            self.current_offset += LIMIT
            results = response.get("results")

        return results

    async def upload(self):
        file_path = settings.FILE_UPLOAD
        if not settings.RWGPS_TOKEN or not settings.RWGPS_APIKEY:
            app_logger.info("set APIKEY or TOKEN of RWGPS")
            return False
        elif not file_path:
            app_logger.info("No file to upload")
            return False

        async with aiofiles.open(file_path, "rb") as file:
            response = await post(
                f"{BASE_URL}/trips.json",
                params=self.get_params,
                data={"file": file},
            )
            if response["success"] != 1:
                return False

        return True
