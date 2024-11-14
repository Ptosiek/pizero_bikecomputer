import sqlite3
from io import BytesIO


def connect_mbtiles(mbtiles):
    con = sqlite3.connect(f"file:{mbtiles}?mode=ro", uri=True)
    cur = con.cursor()

    return con, cur


def check_mbtiles_image(cur, x, y, z_level):
    sql = (
        f"select count(*) from tiles where "
        f"zoom_level={z_level} and tile_column={x} and tile_row={2 ** z_level - 1 - y}"
    )
    return cur.execute(sql).fetchone()[0] == 1


def get_mbtiles_image(cur, x, y, z_level):
    sql = (
        f"select tile_data from tiles where "
        f"zoom_level={z_level} and tile_column={x} and tile_row={2 ** z_level - 1 - y}"
    )
    return BytesIO((cur.execute(sql).fetchone())[0])
