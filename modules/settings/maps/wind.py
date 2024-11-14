from datetime import datetime
from enum import StrEnum

from .utils import MapInfo


class WindMap(StrEnum):
    OPEN_PORT_GUIDE = "openportguide"


WIND_OVERLAY_MAP_CONFIG = {
    # worldwide wind tile
    # https://weather.openportguide.de/index.php/en/weather-forecasts/weather-tiles
    WindMap.OPEN_PORT_GUIDE: MapInfo(
        name=WindMap.OPEN_PORT_GUIDE.value,
        url="https://weather.openportguide.de/tiles/actual/wind_stream/0h/{z}/{x}/{y}.png",
        tile_size=256,
        max_zoomlevel=7,
        min_zoomlevel=0,
        current_time_func=datetime.utcnow,
        basetime=None,
        validtime=None,
        time_interval=60,  # [minutes]
        update_minutes=30,  # [minutes]
        time_format="%H%MZ%d%b%Y",
    ),
}
