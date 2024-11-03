from functools import partial

from logger import app_logger
from modules._pyqt import QtCore, QtWidgets, QtGui
from modules.constants import MenuLabel, ANTDevice
from modules.sensor.ant.ant_code import AntCode
from modules.settings import settings
from .pyqt_menu_widget import MenuWidget, ListWidget, ListItemWidget


class SensorMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions
            (
                MenuLabel.ANT_SENSORS,
                "submenu",
                partial(self.change_page, MenuLabel.ANT_SENSORS),
            ),
            (MenuLabel.ADJUST_ALTITUDE, "submenu", self.adjust_altitude),
        )
        self.add_buttons(button_conf)

    def adjust_altitude(self):
        self.change_page(MenuLabel.ADJUST_ALTITUDE)
        # temporary
        self.config.logger.sensor.sensor_i2c.recalibrate_position()


class ANTMenuWidget(MenuWidget):
    items = {
        ANTDevice.HEART_RATE: "Heart Rate",
        ANTDevice.SPEED: "Speed",
        ANTDevice.CADENCE: "Cadence",
        ANTDevice.POWER: "Power",
        ANTDevice.LIGHT: "Light",
        ANTDevice.CONTROL: "Control",
        ANTDevice.TEMPERATURE: "Temperature",
    }

    def setup_menu(self):
        self.add_buttons(
            [(name, "submenu", partial(self.setting_ant, name)) for name in self.items]
        )

        for name in self.items:
            self.buttons[name].setText(self.get_button_state(name))

        if not self.config.display.has_touch:
            self.focus_widget = self.buttons[next(iter(self.items.keys()))]

    def get_button_state(self, ant_name):
        status = "OFF"
        if settings.is_ant_device_enabled(ant_name):
            device_id, _ = settings.get_ant_device(ant_name)

            if device_id is not None:
                status = f"{device_id:05d}"
            else:
                status = "No dev"
        return f"{self.items[ant_name]}: {status}"

    def setting_ant(self, ant_name):
        if settings.is_ant_device_enabled(ant_name):
            # disable ANT+ sensor
            self.config.logger.sensor.sensor_ant.disconnect_ant_sensor(ant_name)
        else:
            # search ANT+ sensor
            self.change_page(MenuLabel.ANT_DETAIL, reset=True, list_type=ant_name)

        self.update_button_label()

    def update_button_label(self):
        for ant_name in self.buttons.keys():
            self.buttons[ant_name].setText(self.get_button_state(ant_name))


class ANTListWidget(ListWidget):
    ant_sensor_types = None

    def __init__(self, parent, page_name, config):
        self.ant_sensor_types = {}
        super().__init__(parent, page_name, config)

    def setup_menu(self):
        super().setup_menu()
        # update panel for every 1 seconds
        self.timer = QtCore.QTimer(parent=self)
        self.timer.timeout.connect(self.update_display)

    async def button_func_extra(self):
        if self.selected_item is None:
            return

        app_logger.info(f"connect {self.list_type}: {self.selected_item.id}")

        ant_id = int(self.selected_item.id)
        self.config.logger.sensor.sensor_ant.connect_ant_sensor(
            self.list_type,  # sensor type
            ant_id,  # ID
            self.ant_sensor_types[ant_id][0],  # id_type
            self.ant_sensor_types[ant_id][1],  # connection status
        )

    def on_back_menu(self):
        self.timer.stop()
        self.config.logger.sensor.sensor_ant.searcher.stop_search()
        # button update
        self.parentWidget().findChild(
            QtWidgets.QWidget, MenuLabel.ANT_SENSORS
        ).update_button_label()

    def preprocess_extra(self):
        self.ant_sensor_types.clear()
        self.config.logger.sensor.sensor_ant.searcher.search(self.list_type)
        self.timer.start(settings.DRAW_INTERVAL)

    def update_display(self):
        detected_sensors = (
            self.config.logger.sensor.sensor_ant.searcher.get_search_list()
        )

        for ant_id, ant_type_array in detected_sensors.items():
            ant_id_str = f"{ant_id:05d}"
            add = ant_id not in self.ant_sensor_types

            if add:
                self.ant_sensor_types[ant_id] = ant_type_array
                status = ant_type_array[1]
                status_str = " (connected)" if status else ""
                sensor_type = AntCode.TYPE[ant_type_array[0]]
                title = f"{sensor_type} {status_str}".strip()
                ant_item = ANTListItemWidget(self, ant_id_str, title)

                self.add_list_item(ant_item)

                app_logger.debug(f"Adding ANT+ sensor: {title}")


class ANTListItemWidget(ListItemWidget):
    id = None

    def __init__(self, parent, ant_id, title):
        self.id = ant_id
        super().__init__(parent, title, detail=f"   ID: {ant_id}")

    def setup_ui(self):
        super().setup_ui()
        dummy_px = QtGui.QPixmap(20, 20)
        dummy_px.fill(QtGui.QColor("#008000"))
        icon = QtWidgets.QLabel()
        icon.setPixmap(dummy_px)
        icon.setContentsMargins(5, 0, 10, 0)

        # outer layout (custom)
        self.outer_layout.insertWidget(0, icon)
        self.enter_signal.connect(self.parentWidget().button_func)
