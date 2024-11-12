from enum import StrEnum


class MenuLabel(StrEnum):
    ADJUST_ALTITUDE = "Adjust Altitude"
    ANT_DETAIL = "ANT+ Detail"
    ANT_SENSORS = "ANT+ Sensors"
    BLUETOOTH = "Bluetooth"
    BT_AUTO_TETHERING = "BT Auto Tethering"
    BT_TETHERING_DEVICE = "BT Tethering"
    CANCEL_COURSE = "Cancel Course"
    CONNECTIVITY = "Connectivity"
    COURSE_DETAIL = "Course Detail"
    COURSES_LIST = "Courses List"
    COURSES = "Courses"
    CP = "CP"
    DEBUG = "Debug"
    DEBUG_LEVEL_LOG = "Debug Level Log"
    DEBUG_LOG = "Debug Log"
    GADGETBRIDGE = "Gadgetbridge"
    GET_LOCATION = "Get Location"
    HEATMAP = "Heatmap"
    HEATMAP_LIST = "Heatmap List"
    IP_ADDRESS = "IP Address"
    LOCAL_STORAGE = "Local Storage"
    MAP = "Map"
    MAP_OVERLAY = "Map Overlay"
    MENU = "Menu"
    NETWORK = "Network"
    POWER_OFF = "Power Off"
    PROFILE = "Profile"
    RAIN_MAP = "Rain map"
    RAIN_MAP_LIST = "Rain map List"
    RIDE_WITH_GPS = "Ride with GPS"
    REBOOT = "Reboot"
    RESTART = "Restart"
    SELECT_MAP = "Select Map"
    SENSORS = "Sensors"
    SYSTEM = "System"
    UPDATE = "Update"
    UPLOAD_ACTIVITY = "Upload Activity"
    W_PRIME_BALANCE = "W Prime Balance"
    WHEEL_SIZE = "Wheel Size"
    WIFI = "Wifi"
    WIND_MAP = "Wind map"
    WIND_MAP_LIST = "Wind map List"


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
