import inspect

from . import ant
from . import general
from . import gps
from . import i2c

from .base import BaseItemConfig


def check(c):
    return inspect.isclass(c) and issubclass(c, BaseItemConfig) and hasattr(c, "name")


ITEM_CONFIG = {
    **{c.name: c for _, c in inspect.getmembers(ant) if check(c)},
    **{c.name: c for _, c in inspect.getmembers(general) if check(c)},
    **{c.name: c for _, c in inspect.getmembers(gps) if check(c)},
    **{c.name: c for _, c in inspect.getmembers(i2c) if check(c)},
}
