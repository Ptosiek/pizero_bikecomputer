from datetime import datetime
from enum import StrEnum

from modules.utils.map import MapInfo


class RainMap(StrEnum):
    RAINVIEWER = "rainviewer"


RAIN_OVERLAY_MAP_CONFIG = {
    # worldwide rain tile
    RainMap.RAINVIEWER: MapInfo(
        url="https://tilecache.rainviewer.com/v2/radar/{basetime}/256/{z}/{x}/{y}/6/1_1.png",
        max_zoom_level=18,
        min_zoom_level=1,
        current_time_func=datetime.now,  # local?
        basetime=None,
        validtime=None,
        time_interval=10,  # [minutes]
        update_minutes=1,  # typically int(time_interval/2) [minutes]
        time_format="unix_timestamp",
    )
}
