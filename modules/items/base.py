from dataclasses import dataclass

from modules.utils.formatter import ValueFormatter


@dataclass
class BaseItemConfig:
    name: str  # name of widget to use in layout file
    label: str  # label on screen
    formatter: ValueFormatter
    value: str  # string to eval to get value
