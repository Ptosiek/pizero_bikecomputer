from enum import StrEnum

from .utils import MapInfo


class HeatMap(StrEnum):
    RWG = "rwg_heatmap"


HEATMAP_OVERLAY_MAP_CONFIG = {
    HeatMap.RWG: MapInfo(
        # start_color: low, white(FFFFFF) is recommended.
        # end_color: high, any color you like.
        name=HeatMap.RWG.value,
        url="https://heatmap.ridewithgps.com/normalized/{z}/{x}/{y}.png?start_color=%23FFFFFF&end_color=%23FF8800",
        max_zoomlevel=16,
        min_zoomlevel=10,
    )
}
