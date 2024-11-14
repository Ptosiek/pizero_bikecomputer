import math
import shutil
from contextlib import contextmanager

from modules.settings import settings
from .mbutils import connect_mbtiles


@contextmanager
def with_map(map_info):
    # Initialize the connection only if the flag is True
    connection = None
    cursor = None
    try:
        if map_info.mbtiles:
            connection, cursor = connect_mbtiles(map_info.mbtiles)
            map_info.connection = connection
            map_info.cursor = connection.cursor()
        yield cursor  # Yield the cursor or None if no connection is made
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if connection:
            map_info.cursor.close()
            map_info.connection.close()
            del map_info.cursor
            del map_info.connection


def check_map_dir():
    for p in (
        settings.HEATMAP_OVERLAY_MAP,
        settings.RAIN_OVERLAY_MAP,
        settings.WIND_OVERLAY_MAP,
    ):
        (settings.MAPTILE_DIR / p).mkdir(parents=True, exist_ok=True)

    if not settings.CURRENT_MAP.mbtiles:
        (settings.MAPTILE_DIR / settings.MAP).mkdir(parents=True, exist_ok=True)


def get_maptile_filename(map_name, z, x, y, basetime=None, validtime=None):
    p = settings.MAPTILE_DIR / map_name

    if basetime and validtime:
        p = p / str(basetime) / str(validtime)

    p = p / str(z) / str(x) / str(y)

    return p.with_suffix(".png")


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


def remove_maptiles(map_name):
    path = settings.MAPTILE_DIR / map_name

    if path.exists():
        dirs = [d for d in path.iterdir() if d.is_dir()]
        # Remove each subdirectory
        for d in dirs:
            shutil.rmtree(d)
