from .values import ValuesWidget


class MonitoringWidget(ValuesWidget):
    item_layout = {
        "CPU": [0, 0],
        "Threads": [0, 1],
        "Memory": [1, 0],
    }
