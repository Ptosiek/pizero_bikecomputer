from datetime import datetime
from enum import StrEnum


class WindMap(StrEnum):
    OPEN_PORT_GUIDE = "openportguide"
    JPN_SCW = "jpn_scw"


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
    # japanese wind tile
    WindMap.JPN_SCW: {
        "url": "https://{subdomain}.supercweather.com/tl/msm/{basetime}/{validtime}/wa/{z}/{x}/{y}.png",
        "attribution": "SCW",
        "tile_size": 256,
        "max_zoomlevel": 8,
        "min_zoomlevel": 8,
        "inittime": "https://k2.supercweather.com/tl/msm/initime.json?rand={rand}",
        "fl": "https://k2.supercweather.com/tl/msm/{basetime}/fl.json?rand={rand}",
        "nowtime": None,
        "nowtime_func": datetime.utcnow,
        "timeline": None,
        "basetime": None,
        "validtime": None,
        "subdomain": None,
        "time_interval": 60,  # [minutes]
        "update_minutes": 30,  # [minutes]
        "time_format": "%H%MZ%d%b%Y",  # need upper()
        "referer": "https://supercweather.com/",
    },
}
