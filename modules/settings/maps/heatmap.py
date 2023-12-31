from enum import StrEnum


class HeatMap(StrEnum):
    RWG = "rwg_heatmap"
    STRAVA_BLUERED = "strava_heatmap_bluered"
    STRAVA_HOT = "strava_heatmap_hot"
    STRAVA_BLUE = "strava_heatmap_blue"
    STRAVA_PURPLE = "strava_heatmap_purple"
    STRAVA_GRAY = "strava_heatmap_gray"


HEATMAP_OVERLAY_MAP_CONFIG = {
    HeatMap.RWG: {
        # start_color: low, white(FFFFFF) is recommended.
        # end_color: high, any color you like.
        "url": "https://heatmap.ridewithgps.com/normalized/{z}/{x}/{y}.png?start_color=%23FFFFFF&end_color=%23FF8800",
        "attribution": "Ride with GPS",
        "tile_size": 256,
        "max_zoomlevel": 16,
        "min_zoomlevel": 10,
    },
    # strava heatmap
    # https://wiki.openstreetmap.org/wiki/Strava
    # bluered / hot / blue / purple / gray
    HeatMap.STRAVA_BLUERED: {
        "url": "https://heatmap-external-b.strava.com/tiles-auth/ride/bluered/{z}/{x}/{y}.png?px=256&Key-Pair-Id={key_pair_id}&Policy={policy}&Signature={signature}",
        "attribution": "STRAVA",
        "tile_size": 256,
        "max_zoomlevel": 16,
        "min_zoomlevel": 10,
    },
    HeatMap.STRAVA_HOT: {
        "url": "https://heatmap-external-b.strava.com/tiles-auth/ride/hot/{z}/{x}/{y}.png?px=256&Key-Pair-Id={key_pair_id}&Policy={policy}&Signature={signature}",
        "attribution": "STRAVA",
        "tile_size": 256,
        "max_zoomlevel": 16,
        "min_zoomlevel": 10,
    },
    HeatMap.STRAVA_BLUE: {
        "url": "https://heatmap-external-b.strava.com/tiles-auth/ride/blue/{z}/{x}/{y}.png?px=256&Key-Pair-Id={key_pair_id}&Policy={policy}&Signature={signature}",
        "attribution": "STRAVA",
        "tile_size": 256,
        "max_zoomlevel": 16,
        "min_zoomlevel": 10,
    },
    HeatMap.STRAVA_PURPLE: {
        "url": "https://heatmap-external-b.strava.com/tiles-auth/ride/purple/{z}/{x}/{y}.png?px=256&Key-Pair-Id={key_pair_id}&Policy={policy}&Signature={signature}",
        "attribution": "STRAVA",
        "tile_size": 256,
        "max_zoomlevel": 16,
        "min_zoomlevel": 10,
    },
    HeatMap.STRAVA_GRAY: {
        "url": "https://heatmap-external-b.strava.com/tiles-auth/ride/gray/{z}/{x}/{y}.png?px=256&Key-Pair-Id={key_pair_id}&Policy={policy}&Signature={signature}",
        "attribution": "STRAVA",
        "tile_size": 256,
        "max_zoomlevel": 16,
        "min_zoomlevel": 10,
    },
}
