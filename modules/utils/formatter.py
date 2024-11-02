import numpy as np
import time
from dataclasses import dataclass


@dataclass
class ValueFormatter:
    unit: str = ""
    value_format: str = ""

    @classmethod
    def get_value(cls, value):
        # isnan does not support string input so make sure we don't have a string already
        if isinstance(value, str):
            return value
        if value is None or np.isnan(value):
            return None
        return value

    @classmethod
    def format_text(cls, value):
        value = cls.get_value(value)
        if value is None:
            return "-"
        else:
            if cls.value_format:
                return f"{value:{cls.value_format}}"
            return str(value)


class Altitude(ValueFormatter):
    value_format = ".0f"
    unit = "m"


class Cadence(ValueFormatter):
    value_format = ".0f"
    unit = "rpm"


class Distance(ValueFormatter):
    value_format = ".1f"
    unit = "km"

    @classmethod
    def get_value(cls, value):
        value = super().get_value(value)
        if value is not None:
            return value / 1000
        return value


class GPS_dop(ValueFormatter):
    value_format = ".1f"


class GPS_error(ValueFormatter):
    value_format = ".0f"
    unit = "m"


class GPS_fix(ValueFormatter):
    value_format = "d"


class HeartRate(ValueFormatter):
    value_format = ".0f"
    unit = "bpm"


class Percent(ValueFormatter):
    value_format = ".0f"
    unit = "%"


class Position(ValueFormatter):
    value_format = ".5f"


class Power(ValueFormatter):
    value_format = ".0f"
    unit = "W"


class Pressure(ValueFormatter):
    value_format = "4.0f"
    unit = "hPa"


class Speed(ValueFormatter):
    value_format = ".1f"
    unit = "km/h"

    @classmethod
    def get_value(cls, value):
        value = super().get_value(value)
        if value is not None:
            return value * 3.6
        return value


class Temperature(ValueFormatter):
    value_format = "3.0f"
    unit = "C"


class Time(ValueFormatter):
    @classmethod
    def format_text(cls, value):
        value = cls.get_value(value)
        if value is None:
            return "-"
        else:
            return time.strftime("%H:%M")


class Timer(ValueFormatter):
    @classmethod
    def format_text(cls, value):
        value = cls.get_value(value)
        if value is None:
            return "-"
        else:
            fmt = "%M:%S" if value < 3600 else "%H:%M"
            return time.strftime(fmt, time.gmtime(value))


class Work(ValueFormatter):
    value_format = ".0f"
    unit = "kJ"

    @classmethod
    def get_value(cls, value):
        value = super().get_value(value)
        if value is not None:
            return value / 1000
        return value
