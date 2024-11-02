from modules.utils.formatter import (
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
    label = "HR(ANT+)"
    formatter = HeartRate
    value = (
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['HR']]['heart_rate']"
    )


class ANT_SpeedItemConfig(BaseItemConfig):
    name = "ANT+ Speed"
    label = "Speed(ANT+)"
    formatter = Speed
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['SPD']]['speed']"


class ANT_DistanceItemConfig(BaseItemConfig):
    name = "ANT+ Distance"
    label = "Dist.(ANT+)"
    formatter = Distance
    value = (
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['SPD']]['distance']"
    )


class ANT_CadenceItemConfig(BaseItemConfig):
    name = "ANT+ Cadence"
    label = "Cad.(ANT+)"
    formatter = Cadence
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['CDC']]['cadence']"


class ANT_DistanceItemConfig(BaseItemConfig):
    name = "ANT+ Distance"
    label = "Dist(ANT+)"
    formatter = Distance
    value = (
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['SPD']]['distance']"
    )


class ANT_LightItemConfig(BaseItemConfig):
    name = "ANT+ Light"
    label = "Light(ANT+)"
    formatter = ValueFormatter
    value = (
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['LGT']]['light_mode']"
    )


class ANT_PWR_0x10_PowerItemConfig(BaseItemConfig):
    name = "ANT+ Power 16"
    label = "Power16(ANT+)"
    formatter = Power
    value = (
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['power']"
    )


class ANT_PWR_0x10_PowerSimpleItemConfig(BaseItemConfig):
    name = "ANT+ Power 16s"
    label = "Power16s(ANT+)"
    formatter = Power
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['power_16_simple']"


class ANT_PWR_0x10_CadenceItemConfig(BaseItemConfig):
    name = "ANT+ Cadence 16"
    label = "Cad.16(ANT+)"
    formatter = Cadence
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['cadence']"


class ANT_PWR_0x10_WorkItemConfig(BaseItemConfig):
    name = "ANT+ Work 16"
    label = "Work16(ANT+)"
    formatter = Work
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['accumulated_power']"


class ANT_PWR_0x10_PowerRItemConfig(BaseItemConfig):
    name = "ANT+ Power R"
    label = "Power R(ANT+)"
    formatter = Power
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['power_r']"


class ANT_PWR_0x10_PowerLItemConfig(BaseItemConfig):
    name = "ANT+ Power L"
    label = "Power L(ANT+)"
    formatter = Power
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['power_l']"


class ANT_PWR_0x10_BalanceItemConfig(BaseItemConfig):
    name = "ANT+ Balance"
    label = "Balance(ANT+)"
    formatter = ValueFormatter
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x10]['lr_balance']"


class ANT_PWR_0x11_PowerItemConfig(BaseItemConfig):
    name = "ANT+ Power 17"
    label = "Power17(ANT+)"
    formatter = Power
    value = (
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['power']"
    )


class ANT_PWR_0x11_SpeedItemConfig(BaseItemConfig):
    name = "ANT+ Speed 17"
    label = "Speed17(ANT+)"
    formatter = Speed
    value = (
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['speed']"
    )


class ANT_PWR_0x11_DistanceItemConfig(BaseItemConfig):
    name = "ANT+ Distance 17"
    label = "Dist.17(ANT+)"
    formatter = Distance
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['distance']"


class ANT_PWR_0x11_WorkItemConfig(BaseItemConfig):
    name = "ANT+ Work 17"
    label = "Work17(ANT+)"
    formatter = Work
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['accumulated_power']"


class ANT_PWR_0x11_WorkItemConfig(BaseItemConfig):
    name = "ANT+ Work 17"
    label = "Work17(ANT+)"
    formatter = Work
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['accumulated_power']"


class ANT_PWR_0x12_PowerItemConfig(BaseItemConfig):
    name = "ANT+ Power 18"
    label = "Power18(ANT+)"
    formatter = Power
    value = (
        "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x12]['power']"
    )


class ANT_PWR_0x12_CadenceItemConfig(BaseItemConfig):
    name = "ANT+ Cadence 18"
    label = "Cad.18(ANT+)"
    formatter = Cadence
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x12]['cadence']"


class ANT_PWR_0x12_WorkItemConfig(BaseItemConfig):
    name = "ANT+ Work 18"
    label = "Work18(ANT+)"
    formatter = Work
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x11]['accumulated_power']"


class ANT_PWR_0x13_TorqueItemConfig(BaseItemConfig):
    name = "ANT+ Torque Effectiveness"
    label = "Torque Ef.(ANT+)"
    formatter = ValueFormatter
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x13]['torque_eff']"


class ANT_PWR_0x13_PedalItemConfig(BaseItemConfig):
    name = "ANT+ Pedal Smoothness"
    label = "Pedal Sm.(ANT+)"
    formatter = ValueFormatter
    value = "self.sensor.values['ANT+'][self.config.G_ANT['ID_TYPE']['PWR']][0x13]['pedal_sm']"
