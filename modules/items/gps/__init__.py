from modules.utils.formatter import (
    Altitude,
    Distance,
    GPS_dop,
    GPS_error,
    GPS_fix,
    Position,
    Speed,
    ValueFormatter,
)

from ..base import BaseItemConfig


class GPS_LatitudeItemConfig(BaseItemConfig):
    name = "GPS Latitude"
    label = "Latitude"
    formatter = Position
    value = "self.sensor.values['GPS']['lat']"


class GPS_LongitudeItemConfig(BaseItemConfig):
    name = "GPS Longitude"
    label = "Longitude"
    formatter = Position
    value = "self.sensor.values['GPS']['lon']"


class GPS_AltitudeItemConfig(BaseItemConfig):
    name = "GPS Altitude"
    label = "Alt.(GPS)"
    formatter = Altitude
    value = "self.sensor.values['GPS']['alt']"


class GPS_SpeedItemConfig(BaseItemConfig):
    name = "GPS Speed"
    label = "Speed(GPS)"
    formatter = Speed
    value = "self.sensor.values['GPS']['speed']"


class GPS_DistanceItemConfig(BaseItemConfig):
    name = "GPS Distance"
    label = "Dist.(GPS)"
    formatter = Distance
    value = "self.sensor.values['GPS']['distance']"


class GPS_HeadingItemConfig(BaseItemConfig):
    name = "GPS Heading"
    label = "Heading(GPS)"
    formatter = ValueFormatter
    value = "self.sensor.values['GPS']['track_str']"


class GPS_SatellitesItemConfig(BaseItemConfig):
    name = "GPS Satellites"
    label = "Satellites"
    formatter = ValueFormatter
    value = "self.sensor.values['GPS']['used_sats_str']"


class GPS_ErrorXItemConfig(BaseItemConfig):
    name = "GPS Error X"
    label = "Error(x)"
    formatter = GPS_error
    value = "self.sensor.values['GPS']['epx']"


class GPS_ErrorYItemConfig(BaseItemConfig):
    name = "GPS Error Y"
    label = "Error(y)"
    formatter = GPS_error
    value = "self.sensor.values['GPS']['epy']"


class GPS_ErrorAltItemConfig(BaseItemConfig):
    name = "GPS Error Alt"
    label = "Error(alt)"
    formatter = GPS_error
    value = "self.sensor.values['GPS']['epv']"


class GPS_PDOPItemConfig(BaseItemConfig):
    name = "GPS PDOP"
    label = "PDOP"
    formatter = GPS_dop
    value = "self.sensor.values['GPS']['pdop']"


class GPS_HDOPItemConfig(BaseItemConfig):
    name = "GPS HDOP"
    label = "HDOP"
    formatter = GPS_dop
    value = "self.sensor.values['GPS']['hdop']"


class GPS_VDOPItemConfig(BaseItemConfig):
    name = "GPS VDOP"
    label = "VDOP"
    formatter = GPS_dop
    value = "self.sensor.values['GPS']['vdop']"


class GPS_TimeItemConfig(BaseItemConfig):
    name = "GPS Time"
    label = "GPSTime"
    formatter = ValueFormatter
    value = "self.sensor.values['GPS']['utctime']"


class GPS_FixItemConfig(BaseItemConfig):
    name = "GPS Fix"
    label = "GPS Fix"
    formatter = GPS_fix
    value = "self.sensor.values['GPS']['mode']"


class GPS_CourseDistanceItemConfig(BaseItemConfig):
    name = "GPS Course Distance"
    label = "Course Dist."
    formatter = Distance
    value = "self.sensor.values['GPS']['course_distance']"
