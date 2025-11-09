from enum import StrEnum


class OverlayMap(StrEnum):
    HEAT_MAP = "Heat map"
    RAIN_MAP = "Rain map"
    WIND_MAP = "Wind map"


class MenuLabel(StrEnum):
    ADJUST_ALTITUDE = "Adjust altitude"
    ANT_DETAIL = "ANT+ Detail"
    ANT_SENSORS = "ANT+ sensors"
    BLUETOOTH = "Bluetooth"
    BT_TETHERING_DEVICE = "BT tethering"
    CANCEL_COURSE = "Cancel course"
    CONNECTIVITY = "Connectivity"
    COURSE_DETAIL = "Course detail"
    COURSES_LIST = "Courses list"
    COURSES = "Courses"
    CP = "CP"
    DEBUG = "Debug"
    GADGETBRIDGE = "Gadgetbridge"
    GET_LOCATION = "Get location"
    HEAT_MAP = "Heat map"
    LOCAL_STORAGE = "Local storage"
    LOGS = "Logs"
    MAP = "Map"
    MENU = "Menu"
    POWER_OFF = "Power off"
    PROFILE = "Profile"
    RAIN_MAP = "Rain map"
    RIDE_WITH_GPS = "Ride with GPS"
    REBOOT = "Reboot"
    RESTART = "Restart"
    SELECT_MAP = "Select map"
    SENSORS = "Sensors"
    SYSTEM = "System"
    UPDATE = "Update"
    UPLOAD_ACTIVITY = "Upload activity"
    W_PRIME_BALANCE = "W Prime Balance"
    WHEEL_SIZE = "Wheel Size"
    WIFI = "Wifi"
    WIND_MAP = "Wind map"


# these are 'individual' ant devices as supported by the system
class ANTDevice(StrEnum):
    CADENCE = "CADENCE"
    CONTROL = "CONTROL"
    HEART_RATE = "HEART_RATE"
    LIGHT = "LIGHT"
    POWER = "POWER"
    SPEED = "SPEED"
    TEMPERATURE = "TEMPERATURE"

    @classmethod
    def keys(cls):
        return list(map(lambda c: c.value, cls))
