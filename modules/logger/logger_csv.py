import shutil

from modules.db.sqlite3_utils import sqlite3
from modules.utils.cmd import exec_cmd


class LoggerCsv:
    def __init__(self, db):
        self.db = db

    def write_log(self, filename):
        r = (
            "lap,timer,timestamp,total_timer_time,elapsed_time,heart_rate,speed,cadence,power,distance,"
            "accumulated_power,position_long,position_lat,raw_long,raw_lat,altitude,gps_altitude,course_altitude,"
            "gps_speed,gps_distance,gps_mode,gps_used_sats,gps_total_sats,gps_epx,gps_epy,gps_epv,"
            "gps_pdop,gps_hdop,gps_vdop,total_ascent,total_descent,pressure,temperature,heading,gps_track,"
            "motion,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,cpu_percent,light"
        )

        # if sqlite3 command exists, use this command (much faster)
        if shutil.which("sh") is not None and shutil.which("sqlite3"):
            sql_cmd = f"sqlite3 -header -csv {self.db} 'SELECT {r} FROM BIKECOMPUTER_LOG;' > {filename}"
            sqlite3_cmd = ["sh", "-c", sql_cmd]
            exec_cmd(sqlite3_cmd)
        else:
            con = sqlite3.connect(
                self.db,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            cur = con.cursor()

            with open(filename, "w", encoding="UTF-8") as o:
                # get Lap Records
                o.write(r + "\n")

                for row in cur.execute("SELECT %s FROM BIKECOMPUTER_LOG" % r):
                    o.write(",".join(map(str, row)) + "\n")

            cur.close()
            con.close()

        return True
