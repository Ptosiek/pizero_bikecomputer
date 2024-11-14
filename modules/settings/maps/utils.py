from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

DEFAULT_TILE_SIZE = 256


@dataclass
class MapInfo:
    name: str = ""  # mandatory but it will be set automatically by the system
    mbtiles: None | Path = None
    referer: str = ""
    tile_size: int = DEFAULT_TILE_SIZE
    user_agent: bool = False
    url: str = ""

    max_zoomlevel: int | float = float("inf")
    min_zoomlevel: int | float = float("-inf")

    # time based map
    time_based: bool = False
    current_time: None | str = None
    current_time_func: Callable = datetime.now  # local?
    time_format: str = ""
    time_interval: int = 10  # [minutes]
    update_minutes: int = 1  # typically int(time_interval/2) [minutes]

    basetime: str = ""
    validtime: str = ""

    def format_current_time(self) -> str:
        if self.time_format == "unix_timestamp":
            return str(int(self.current_time.timestamp()))
        else:
            return self.current_time.strftime(self.time_format)
