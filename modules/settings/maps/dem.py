# DEM(Digital Elevation Model) maps
from enum import StrEnum


class DemMap(StrEnum):
    JPN_KOKUDO_CHIRI_IN_DEM5A = "jpn_kokudo_chiri_in_DEM5A"
    JPN_KOKUDO_CHIRI_IN_DEM5B = "jpn_kokudo_chiri_in_DEM5B"
    JPN_KOKUDO_CHIRI_IN_DEM5C = "jpn_kokudo_chiri_in_DEM5C"
    JPN_KOKUDO_CHIRI_IN_DEM10B = "jpn_kokudo_chiri_in_DEM10B"


DEM_MAP_CONFIG = {
    DemMap.JPN_KOKUDO_CHIRI_IN_DEM5A: {
        "url": "https://cyberjapandata.gsi.go.jp/xyz/dem5a_png/{z}/{x}/{y}.png",
        "attribution": "国土地理院",
        "fix_zoomlevel": 15,
    },
    DemMap.JPN_KOKUDO_CHIRI_IN_DEM5B: {
        "url": "https://cyberjapandata.gsi.go.jp/xyz/dem5b_png/{z}/{x}/{y}.png",
        "attribution": "国土地理院",
        "fix_zoomlevel": 15,
    },
    DemMap.JPN_KOKUDO_CHIRI_IN_DEM5C: {
        "url": "https://cyberjapandata.gsi.go.jp/xyz/dem5c_png/{z}/{x}/{y}.png",
        "attribution": "国土地理院",
        "fix_zoomlevel": 15,
    },
    DemMap.JPN_KOKUDO_CHIRI_IN_DEM10B: {
        "url": "https://cyberjapandata.gsi.go.jp/xyz/dem_png/{z}/{x}/{y}.png",
        "attribution": "国土地理院",
        "fix_zoomlevel": 14,
    },
}
