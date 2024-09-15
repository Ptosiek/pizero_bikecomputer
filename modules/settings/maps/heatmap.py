from enum import StrEnum


class HeatMap(StrEnum):
    RWG = "rwg_heatmap"


HEATMAP_OVERLAY_MAP_CONFIG = {
    HeatMap.RWG: {
        # start_color: low, white(FFFFFF) is recommended.
        # end_color: high, any color you like.
        "url": "https://heatmap.ridewithgps.com/normalized/{z}/{x}/{y}.png?start_color=%23FFFFFF&end_color=%23FF8800",
        "attribution": "Ride with GPS",
        "tile_size": 256,
        "max_zoomlevel": 16,
        "min_zoomlevel": 10,
    }
}
