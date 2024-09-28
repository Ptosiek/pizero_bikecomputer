from enum import StrEnum

from .utils import MapDict


class Map(StrEnum):
    TONER = "toner"
    TONER_LITE = "toner-lite"
    TONER_2X = "toner_2x"
    TONER_TERRAIN = "toner-terrain"
    WIKIMEDIA = "wikimedia"
    WIKIMEDIA_2X = "wikimedia_2x"


MAP_CONFIG = {
    # basic map
    Map.TONER: MapDict(
        {
            # 0:z(zoom), 1:tile_x, 2:tile_y
            "url": "https://tiles.stadiamaps.com/toner/{z}/{x}/{y}.png",
        }
    ),
    Map.TONER_LITE: MapDict(
        {
            # 0:z(zoom), 1:tile_x, 2:tile_y
            "url": "https://tiles.stadiamaps.com/toner-lite/{z}/{x}/{y}.png",
        }
    ),
    Map.TONER_2X: MapDict(
        {
            # 0:z(zoom), 1:tile_x, 2:tile_y
            "url": "https://tiles.stadiamaps.com/toner/{z}/{x}/{y}@2x.png",
            "tile_size": 512,
        }
    ),
    Map.TONER_TERRAIN: MapDict(
        {
            # 0:z(zoom), 1:tile_x, 2:tile_y
            "url": "https://tiles.stadiamaps.com/terrain/{z}/{x}/{y}.png",
        }
    ),
    Map.WIKIMEDIA: MapDict(
        {
            "url": "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
            "referer": "https://maps.wikimedia.org/",
        }
    ),
    Map.WIKIMEDIA_2X: MapDict(
        {
            "url": "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}@2x.png",
            "referer": "https://maps.wikimedia.org/",
            "tile_size": 512,
        }
    ),
}
