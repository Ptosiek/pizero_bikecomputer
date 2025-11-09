from pizero_bikecomputer.modules.utils.formatter import (
    Cadence,
    Distance,
    HeartRate,
    Power,
    Speed,
    ValueFormatter,
    Work,
)

from ..base import BaseItemConfig


class ANT_HeartRateItemConfig(BaseItemConfig):
    name = "ANT+ Heart Rate"
    label = "HR 📡"
    formatter = HeartRate
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.HEART_RATE)]['heart_rate']"


class ANT_SpeedItemConfig(BaseItemConfig):
    name = "ANT+ Speed"
    label = "Speed 📡"
    formatter = Speed
    value = (
        "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.SPEED)]['speed']"
    )


class ANT_CadenceItemConfig(BaseItemConfig):
    name = "ANT+ Cadence"
    label = "Cad. 📡"
    formatter = Cadence
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.CADENCE)]['cadence']"


class ANT_DistanceItemConfig(BaseItemConfig):
    name = "ANT+ Distance"
    label = "Dist. 📡"
    formatter = Distance
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.SPEED)]['distance']"


class ANT_LightItemConfig(BaseItemConfig):
    name = "ANT+ Light"
    label = "Light"
    formatter = ValueFormatter
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.LIGHT)]['light_mode']"


class ANT_PWR_0x10_PowerItemConfig(BaseItemConfig):
    name = "ANT+ Power 16"
    label = "Power16"
    formatter = Power
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x10]['power']"


class ANT_PWR_0x10_PowerSimpleItemConfig(BaseItemConfig):
    name = "ANT+ Power 16s"
    label = "Power16s"
    formatter = Power
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x10]['power_16_simple']"


class ANT_PWR_0x10_CadenceItemConfig(BaseItemConfig):
    name = "ANT+ Cadence 16"
    label = "Cad.16"
    formatter = Cadence
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x10]['cadence']"


class ANT_PWR_0x10_WorkItemConfig(BaseItemConfig):
    name = "ANT+ Work 16"
    label = "Work16"
    formatter = Work
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x10]['accumulated_power']"


class ANT_PWR_0x10_PowerRItemConfig(BaseItemConfig):
    name = "ANT+ Power R"
    label = "Power R"
    formatter = Power
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x10]['power_r']"


class ANT_PWR_0x10_PowerLItemConfig(BaseItemConfig):
    name = "ANT+ Power L"
    label = "Power L"
    formatter = Power
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x10]['power_l']"


class ANT_PWR_0x10_BalanceItemConfig(BaseItemConfig):
    name = "ANT+ Balance"
    label = "Balance"
    formatter = ValueFormatter
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x10]['lr_balance']"


class ANT_PWR_0x11_PowerItemConfig(BaseItemConfig):
    name = "ANT+ Power 17"
    label = "Power17"
    formatter = Power
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x11]['power']"


class ANT_PWR_0x11_SpeedItemConfig(BaseItemConfig):
    name = "ANT+ Speed 17"
    label = "Speed17"
    formatter = Speed
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x11]['speed']"


class ANT_PWR_0x11_DistanceItemConfig(BaseItemConfig):
    name = "ANT+ Distance 17"
    label = "Dist.17"
    formatter = Distance
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x11]['distance']"


class ANT_PWR_0x11_WorkItemConfig(BaseItemConfig):
    name = "ANT+ Work 17"
    label = "Work17"
    formatter = Work
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x11]['accumulated_power']"


class ANT_PWR_0x11_WorkItemConfig(BaseItemConfig):
    name = "ANT+ Work 17"
    label = "Work17"
    formatter = Work
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x11]['accumulated_power']"


class ANT_PWR_0x12_PowerItemConfig(BaseItemConfig):
    name = "ANT+ Power 18"
    label = "Power18"
    formatter = Power
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x12]['power']"


class ANT_PWR_0x12_CadenceItemConfig(BaseItemConfig):
    name = "ANT+ Cadence 18"
    label = "Cad.18"
    formatter = Cadence
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x12]['cadence']"


class ANT_PWR_0x12_WorkItemConfig(BaseItemConfig):
    name = "ANT+ Work 18"
    label = "Work18"
    formatter = Work
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x12]['accumulated_power']"


class ANT_PWR_0x13_TorqueItemConfig(BaseItemConfig):
    name = "ANT+ Torque Effectiveness"
    label = "Torque Ef."
    formatter = ValueFormatter
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x13]['torque_eff']"


class ANT_PWR_0x13_PedalItemConfig(BaseItemConfig):
    name = "ANT+ Pedal Smoothness"
    label = "Pedal Sm."
    formatter = ValueFormatter
    value = "self.sensor.values['ANT+'][settings.get_ant_device(ANTDevice.POWER)][0x13]['pedal_sm']"
