from dataclasses import dataclass

from pizero_bikecomputer.modules.utils.formatter import ValueFormatter


@dataclass
class BaseItemConfig:
    name: str  # name of widget to use in layout file
    label: str  # label on screen
    value: str  # string to eval to get value

    formatter: ValueFormatter = ValueFormatter
