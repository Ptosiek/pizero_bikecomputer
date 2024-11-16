from enum import StrEnum

from modules.utils.map import MapInfo


class Map(StrEnum):
    WIKIMEDIA = "wikimedia"
    WIKIMEDIA_2X = "wikimedia_2x"


MAP_CONFIG = {
    # basic map
    Map.WIKIMEDIA: MapInfo(
        url="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
        referer="https://maps.wikimedia.org/",
        max_zoom_level=19,
    ),
    Map.WIKIMEDIA_2X: MapInfo(
        url="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}@2x.png",
        referer="https://maps.wikimedia.org/",
        max_zoom_level=19,
        tile_size=512,
    ),
}
