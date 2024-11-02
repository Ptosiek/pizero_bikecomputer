from modules.utils.formatter import (
    Altitude,
    Percent,
    Pressure,
    Temperature,
    ValueFormatter,
)

from ..base import BaseItemConfig


class I2C_TemperatureItemConfig(BaseItemConfig):
    name = "I2C Temperature"
    label = "Temp(I2C)"
    formatter = Temperature
    value = "self.sensor.values['I2C']['temperature']"


class I2C_PressureItemConfig(BaseItemConfig):
    name = "I2C Pressure"
    label = "Pressure"
    formatter = Pressure
    value = "self.sensor.values['I2C']['pressure']"


class I2C_AltitudeItemConfig(BaseItemConfig):
    name = "I2C Altitude"
    label = "Altitude"
    formatter = Altitude
    value = "self.sensor.values['I2C']['altitude']"


class I2C_HumidityItemConfig(BaseItemConfig):
    name = "I2C Humidity"
    label = "Humidity"
    formatter = Percent
    value = "self.sensor.values['I2C']['humidity']"


class I2C_AccumulatedAltitudeItemConfig(BaseItemConfig):
    name = "I2C Accumulated Altitude"
    label = "Accum.Alt."
    formatter = Altitude
    value = "self.sensor.values['I2C']['accumulated_altitude']"


class I2C_VerticalSpeedItemConfig(BaseItemConfig):
    name = "I2C Vertical Speed"
    label = "Vert.Spd"
    formatter = (ValueFormatter(value_format="3.1f", unit="m/s"),)
    value = "self.sensor.values['I2C']['vertical_speed']"


class I2C_AscentItemConfig(BaseItemConfig):
    name = "I2C Ascent"
    label = "Ascent"
    formatter = Altitude
    value = "self.sensor.values['I2C']['total_ascent']"


class I2C_DescentItemConfig(BaseItemConfig):
    name = "I2C Descent"
    label = "Descent"
    formatter = Altitude
    value = "self.sensor.values['I2C']['total_descent']"


class I2C_LightItemConfig(BaseItemConfig):
    name = "I2C Light"
    label = "Light"
    formatter = ValueFormatter(value_format=".0f")
    value = "self.sensor.values['I2C']['light']"


class I2C_InfraredItemConfig(BaseItemConfig):
    name = "I2C Infrared"
    label = "Infrared"
    formatter = (ValueFormatter(value_format=".0f"),)
    value = "self.sensor.values['I2C']['infrared']"


class I2C_UVIItemConfig(BaseItemConfig):
    name = "I2C UVI"
    label = "UVI"
    formatter = ValueFormatter(value_format=".0f")
    value = "self.sensor.values['I2C']['uvi']"


class I2C_VOCIndexItemConfig(BaseItemConfig):
    name = "I2C VOC Index"
    label = "VOC Index"
    formatter = ValueFormatter(value_format=".0f")
    value = "self.sensor.values['I2C']['voc_index']"


class I2C_RawGasItemConfig(BaseItemConfig):
    name = "I2C Raw Gas"
    label = "Raw Gas"
    formatter = ValueFormatter(value_format=".0f")
    value = "self.sensor.values['I2C']['raw_gas']"


class I2C_MotionItemConfig(BaseItemConfig):
    name = "I2C Motion"
    label = "Motion"
    formatter = ValueFormatter(value_format="1.1f")
    value = "self.sensor.values['I2C']['motion']"


class I2C_MStatItemConfig(BaseItemConfig):
    name = "I2C M Stat"
    label = "M Stat"
    formatter = ValueFormatter(value_format="1.1f")
    value = "self.sensor.values['I2C']['m_stat']"


class I2C_AccXItemConfig(BaseItemConfig):
    name = "I2C Acc X"
    label = "Acc X"
    formatter = ValueFormatter(value_format="1.1f")
    value = "self.sensor.values['I2C']['acc'][0]"


class I2C_AccYItemConfig(BaseItemConfig):
    name = "I2C Acc Y"
    label = "Acc Y"
    formatter = ValueFormatter(value_format="1.1f")
    value = "self.sensor.values['I2C']['acc'][1]"


class I2C_AccZItemConfig(BaseItemConfig):
    name = "I2C Acc Z"
    label = "Acc Z"
    formatter = ValueFormatter(value_format="1.1f")
    value = "self.sensor.values['I2C']['acc'][2]"


class I2C_HeadingItemConfig(BaseItemConfig):
    name = "I2C Heading"
    label = "Heading"
    formatter = ValueFormatter
    value = "self.sensor.values['I2C']['heading_str']"


class I2C_PitchItemConfig(BaseItemConfig):
    name = "I2C Pitch"
    label = "Pitch"
    formatter = ValueFormatter(value_format="1.0f")
    value = "self.sensor.values['I2C']['modified_pitch']"
