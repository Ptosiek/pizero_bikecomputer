import asyncio
import os
from datetime import datetime, timezone

from logger import app_logger
from modules.settings import settings
from .base import AbstractSensorGPS

_SENSOR_GPS_GPSD = False
try:
    from gps3 import agps3threaded
    from gps3.misc import satellites_used

    # device test
    _gps3_thread = agps3threaded.AGPS3mechanism()
    _SENSOR_GPS_GPSD = True
except ImportError:
    pass
except Exception:  # noqa
    app_logger.exception("Failed to init GPS_GPSD")
    try:
        _gps3_thread.stop()
    except:
        pass


class GPSD(AbstractSensorGPS):
    gps_thread = None

    valid_cutoff_ep = None

    def sensor_init(self):
        self.gps_thread = _gps3_thread
        self.gps_thread.stream_data(
            host=os.environ.get("GPSD_HOST", agps3threaded.HOST),
            port=os.environ.get("GPSD_PORT", agps3threaded.GPSD_PORT),
        )
        self.gps_thread.run_thread()
        super().sensor_init()

        self.valid_cutoff_ep = (
            settings.GPSD_PARAM_EPX_EPY_CUTOFF,
            settings.GPSD_PARAM_EPX_EPY_CUTOFF,
            settings.GPSD_PARAM_EPV_CUTOFF,
        )

    async def quit(self):
        await super().quit()
        self.gps_thread.stop()

    async def update(self):
        g = self.gps_thread.data_stream
        try:
            while True:
                await self.sleep()
                total, used = satellites_used(g.satellites)
                gps_time = self.NULL_VALUE
                if g.time != self.NULL_VALUE:
                    gps_time = datetime.strptime(g.time, "%Y-%m-%dT%X.%fZ").replace(
                        tzinfo=timezone.utc
                    )
                await self.get_basic_values(
                    g.lat,
                    g.lon,
                    g.alt,
                    g.speed,
                    g.track,
                    g.mode,
                    [g.epx, g.epy, g.epv],
                    [g.pdop, g.hdop, g.vdop],
                    (used, total),
                    gps_time,
                )
                self.get_sleep_time()
        except asyncio.CancelledError:
            pass

    def is_position_valid(self, lat, lon, mode, dop, satellites, error=None):
        valid = super().is_position_valid(lat, lon, mode, dop, satellites, error)

        if valid and error:
            epv = error[2]
            if None in error or any(
                [x >= self.valid_cutoff_ep[i] for i, x in enumerate(dop)]
            ):
                valid = False
            # special condition #1
            elif (
                satellites[0] < settings.GPSD_PARAM_SP1_USED_SATS_CUTOFF
                and epv > settings.GPSD_PARAM_SP1_EPV_CUTOFF
            ):
                valid = False
        return valid
