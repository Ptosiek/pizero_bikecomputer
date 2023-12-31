from enum import StrEnum

from .utils import MapDict


class Map(StrEnum):
    TONER = "toner"
    TONER_LITE = "toner-lite"
    TONER_2X = "toner_2x"
    TONER_TERRAIN = "toner-terrain"
    WIKIMEDIA = "wikimedia"
    WIKIMEDIA_2X = "wikimedia_2x"
    JPN_KOKUDO_CHIRI_IN = "jpn_kokudo_chiri_in"


MAP_CONFIG = {
    # basic map
    Map.TONER: MapDict(
        {
            # 0:z(zoom), 1:tile_x, 2:tile_y
            "url": "https://tiles.stadiamaps.com/toner/{z}/{x}/{y}.png",
            "attribution": "Map tiles by Stamen Design, under CC BY 3.0.<br />Data by OpenStreetMap, under ODbL",
        }
    ),
    Map.TONER_LITE: MapDict(
        {
            # 0:z(zoom), 1:tile_x, 2:tile_y
            "url": "https://tiles.stadiamaps.com/toner-lite/{z}/{x}/{y}.png",
            "attribution": "Map tiles by Stamen Design, under CC BY 3.0.<br />Data by OpenStreetMap, under ODbL",
        }
    ),
    Map.TONER_2X: MapDict(
        {
            # 0:z(zoom), 1:tile_x, 2:tile_y
            "url": "https://tiles.stadiamaps.com/toner/{z}/{x}/{y}@2x.png",
            "attribution": "Map tiles by Stamen Design, under CC BY 3.0.<br />Data by OpenStreetMap, under ODbL",
            "tile_size": 512,
        }
    ),
    Map.TONER_TERRAIN: MapDict(
        {
            # 0:z(zoom), 1:tile_x, 2:tile_y
            "url": "https://tiles.stadiamaps.com/terrain/{z}/{x}/{y}.png",
            "attribution": "Map tiles by Stamen Design, under CC BY 3.0.<br />Data by OpenStreetMap, under ODbL",
        }
    ),
    Map.WIKIMEDIA: MapDict(
        {
            "url": "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
            "attribution": "© OpenStreetMap contributors",
            "referer": "https://maps.wikimedia.org/",
        }
    ),
    Map.WIKIMEDIA_2X: MapDict(
        {
            "url": "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}@2x.png",
            "attribution": "© OpenStreetMap contributors",
            "referer": "https://maps.wikimedia.org/",
            "tile_size": 512,
        }
    ),
    # japanese tile
    Map.JPN_KOKUDO_CHIRI_IN: MapDict(
        {
            "url": "https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png",
            "attribution": "国土地理院",
        }
    ),
}
