from datetime import datetime
from enum import StrEnum


class RainMap(StrEnum):
    RAINVIEWER = "rainviewer"


RAIN_OVERLAY_MAP_CONFIG = {
    # worldwide rain tile
    RainMap.RAINVIEWER: {
        "url": "https://tilecache.rainviewer.com/v2/radar/{basetime}/256/{z}/{x}/{y}/6/1_1.png",
        "tile_size": 256,
        "max_zoomlevel": 18,
        "min_zoomlevel": 1,
        "time_list": "https://api.rainviewer.com/public/weather-maps.json",
        "nowtime": None,
        "nowtime_func": datetime.now,  # local?
        "basetime": None,
        "validtime": None,
        "time_interval": 10,  # [minutes]
        "update_minutes": 1,  # typically int(time_interval/2) [minutes]
        "time_format": "unix_timestamp",
    }
}
