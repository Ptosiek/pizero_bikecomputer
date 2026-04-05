from pizero_bikecomputer.modules.settings import settings

from .values import ValuesWidget


class MonitoringWidget(ValuesWidget):
    item_layout = {
        "CPU": [0, 0],
        "Threads": [0, 1],
        "Memory": [1, 0],
    }

    @property
    def visible(self):
        return settings.SYSTEM_MONITORING
