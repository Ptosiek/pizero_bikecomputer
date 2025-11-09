from pizero_bikecomputer.logger import app_logger

from .gpsd import _SENSOR_GPS_GPSD, GPSD

if _SENSOR_GPS_GPSD:
    SensorGPS = GPSD
else:
    # we always have a non-null GPS sensor, but it won't generate data unless told to do so with DUMMY_OUTPUT
    from .dummy import Dummy_GPS

    SensorGPS = Dummy_GPS

app_logger.info(f"GPS {SensorGPS.__name__}")
