import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

from logging.handlers import RotatingFileHandler


class StreamToLogger:
    logger = None
    level = None

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass


class CustomRotatingFileHandler(RotatingFileHandler):
    def doRollover(self):
        datetime_format = "%Y-%m-%d_%H-%M-%S"

        if self.stream:
            self.stream.close()
            self.stream = None
            # remove file older than one month (30 days)
            base_path = Path(self.baseFilename)

            regex = rf"{base_path.stem}-(.*?){base_path.suffix}"
            cut_out_date = datetime.now() - timedelta(days=30)

            for file in base_path.parent.rglob(
                "*"
            ):  # Use `rglob` for recursive search or `glob` for current dir only
                if file.is_file():
                    match = re.match(
                        regex, file.name
                    )  # Use file.name for matching the filename
                    if match:
                        try:
                            date = datetime.strptime(match.group(1), datetime_format)
                            if date < cut_out_date:
                                file.unlink()  # Delete the file
                        except Exception:
                            # If parsing fails, ignore and move on
                            pass

            # we can't get the creation date of the file easily, so use the mt_time
            # e.g. last log time of the file instead
            last_date = datetime.fromtimestamp(base_path.stat().st_mtime).strftime(
                datetime_format
            )

            self.rotate(
                self.baseFilename,
                base_path.with_name(f"{base_path.stem}-{last_date}{base_path.suffix}"),
            )
        if not self.delay:
            self.stream = self._open()

    # never do a rollover "live"
    def shouldRollover(self, record):
        return False


app_logger = logging.getLogger("bike_computer")

# change level in regard to config G_DEBUG
app_logger.setLevel(level=logging.INFO)

# Add simple stream handler
sh = logging.StreamHandler()

app_logger.addHandler(sh)

sys.stdout = StreamToLogger(app_logger, logging.INFO)
sys.stderr = StreamToLogger(app_logger, logging.ERROR)
