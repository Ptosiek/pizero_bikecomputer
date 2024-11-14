from enum import StrEnum

from .utils import MapInfo


class Map(StrEnum):
    WIKIMEDIA = "wikimedia"
    WIKIMEDIA_2X = "wikimedia_2x"


MAP_CONFIG = {
    # basic map
    Map.WIKIMEDIA: MapInfo(
        name=Map.WIKIMEDIA.value,
        url="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
        referer="https://maps.wikimedia.org/",
    ),
    Map.WIKIMEDIA_2X: MapInfo(
        name=Map.WIKIMEDIA_2X.value,
        url="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}@2x.png",
        referer="https://maps.wikimedia.org/",
        tile_size=512,
    ),
}
