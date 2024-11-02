from modules.utils.formatter import (
    Altitude,
    Cadence,
    Distance,
    HeartRate,
    Percent,
    Power,
    Speed,
    Temperature,
    Time,
    Timer,
    ValueFormatter,
    Work,
)


from .base import BaseItemConfig


# General
class ElapsedTimeItemConfig(BaseItemConfig):
    name = "Elapsed Time"
    label = "ElapsedTime"
    formatter = Time
    value = "self.logger.values['elapsed_time']"


class GrossAverageSpeedItemConfig(BaseItemConfig):
    name = "Gross Average Speed"
    label = "GrossAvgSPD"
    formatter = Speed
    value = "self.logger.values['gross_avg_spd']"


class GrossDiffTimeItemConfig(BaseItemConfig):
    name = "Gross Diff Time"
    label = "GrossDiffTime"
    formatter = ValueFormatter
    value = "self.logger.values['gross_diff_time']"


class LapItemConfig(BaseItemConfig):
    name = "Lap"
    label = "Lap"
    formatter = ValueFormatter(value_format="d")
    value = "self.logger.values['lap']"


class LapTimeItemConfig(BaseItemConfig):
    name = "Lap Time"
    label = "Lap Time"
    formatter = Timer
    value = "self.logger.values['count_lap']"


class TimerItemConfig(BaseItemConfig):
    name = "Timer"
    label = "Timer"
    formatter = Timer
    value = "self.logger.values['count']"


# Integrated
class DistanceItemConfig(BaseItemConfig):
    name = "Distance"
    label = "Dist."
    formatter = Distance
    value = "self.sensor.values['integrated']['distance']"


class PowerItemConfig(BaseItemConfig):
    name = "Power"
    label = "Power"
    formatter = Power
    value = "self.sensor.values['integrated']['power']"


class SpeedItemConfig(BaseItemConfig):
    name = "Speed"
    label = "Speed"
    formatter = Speed
    value = "self.sensor.values['integrated']['speed']"


class CadenceItemConfig(BaseItemConfig):
    name = "Cadence"
    label = "Cad."
    formatter = Cadence
    value = "self.sensor.values['integrated']['cadence']"


class HeartRateItemConfig(BaseItemConfig):
    name = "Heart Rate"
    label = "HR"
    formatter = HeartRate
    value = "self.sensor.values['integrated']['heart_rate']"


class WorkItemConfig(BaseItemConfig):
    name = "Work"
    label = "Work"
    formatter = Work
    value = "self.sensor.values['integrated']['accumulated_power']"


class WBalItemConfig(BaseItemConfig):
    name = "W'bal"
    label = "W'bal"
    formatter = Work
    value = "self.sensor.values['integrated']['w_prime_balance']"


class WBalNormItemConfig(BaseItemConfig):
    name = "W'bal(Norm)"
    label = "W'bal(Norm)"
    formatter = Percent
    value = "self.sensor.values['integrated']['w_prime_balance_normalized']"


class GradeItemConfig(BaseItemConfig):
    name = "Grade"
    label = "Grade"
    formatter = Percent
    value = "self.sensor.values['integrated']['grade']"


class GradeSpdItemConfig(BaseItemConfig):
    name = "Grade (speed)"
    label = "Grade(spd)"
    formatter = Percent
    value = "self.sensor.values['integrated']['grade_spd']"


class GlideRatioItemConfig(BaseItemConfig):
    name = "Glide Ratio"
    label = "GlideRatio"
    formatter = Altitude
    value = "self.sensor.values['integrated']['glide_ratio']"


class TemperatureItemConfig(BaseItemConfig):
    name = "Temperature"
    label = "Temp"
    formatter = Temperature
    value = "self.sensor.values['integrated']['temperature']"


class CpuMemItemConfig(BaseItemConfig):
    name = "CPU Mem"
    label = "CPU_MEM"
    formatter = ValueFormatter
    value = "self.sensor.values['integrated']['CPU_MEM']"


class SendTimeItemConfig(BaseItemConfig):
    name = "Send Time"
    label = "Send Time"
    formatter = ValueFormatter
    value = "self.sensor.values['integrated']['send_time']"


class Power3sItemConfig(BaseItemConfig):
    name = "Power(3s)"
    label = "Power(3s)"
    formatter = Power
    value = "self.sensor.values['integrated']['ave_power_3s']"


class Power30sItemConfig(BaseItemConfig):
    name = "Power(30s)"
    label = "Power(30s)"
    formatter = Power
    value = "self.sensor.values['integrated']['ave_power_30s']"


class Power60sItemConfig(BaseItemConfig):
    name = "Power(60s)"
    label = "Power(60s)"
    formatter = Power
    value = "self.sensor.values['integrated']['ave_power_60s']"


# Statistics
class PreLapHeartRateItemConfig(BaseItemConfig):
    name = "Pre Lap Heart Rate"
    label = "PLap HR"
    formatter = HeartRate
    value = "self.logger.record_stats['pre_lap_avg']['heart_rate']"


class PreLapCadenceItemConfig(BaseItemConfig):
    name = "Pre Lap Cadence"
    label = "PLap CAD"
    formatter = Cadence
    value = "self.logger.record_stats['pre_lap_avg']['cadence']"


class PreLapDistanceItemConfig(BaseItemConfig):
    name = "Pre Lap Distance"
    label = "PLap DIST"
    formatter = Distance
    value = "self.logger.record_stats['pre_lap_avg']['distance']"


class PreLapSpeedItemConfig(BaseItemConfig):
    name = "Pre Lap Speed"
    label = "PLap SPD"
    formatter = Speed
    value = "self.logger.record_stats['pre_lap_avg']['speed']"


class PreLapPowerItemConfig(BaseItemConfig):
    name = "Pre Lap Power"
    label = "PLap PWR"
    formatter = Speed
    value = "self.logger.record_stats['pre_lap_avg']['power']"


class PreLapWorkItemConfig(BaseItemConfig):
    name = "Pre Lap Work"
    label = "PLap WRK"
    formatter = Speed
    value = "self.logger.record_stats['pre_lap_avg']['accumulated_power']"


class PreLapAscentItemConfig(BaseItemConfig):
    name = "Pre Lap Ascent"
    label = "PLap ASC"
    formatter = Altitude
    value = "self.logger.record_stats['pre_lap_avg']['total_ascent']"


class PreLapDescentItemConfig(BaseItemConfig):
    name = "Pre Lap Descent"
    label = "PLap DSC"
    formatter = Altitude
    value = "self.logger.record_stats['pre_lap_avg']['total_descent']"


class LapHeartRateItemConfig(BaseItemConfig):
    name = "Lap Heart Rate"
    label = "Lap HR"
    formatter = HeartRate
    value = "self.logger.record_stats['lap_avg']['heart_rate']"


class LapCadenceItemConfig(BaseItemConfig):
    name = "Lap Cadence"
    label = "Lap CAD"
    formatter = Cadence
    value = "self.logger.record_stats['lap_avg']['cadence']"


class LapDistanceItemConfig(BaseItemConfig):
    name = "Lap Distance"
    label = "Lap DIST"
    formatter = Distance
    value = "self.logger.record_stats['lap_avg']['distance']"


class LapSpeedItemConfig(BaseItemConfig):
    name = "Lap Speed"
    label = "Lap SPD"
    formatter = Speed
    value = "self.logger.record_stats['lap_avg']['speed']"


class LapPowerItemConfig(BaseItemConfig):
    name = "Lap Power"
    label = "Lap PWR"
    formatter = Speed
    value = "self.logger.record_stats['lap_avg']['power']"


class LapWorkItemConfig(BaseItemConfig):
    name = "Lap Work"
    label = "Lap WRK"
    formatter = Speed
    value = "self.logger.record_stats['lap_avg']['accumulated_power']"


class LapAscentItemConfig(BaseItemConfig):
    name = "Lap Ascent"
    label = "Lap ASC"
    formatter = Altitude
    value = "self.logger.record_stats['lap_avg']['total_ascent']"


class LapDescentItemConfig(BaseItemConfig):
    name = "Lap Descent"
    label = "Lap DSC"
    formatter = Altitude
    value = "self.logger.record_stats['lap_avg']['total_descent']"


class AverageHeartRateItemConfig(BaseItemConfig):
    name = "Average Heart Rate"
    label = "Ave HR"
    formatter = HeartRate
    value = "self.logger.record_stats['entire_avg']['heart_rate']"


class AverageCadenceItemConfig(BaseItemConfig):
    name = "Average Cadence"
    label = "Ave CAD"
    formatter = Cadence
    value = "self.logger.record_stats['entire_avg']['cadence']"


class AverageSpeedItemConfig(BaseItemConfig):
    name = "Average Speed"
    label = "Ave SPD"
    formatter = Speed
    value = "self.logger.record_stats['entire_avg']['speed']"


class AveragePowerItemConfig(BaseItemConfig):
    name = "Average Power"
    label = "Ave PWR"
    formatter = Power
    value = "self.logger.record_stats['entire_avg']['power']"


class MaxHeartRateItemConfig(BaseItemConfig):
    name = "Max Heart Rate"
    label = "Max HR"
    formatter = HeartRate
    value = "self.logger.record_stats['entire_max]['heart_rate']"


class MaxCadenceItemConfig(BaseItemConfig):
    name = "Max Cadence"
    label = "Max CAD"
    formatter = Cadence
    value = "self.logger.record_stats['entire_max']['cadence']"


class MaxSpeedItemConfig(BaseItemConfig):
    name = "Max Speed"
    label = "Max SPD"
    formatter = Speed
    value = "self.logger.record_stats['entire_max']['speed']"


class MaxPowerItemConfig(BaseItemConfig):
    name = "Max Power"
    label = "Max PWR"
    formatter = Power
    value = "self.logger.record_stats['entire_max']['power']"


class LapMaxHeartRateItemConfig(BaseItemConfig):
    name = "Lap Max Heart Rate"
    label = "LMax HR"
    formatter = HeartRate
    value = "self.logger.record_stats['lap_max]['heart_rate']"


class LapMaxCadenceItemConfig(BaseItemConfig):
    name = "Lap Max Cadence"
    label = "LMax CAD"
    formatter = Cadence
    value = "self.logger.record_stats['lap_max']['cadence']"


class LapMaxSpeedItemConfig(BaseItemConfig):
    name = "Lap Max Speed"
    label = "LMax SPD"
    formatter = Speed
    value = "self.logger.record_stats['lap_max']['speed']"


class LapMaxPowerItemConfig(BaseItemConfig):
    name = "Lap Max Power"
    label = "LMax PWR"
    formatter = Power
    value = "self.logger.record_stats['lap_max']['power']"


class PreLapMaxHeartRateItemConfig(BaseItemConfig):
    name = "Pre Lap Max Heart Rate"
    label = "PLMax HR"
    formatter = HeartRate
    value = "self.logger.record_stats['pre_lap_max]['heart_rate']"


class PreLapMaxCadenceItemConfig(BaseItemConfig):
    name = "Pre Lap Max Cadence"
    label = "PLMax CAD"
    formatter = Cadence
    value = "self.logger.record_stats['pre_lap_max']['cadence']"


class PreLapMaxSpeedItemConfig(BaseItemConfig):
    name = "Pre Lap Max Speed"
    label = "PLMax SPD"
    formatter = Speed
    value = "self.logger.record_stats['pre_lap_max']['speed']"


class PreLapMaxPowerItemConfig(BaseItemConfig):
    name = "Pre Lap Max Power"
    label = "PLMax PWR"
    formatter = Power
    value = "self.logger.record_stats['pre_lap_max']['power']"
