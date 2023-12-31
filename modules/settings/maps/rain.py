from datetime import datetime
from enum import StrEnum


class RainMap(StrEnum):
    RAINVIEWER = "rainviewer"
    JPN_JMA_BOUSAI = "jpn_jma_bousai"


RAIN_OVERLAY_MAP_CONFIG = {
    # worldwide rain tile
    RainMap.RAINVIEWER: {
        "url": "https://tilecache.rainviewer.com/v2/radar/{basetime}/256/{z}/{x}/{y}/6/1_1.png",
        "attribution": "RainViewer",
        "tile_size": 256,
        "max_zoomlevel": 18,
        "min_zoomlevel": 1,
        "time_list": "https://api.rainviewer.com/public/weather-maps.json",
        "nowtime": None,
        "nowtime_func": datetime.now,  # local?
        "basetime": None,
        "time_interval": 10,  # [minutes]
        "update_minutes": 1,  # typically int(time_interval/2) [minutes]
        "time_format": "unix_timestamp",
    },
    # japanese rain tile
    RainMap.JPN_JMA_BOUSAI: {
        "url": "https://www.jma.go.jp/bosai/jmatile/data/nowc/{basetime}/none/{validtime}/surf/hrpns/{z}/{x}/{y}.png",
        "attribution": "Japan Meteorological Agency",
        "tile_size": 256,
        "max_zoomlevel": 10,
        "min_zoomlevel": 4,
        "past_time_list": "https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N1.json",
        "forcast_time_list": "https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N2.json",
        "nowtime": None,
        "nowtime_func": datetime.utcnow,
        "basetime": None,
        "validtime": None,
        "time_interval": 5,  # [minutes]
        "update_minutes": 1,  # [minutes]
        "time_format": "%Y%m%d%H%M%S",
    },
}
