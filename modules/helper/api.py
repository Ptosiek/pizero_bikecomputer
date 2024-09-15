import os

from modules.utils.network import detect_network
from logger import app_logger

from .rwgps import RWGPS


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
