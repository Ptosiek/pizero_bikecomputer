from datetime import datetime
from enum import StrEnum


class WindMap(StrEnum):
    OPEN_PORT_GUIDE = "openportguide"


WIND_OVERLAY_MAP_CONFIG = {
    # worldwide wind tile
    # https://weather.openportguide.de/index.php/en/weather-forecasts/weather-tiles
    WindMap.OPEN_PORT_GUIDE: {
        "url": "https://weather.openportguide.de/tiles/actual/wind_stream/0h/{z}/{x}/{y}.png",
        "attribution": "openportguide",
        "tile_size": 256,
        "max_zoomlevel": 7,
        "min_zoomlevel": 0,
        "nowtime": None,
        "nowtime_func": datetime.utcnow,
        "basetime": None,
        "validtime": None,
        "time_interval": 60,  # [minutes]
        "update_minutes": 30,  # [minutes]
        "time_format": "%H%MZ%d%b%Y",
    },
}
