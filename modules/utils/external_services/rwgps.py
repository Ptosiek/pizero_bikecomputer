import json
from pathlib import Path
from typing import Sequence

import aiofiles

from logger import app_logger
from modules.utils.network import detect_network, download_files, get_json, post


BASE_URL = "https://ridewithgps.com"
LIMIT = 10


class RWGPS:
    current_offset = 0
    nb_routes = float("inf")
    user_id = None

    def __init__(self, folder_root: Path, api_key: str, auth_token: str):
        self.folder_root = folder_root
        self.api_key = api_key
        self.auth_token = auth_token

    def course_json_path(self, route_id):
        return self.folder_root / f"course-{route_id}.json"

    def preview_path(self, route_id):
        return self.folder_root / f"preview-{route_id}.png"

    def elevation_profile_path(self, route_id):
        return self.folder_root / f"elevation-profile-{route_id}.jpg"

    def course_path(self, route_id):
        return self.folder_root / f"course-{route_id}.tcx"

    @property
    def get_params(self):
        return {"apikey": self.api_key, "version": "2", "auth_token": self.auth_token}

    def check_files(self, route_id):
        save_paths = [
            self.course_json_path(route_id),
            self.preview_path(route_id),
            self.elevation_profile_path(route_id),
            self.course_path(route_id),
        ]

        for filename in save_paths:
            if not filename.exists() or not filename.stat().st_size:
                return False

        return save_paths

    def get_route_privacy_code(self, route_id):
        filename = self.course_json_path(route_id)

        with filename.open() as json_file:
            json_contents = json.load(json_file)

            return json_contents["route"].get("privacy_code", None)

    async def get_route_files(self, route_id) -> Sequence[str] | None:
        course_json_path = self.course_json_path(route_id)
        preview_path = self.preview_path(route_id)

        urls_with_path = (
            (f"{BASE_URL}/routes/{route_id}.json", course_json_path),
            (f"{BASE_URL}/routes/{route_id}/hover_preview.png", preview_path),
        )

        result = all(await download_files(urls_with_path, params=self.get_params))

        return (course_json_path, preview_path) if result else (None, None)

    async def get_private_route_files(self, route_id) -> Sequence[str] | None:
        params = self.get_params

        elevation_path = self.elevation_profile_path(route_id)
        course_path = self.course_path(route_id)

        urls_with_path = (
            (
                f"{BASE_URL}/routes/{route_id}/elevation_profile.jpg",
                elevation_path,
            ),
            (
                f"{BASE_URL}/routes/{route_id}.tcx",
                course_path,
            ),
        )

        privacy_code = self.get_route_privacy_code(route_id)

        if privacy_code:
            params = {**self.get_params, "privacy_code": privacy_code}

        result = all(await download_files(urls_with_path, params=params))

        return (elevation_path, course_path) if result else (None, None)

    async def list_routes(self, reset=False):
        results = []
        if not detect_network() or not self.auth_token:
            return None

        if reset:
            self.current_offset = 0
            self.nb_routes = float("inf")

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

        if self.current_offset < self.nb_routes:
            response = await get_json(
                f"{BASE_URL}/users/{self.user_id}/routes.json",
                params={
                    **self.get_params,
                    "offset": self.current_offset,
                    "limit": LIMIT,
                },
            )
            self.nb_routes = response["results_count"]
            self.current_offset += LIMIT
            results = response.get("results")

        return results

    async def upload(self, file_path: Path):
        if not self.api_key or not self.auth_token:
            app_logger.info("set APIKEY or TOKEN of RWGPS")
            return False
        elif not file_path.exists():
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
