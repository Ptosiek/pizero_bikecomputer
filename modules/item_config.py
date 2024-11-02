from modules.utils.formatter import (
    Altitude,
    Cadence,
    Distance,
    GPS_dop,
    GPS_error,
    GPS_fix,
    HeartRate,
    Percent,
    Position,
    Power,
    Pressure,
    Speed,
    Temperature,
    Time,
    Timer,
    ValueFormatter,
    Work,
)

ITEM_CONFIG = {
    # integrated
    "Power": (Power, "self.sensor.values['integrated']['power']"),
    "Speed": (Speed, "self.sensor.values['integrated']['speed']"),
    "Dist.": (Distance, "self.sensor.values['integrated']['distance']"),
    "Distance": (
        Distance,
        "self.sensor.values['integrated']['distance']",
    ),
    "Cad.": (Cadence, "self.sensor.values['integrated']['cadence']"),
    "HR": (HeartRate, "self.sensor.values['integrated']['heart_rate']"),
    "Work": (
        Work,
        "self.sensor.values['integrated']['accumulated_power']",
    ),
    "W'bal": (Work, "self.sensor.values['integrated']['w_prime_balance']"),
    "W'bal(Norm)": (
        Percent,
        "self.sensor.values['integrated']['w_prime_balance_normalized']",
    ),
    "Grade": (Percent, "self.sensor.values['integrated']['grade']"),
    "Grade(spd)": (
        Percent,
        "self.sensor.values['integrated']['grade_spd']",
    ),
    "GlideRatio": (Altitude, "self.sensor.values['integrated']['glide_ratio']"),
    "Temp": (Temperature, "self.sensor.values['integrated']['temperature']"),
    # average_values
    "Power(3s)": (
        Power,
        "self.sensor.values['integrated']['ave_power_3s']",
    ),
    "Power(30s)": (
        Power,
        "self.sensor.values['integrated']['ave_power_30s']",
    ),
    "Power(60s)": (
        Power,
        "self.sensor.values['integrated']['ave_power_60s']",
    ),
    # GPS raw
    "Latitude": (Position, "self.sensor.values['GPS']['lat']"),
    "Longitude": (Position, "self.sensor.values['GPS']['lon']"),
    "Alt.(GPS)": (Altitude, "self.sensor.values['GPS']['alt']"),
    "Speed(GPS)": (Speed, "self.sensor.values['GPS']['speed']"),
    "Dist.(GPS)": (Distance, "self.sensor.values['GPS']['distance']"),
    "Heading(GPS)": (ValueFormatter, "self.sensor.values['GPS']['track_str']"),
    "Satellites": (ValueFormatter, "self.sensor.values['GPS']['used_sats_str']"),
    "Error(x)": (GPS_error, "self.sensor.values['GPS']['epx']"),
    "Error(y)": (GPS_error, "self.sensor.values['GPS']['epy']"),
    "Error(alt)": (GPS_error, "self.sensor.values['GPS']['epv']"),
    "PDOP": (GPS_dop, "self.sensor.values['GPS']['pdop']"),
    "HDOP": (GPS_dop, "self.sensor.values['GPS']['hdop']"),
    "VDOP": (GPS_dop, "self.sensor.values['GPS']['vdop']"),
    "GPSTime": (ValueFormatter, "self.sensor.values['GPS']['utctime']"),
    "GPS Fix": (GPS_fix, "self.sensor.values['GPS']['mode']"),
    "Course Dist.": (
        Distance,
        "self.sensor.values['GPS']['course_distance']",
    ),
    # ANT+ raw
    "HR(ANT+)": (
        HeartRate,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['HR']]['heart_rate']",
    ),
    "Speed(ANT+)": (
        Speed,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['SPD']]['speed']",
    ),
    "Dist.(ANT+)": (
        Distance,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['SPD']]['distance']",
    ),
    "Cad.(ANT+)": (
        Cadence,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['CDC']]['cadence']",
    ),
    # get from sensor as powermeter pairing
    # (cannot get from other pairing not including power sensor pairing)
    "Power16(ANT+)": (
        Power,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['power']",
    ),
    "Power16s(ANT+)": (
        Power,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['power_16_simple']",
    ),
    "Cad.16(ANT+)": (
        Cadence,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['cadence']",
    ),
    "Work16(ANT+)": (
        Work,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['accumulated_power']",
    ),
    "Power R(ANT+)": (
        Power,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['power_r']",
    ),
    "Power L(ANT+)": (
        Power,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['power_l']",
    ),
    "Balance(ANT+)": (
        ValueFormatter,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['lr_balance']",
    ),
    "Power17(ANT+)": (
        Power,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['power']",
    ),
    "Speed17(ANT+)": (
        Speed,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['speed']",
    ),
    "Dist.17(ANT+)": (
        Distance,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['distance']",
    ),
    "Work17(ANT+)": (
        Work,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['accumulated_power']",
    ),
    "Power18(ANT+)": (
        Power,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x12]['power']",
    ),
    "Cad.18(ANT+)": (
        Cadence,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x12]['cadence']",
    ),
    "Work18(ANT+)": (
        Work,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x12]['accumulated_power']",
    ),
    "Torque Ef.(ANT+)": (
        ValueFormatter,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x13]['torque_eff']",
    ),
    "Pedal Sm.(ANT+)": (
        ValueFormatter,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x13]['pedal_sm']",
    ),
    "Light(ANT+)": (
        ValueFormatter,
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['LGT']]['light_mode']",
    ),
    # Sensor raw
    "Temp(I2C)": (Temperature, "self.sensor.values['I2C']['temperature']"),
    "Pressure": (Pressure, "self.sensor.values['I2C']['pressure']"),
    "Altitude": (Altitude, "self.sensor.values['I2C']['altitude']"),
    "Humidity": (Percent, "self.sensor.values['I2C']['humidity']"),
    "Accum.Alt.": (
        Altitude,
        "self.sensor.values['I2C']['accumulated_altitude']",
    ),
    "Vert.Spd": (
        ValueFormatter(value_format="3.1f", unit="m/s"),
        "self.sensor.values['I2C']['vertical_speed']",
    ),
    "Ascent": (Altitude, "self.sensor.values['I2C']['total_ascent']"),
    "Descent": (Altitude, "self.sensor.values['I2C']['total_descent']"),
    "Light": (
        ValueFormatter(value_format=".0f"),
        "self.sensor.values['I2C']['light']",
    ),
    "Infrared": (
        ValueFormatter(value_format=".0f"),
        "self.sensor.values['I2C']['infrared']",
    ),
    "UVI": (ValueFormatter(value_format=".0f"), "self.sensor.values['I2C']['uvi']"),
    "VOC_Index": (
        ValueFormatter(value_format=".0f"),
        "self.sensor.values['I2C']['voc_index']",
    ),
    "Raw_Gas": (
        ValueFormatter(value_format=".0f"),
        "self.sensor.values['I2C']['raw_gas']",
    ),
    "Motion": (
        ValueFormatter(value_format="1.1f"),
        "self.sensor.values['I2C']['motion']",
    ),
    "M_Stat": (
        ValueFormatter(value_format="1.1f"),
        "self.sensor.values['I2C']['m_stat']",
    ),
    "ACC_X": (
        ValueFormatter(value_format="1.1f"),
        "self.sensor.values['I2C']['acc'][0]",
    ),
    "ACC_Y": (
        ValueFormatter(value_format="1.1f"),
        "self.sensor.values['I2C']['acc'][1]",
    ),
    "ACC_Z": (
        ValueFormatter(value_format="1.1f"),
        "self.sensor.values['I2C']['acc'][2]",
    ),
    "Battery": (
        ValueFormatter(value_format="1.0f", unit="%"),
        "self.sensor.values['I2C']['battery_percentage']",
    ),
    "Heading": (ValueFormatter, "self.sensor.values['I2C']['heading_str']"),
    "Pitch": (
        ValueFormatter(value_format="1.0f"),
        "self.sensor.values['I2C']['modified_pitch']",
    ),
    # General
    "Timer": (Timer, "self.logger.values['count']"),
    "LapTime": (Timer, "self.logger.values['count_lap']"),
    "Lap": (ValueFormatter(value_format="d"), "self.logger.values['lap']"),
    "Time": (Time, "0"),
    "ElapsedTime": (Time, "self.logger.values['elapsed_time']"),
    "GrossAvgSPD": (Speed, "self.logger.values['gross_avg_spd']"),
    "GrossDiffTime": (ValueFormatter, "self.logger.values['gross_diff_time']"),
    "CPU_MEM": (ValueFormatter, "self.sensor.values['integrated']['CPU_MEM']"),
    "Send Time": (
        ValueFormatter,
        "self.sensor.values['integrated']['send_time']",
    ),
    # Statistics
    # Pre Lap Average or total
    "PLap HR": (
        HeartRate,
        "self.logger.record_stats['pre_lap_avg']['heart_rate']",
    ),
    "PLap CAD": (
        Cadence,
        "self.logger.record_stats['pre_lap_avg']['cadence']",
    ),
    "PLap DIST": (
        Distance,
        "self.logger.record_stats['pre_lap_avg']['distance']",
    ),
    "PLap SPD": (
        Speed,
        "self.logger.record_stats['pre_lap_avg']['speed']",
    ),
    "PLap PWR": (
        Power,
        "self.logger.record_stats['pre_lap_avg']['power']",
    ),
    "PLap WRK": (
        Work,
        "self.logger.record_stats['pre_lap_avg']['accumulated_power']",
    ),
    "PLap ASC": (
        Altitude,
        "self.logger.record_stats['pre_lap_avg']['total_ascent']",
    ),
    "PLap DSC": (
        Altitude,
        "self.logger.record_stats['pre_lap_avg']['total_descent']",
    ),
    # Lap Average or total
    "Lap HR": (
        HeartRate,
        "self.logger.record_stats['lap_avg']['heart_rate']",
    ),
    "Lap CAD": (
        Cadence,
        "self.logger.record_stats['lap_avg']['cadence']",
    ),
    "Lap DIST": (
        Distance,
        "self.logger.record_stats['lap_avg']['distance']",
    ),
    "Lap SPD": (Speed, "self.logger.record_stats['lap_avg']['speed']"),
    "Lap PWR": (Power, "self.logger.record_stats['lap_avg']['power']"),
    "Lap WRK": (
        Work,
        "self.logger.record_stats['lap_avg']['accumulated_power']",
    ),
    "Lap ASC": (
        Altitude,
        "self.logger.record_stats['lap_avg']['total_ascent']",
    ),
    "Lap DSC": (
        Altitude,
        "self.logger.record_stats['lap_avg']['total_descent']",
    ),
    # Entire Average
    "Ave HR": (
        HeartRate,
        "self.logger.record_stats['entire_avg']['heart_rate']",
    ),
    "Ave CAD": (
        Cadence,
        "self.logger.record_stats['entire_avg']['cadence']",
    ),
    "Ave SPD": (Speed, "self.logger.record_stats['entire_avg']['speed']"),
    "Ave PWR": (Power, "self.logger.record_stats['entire_avg']['power']"),
    # Max
    "Max HR": (
        HeartRate,
        "self.logger.record_stats['entire_max']['heart_rate']",
    ),
    "Max CAD": (
        Cadence,
        "self.logger.record_stats['entire_max']['cadence']",
    ),
    "Max SPD": (Speed, "self.logger.record_stats['entire_max']['speed']"),
    "Max PWR": (Power, "self.logger.record_stats['entire_max']['power']"),
    "LMax HR": (
        HeartRate,
        "self.logger.record_stats['lap_max']['heart_rate']",
    ),
    "LMax CAD": (
        Cadence,
        "self.logger.record_stats['lap_max']['cadence']",
    ),
    "LMax SPD": (Speed, "self.logger.record_stats['lap_max']['speed']"),
    "LMax PWR": (Power, "self.logger.record_stats['lap_max']['power']"),
    "PLMax HR": (
        HeartRate,
        "self.logger.record_stats['pre_lap_max']['heart_rate']",
    ),
    "PLMax CAD": (
        Cadence,
        "self.logger.record_stats['pre_lap_max']['cadence']",
    ),
    "PLMax SPD": (
        Speed,
        "self.logger.record_stats['pre_lap_max']['speed']",
    ),
    "PLMax PWR": (
        Power,
        "self.logger.record_stats['pre_lap_max']['power']",
    ),
}
