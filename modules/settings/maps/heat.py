from enum import StrEnum

from modules.utils.map import MapInfo


class HeatMap(StrEnum):
    RWG = "rwg_heatmap"


HEAT_OVERLAY_MAP_CONFIG = {
    HeatMap.RWG: MapInfo(
        # start_color: low, white(FFFFFF) is recommended.
        # end_color: high, any color you like.
        url="https://heatmap.ridewithgps.com/normalized/{z}/{x}/{y}.png?start_color=%23FFFFFF&end_color=%23FF8800",
        max_zoom_level=16,
        min_zoom_level=10,
    )
}
