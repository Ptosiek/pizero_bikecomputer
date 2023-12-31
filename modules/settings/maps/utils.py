from collections import UserDict

DEFAULT_TILE_SIZE = 256


class MapDict(UserDict):
    def __missing__(self, key):
        if key == "tile_size":
            return DEFAULT_TILE_SIZE
        else:
            raise KeyError(key)
