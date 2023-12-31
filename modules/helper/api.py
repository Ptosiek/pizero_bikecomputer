import asyncio
import os
import traceback
import time

import aiofiles

from modules.utils.network import detect_network, post
from logger import app_logger

from .rwgps import RWGPS

_IMPORT_GARMINCONNECT = False
try:
    from garminconnect import (
        Garmin,
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )

    _IMPORT_GARMINCONNECT = True
except ImportError:
    pass

_IMPORT_STRAVA_COOKIE = False
try:
    from stravacookies import StravaCookieFetcher

    _IMPORT_STRAVA_COOKIE = True
except ImportError:
    pass


class Api:
    config = None
    rwgps = None

    def __init__(self, config):
        self.config = config
        self.rwgps = RWGPS()

    def upload_check(self, blank_check, blank_msg, file_check=True):
        # network check
        if not detect_network():
            app_logger.warning("No Internet connection")
            return False

        # blank check
        for b in blank_check:
            if b == "":
                app_logger.info(blank_msg)
                return False

        # file check
        if file_check and not os.path.exists(self.config.G_UPLOAD_FILE):
            app_logger.warning("file does not exist")
            return False

        return True

    def get_strava_cookie(self):
        blank_check = [
            self.config.G_STRAVA_COOKIE["EMAIL"],
            self.config.G_STRAVA_COOKIE["PASSWORD"],
        ]
        blank_msg = "set EMAIL or PASSWORD of STRAVA"
        if not self.upload_check(blank_check, blank_msg, file_check=False):
            return False

        # import check
        if not _IMPORT_STRAVA_COOKIE:
            app_logger.warning("Install stravacookies")
            return

        if not detect_network():
            return None

        strava_cookie = StravaCookieFetcher()
        try:
            strava_cookie.fetchCookies(
                self.config.G_STRAVA_COOKIE["EMAIL"],
                self.config.G_STRAVA_COOKIE["PASSWORD"],
            )
            self.config.G_STRAVA_COOKIE["KEY_PAIR_ID"] = strava_cookie.keyPairId
            self.config.G_STRAVA_COOKIE["POLICY"] = strava_cookie.policy
            self.config.G_STRAVA_COOKIE["SIGNATURE"] = strava_cookie.signature
        except:
            traceback.print_exc()

    async def strava_upload(self):
        blank_check = [
            self.config.G_STRAVA_API["CLIENT_ID"],
            self.config.G_STRAVA_API["CLIENT_SECRET"],
            self.config.G_STRAVA_API["CODE"],
            self.config.G_STRAVA_API["ACCESS_TOKEN"],
            self.config.G_STRAVA_API["REFRESH_TOKEN"],
        ]
        blank_msg = "set STRAVA settings (token, client_id, etc)"
        if not self.upload_check(blank_check, blank_msg):
            return False

        # refresh access token
        data = {
            "client_id": self.config.G_STRAVA_API["CLIENT_ID"],
            "client_secret": self.config.G_STRAVA_API["CLIENT_SECRET"],
            "code": self.config.G_STRAVA_API["CODE"],
            "grant_type": "refresh_token",
            "refresh_token": self.config.G_STRAVA_API["REFRESH_TOKEN"],
        }
        tokens = await post(self.config.G_STRAVA_API_URL["OAUTH"], data=data)

        if (
            "access_token" in tokens
            and "refresh_token" in tokens
            and tokens["access_token"] != self.config.G_STRAVA_API["ACCESS_TOKEN"]
        ):
            # print("update strava tokens")
            self.config.G_STRAVA_API["ACCESS_TOKEN"] = tokens["access_token"]
            self.config.G_STRAVA_API["REFRESH_TOKEN"] = tokens["refresh_token"]
        elif "message" in tokens and tokens["message"].find("Error") > 0:
            app_logger.error("error occurs at refreshing tokens")
            return False

        # upload activity
        headers = {
            "Authorization": "Bearer " + self.config.G_STRAVA_API["ACCESS_TOKEN"]
        }
        data = {"data_type": "fit"}
        async with aiofiles.open(self.config.G_UPLOAD_FILE, "rb"):
            data["file"] = open(self.config.G_UPLOAD_FILE, "rb")
            upload_result = await post(
                self.config.G_STRAVA_API_URL["UPLOAD"], headers=headers, data=data
            )
            if "status" in upload_result:
                app_logger.info(upload_result["status"])

        return True

    def garmin_upload_internal(self):
        blank_check = [
            self.config.G_GARMINCONNECT_API["EMAIL"],
            self.config.G_GARMINCONNECT_API["PASSWORD"],
        ]
        blank_msg = "set EMAIL or PASSWORD of Garmin Connect"
        if not self.upload_check(blank_check, blank_msg):
            return False

        # import check
        if not _IMPORT_GARMINCONNECT:
            app_logger.warning("Install garminconnect")
            return False

        try:
            saved_session = self.config.state.get_value("garmin_session", None)
            garmin_api = Garmin(session_data=saved_session)
            garmin_api.login()
        except (FileNotFoundError, GarminConnectAuthenticationError):
            try:
                garmin_api = Garmin(
                    self.config.G_GARMINCONNECT_API["EMAIL"],
                    self.config.G_GARMINCONNECT_API["PASSWORD"],
                )
                garmin_api.login()
                self.config.state.set_value(
                    "garmin_session", garmin_api.session_data, force_apply=True
                )
            except (
                GarminConnectConnectionError,
                GarminConnectAuthenticationError,
                GarminConnectTooManyRequestsError,
            ) as err:
                app_logger.error(err)
                return False
            else:
                traceback.print_exc()
                return False

        end_status = False

        for i in range(3):
            try:
                garmin_api.upload_activity(self.config.G_UPLOAD_FILE)
                end_status = True
                break
            except (
                GarminConnectConnectionError,
                GarminConnectAuthenticationError,
                GarminConnectTooManyRequestsError,
            ) as err:
                app_logger.error(err)
            else:
                traceback.print_exc()
            time.sleep(1.0)

        return end_status

    async def garmin_upload(self):
        return await asyncio.get_running_loop().run_in_executor(
            None, self.garmin_upload_internal
        )
