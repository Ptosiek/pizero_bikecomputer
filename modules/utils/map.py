import math
import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np

from .mbutils import check_mbtiles_image, connect_mbtiles, get_mbtiles_image
from .network import detect_network

DEFAULT_TILE_SIZE = 256


@dataclass
class MapInfo:
    name: str = ""  # mandatory but it will be set automatically by the system
    mbtiles: None | Path = None
    referer: str = ""
    root_dir: None | Path = None
    tile_size: int = DEFAULT_TILE_SIZE
    user_agent: str = ""
    url: str = ""

    max_zoom_level: int | float = float("inf")
    min_zoom_level: int | float = float("-inf")

    # time based map
    time_based: bool = False
    current_time: None | str = None
    current_time_func: Callable = datetime.now  # local?
    time_format: str = ""
    time_interval: int = 10  # [minutes]
    update_minutes: int = 1  # typically int(time_interval/2) [minutes]

    basetime: str = ""
    validtime: str = ""

    def check_mbtiles_image(self, x, y, z_level):
        return check_mbtiles_image(self.cursor, x, y, z_level)

    async def download_tiles(self, queue, z, tiles, additional_download=False):
        if not detect_network() or not self.url:
            return False

        urls_with_path = set()

        request_header = {}
        additional_var = {}

        if self.time_based:
            if not self.basetime or not self.validtime:
                return False

            additional_var["basetime"] = self.basetime
            additional_var["validtime"] = self.validtime

        if self.referer:
            request_header["Referer"] = self.referer

        if self.user_agent:
            request_header["User-Agent"] = self.user_agent

        for tile in tiles:
            url = self.url.format(z=z, x=tile[0], y=tile[1], **additional_var)
            urls_with_path.add((url, self.get_tile_filename(z, *tile)))

        await queue.put({"headers": request_header, "urls_with_path": urls_with_path})

        if additional_download:
            additional_urls_with_path = set()

            max_zoom_cond = True

            if z + 1 >= self.max_zoom_level:
                max_zoom_cond = False

            min_zoom_cond = True

            if z - 1 <= self.min_zoom_level:
                min_zoom_cond = False

            for tile in tiles:
                if max_zoom_cond:
                    for i in range(2):
                        for j in range(2):
                            url = self.url.format(
                                z=z + 1,
                                x=2 * tile[0] + i,
                                y=2 * tile[1] + j,
                                **additional_var,
                            )
                            save_path = self.get_tile_filename(
                                z + 1,
                                2 * tile[0] + i,
                                2 * tile[1] + j,
                            )
                            additional_urls_with_path.add((url, save_path))

                if z - 1 <= 0:
                    continue

                if min_zoom_cond:
                    zoom_out_url = self.url.format(
                        z=z - 1,
                        x=int(tile[0] / 2),
                        y=int(tile[1] / 2),
                        **additional_var,
                    )
                    zoom_out_path = self.get_tile_filename(
                        z - 1,
                        int(tile[0] / 2),
                        int(tile[1] / 2),
                    )
                    additional_urls_with_path.add((zoom_out_url, zoom_out_path))

            if additional_urls_with_path:
                await queue.put(
                    {
                        "headers": request_header,
                        "urls_with_path": additional_urls_with_path,
                    }
                )

        return True

    def format_current_time(self) -> str:
        if self.time_format == "unix_timestamp":
            return str(int(self.current_time.timestamp()))
        else:
            return self.current_time.strftime(self.time_format)

    def get_image_file(self, z_draw, x, y):
        if self.mbtiles:
            return get_mbtiles_image(self.cursor, x, y, z_draw)
        else:
            return self.get_tile_filename(z_draw, x, y)

    def get_tile_filename(self, z, x, y, basetime=None, validtime=None):
        path = self.root_dir / self.name

        if basetime and validtime:
            path = path / str(basetime) / str(validtime)

        path = path / str(z) / str(x) / str(y)

        return path.with_suffix(Path(self.url).suffix)

    def init_draw_map(self, z, p0, p1, expand):
        z_draw = z
        z_conv_factor = 1

        if expand:
            if z > self.max_zoom_level:
                z_draw = self.max_zoom_level
            elif z < self.min_zoom_level:
                z_draw = self.min_zoom_level
            # z_draw = min(z, map_info.max_zoom_level)
            z_conv_factor = 2 ** (z - z_draw)

        # tile range
        t0 = get_tilexy_and_xy_in_tile(z, p0["x"], p0["y"], self.tile_size)
        t1 = get_tilexy_and_xy_in_tile(z, p1["x"], p1["y"], self.tile_size)
        tile_x = sorted([t0[0], t1[0]])
        tile_y = sorted([t0[1], t1[1]])

        return z_draw, z_conv_factor, tile_x, tile_y

    def remove_tiles(self):
        path = self.root_dir / self.name

        if path.exists():
            dirs = [d for d in path.iterdir() if d.is_dir()]
            # Remove each subdirectory
            for d in dirs:
                shutil.rmtree(d)


@contextmanager
def connected_map(map_info: MapInfo):
    """
    Context manager that handles connection to .mbtiles file if map_info has one
    """
    connection = None
    cursor = None

    try:
        if map_info.mbtiles:
            connection, cursor = connect_mbtiles(map_info.mbtiles)
            map_info.connection = connection
            map_info.cursor = connection.cursor()
        yield cursor  # Yield the cursor or None if no connection is made
    except Exception as e:
        raise e
    finally:
        if connection:
            map_info.cursor.close()
            map_info.connection.close()
            del map_info.cursor
            del map_info.connection


def get_geo_area(x, y, zoom_level, tile_size: int) -> np.array:
    if np.isnan(x) or np.isnan(y):
        return np.nan, np.nan

    tile_x, tile_y, _, _ = get_tilexy_and_xy_in_tile(
        zoom_level,
        x,
        y,
        tile_size,
    )
    pos_x0, pos_y0 = get_lon_lat_from_tile_xy(zoom_level, tile_x, tile_y)
    pos_x1, pos_y1 = get_lon_lat_from_tile_xy(zoom_level, tile_x + 1, tile_y + 1)

    return np.array(
        (abs(pos_x1 - pos_x0) / tile_size, abs(pos_y1 - pos_y0) / tile_size)
    )


def get_lon_lat_from_tile_xy(z, x, y):
    n = 2.0**z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))

    return lon, lat


def get_tilexy_and_xy_in_tile(z, x, y, tile_size):
    n = 2.0**z
    _y = math.radians(y)
    x_in_tile, tile_x = math.modf((x + 180.0) / 360.0 * n)
    y_in_tile, tile_y = math.modf(
        (1.0 - math.log(math.tan(_y) + (1.0 / math.cos(_y))) / math.pi) / 2.0 * n
    )

    return (
        int(tile_x),
        int(tile_y),
        int(x_in_tile * tile_size),
        int(y_in_tile * tile_size),
    )
