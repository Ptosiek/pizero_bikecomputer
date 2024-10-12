import logging
from functools import partial

from logger import app_logger
from modules._pyqt import (
    QT_TEXTEDIT_NOWRAP,
    QT_SCROLLBAR_ALWAYSOFF,
    QtWidgets,
    qasync,
)
from modules.constants import MenuLabel
from modules.settings import settings
from modules.utils.network import detect_network
from .pyqt_menu_widget import MenuWidget, ListWidget


class SystemMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions
            (
                MenuLabel.NETWORK,
                "submenu",
                partial(self.change_page, MenuLabel.NETWORK),
            ),
            (
                MenuLabel.UPDATE,
                "dialog",
                lambda: self.config.gui.show_dialog(
                    self.config.update_application, MenuLabel.UPDATE
                ),
            ),
            (MenuLabel.DEBUG, "submenu", partial(self.change_page, MenuLabel.DEBUG)),
            (
                MenuLabel.POWER_OFF,
                "dialog",
                lambda: self.config.gui.show_dialog(
                    self.config.poweroff, MenuLabel.POWER_OFF
                ),
            ),
        )
        self.add_buttons(button_conf)


class NetworkMenuWidget(MenuWidget):
    def setup_menu(self):
        wifi_bt_button_func_wifi = None
        wifi_bt_button_func_bt = None

        if settings.IS_RASPI:
            wifi_bt_button_func_wifi = lambda: self.onoff_wifi_bt(True, "Wifi")
            wifi_bt_button_func_bt = lambda: self.onoff_wifi_bt(True, "Bluetooth")

        button_conf = (
            # Name(page_name), button_attribute, connected functions, layout
            (MenuLabel.WIFI, "toggle", wifi_bt_button_func_wifi),
            (MenuLabel.BLUETOOTH, "toggle", wifi_bt_button_func_bt),
            (
                MenuLabel.BT_TETHERING,
                "submenu",
                partial(self.change_page, MenuLabel.BT_TETHERING),
            ),
            (MenuLabel.IP_ADDRESS, "dialog", self.show_ip_address),
            (MenuLabel.GADGETBRIDGE, "toggle", self.onoff_ble_uart_service),
            (MenuLabel.GET_LOCATION, "toggle", self.onoff_gadgetbridge_gps),
        )
        self.add_buttons(button_conf)

        if (
            not self.config.G_BT_ADDRESSES
        ):  # if bt_pan is None there won't be any addresses
            self.buttons[MenuLabel.BT_TETHERING].disable()

        if self.config.ble_uart is None:
            self.buttons[MenuLabel.GADGETBRIDGE].disable()
            self.buttons[MenuLabel.GET_LOCATION].disable()

    def preprocess(self):
        # initialize toggle button status
        if settings.IS_RASPI:
            self.onoff_wifi_bt(change=False, key="Wifi")
            self.onoff_wifi_bt(change=False, key="Bluetooth")
        if self.config.ble_uart:
            status = self.config.ble_uart.status
            self.buttons[MenuLabel.GADGETBRIDGE].change_toggle(status)
            self.buttons[MenuLabel.GET_LOCATION].change_toggle(
                self.config.ble_uart.gps_status
            )
            self.buttons[MenuLabel.GET_LOCATION].onoff_button(status)

    def onoff_wifi_bt(self, change=True, key=None):
        if change:
            self.config.onoff_wifi_bt(key)

        status = {}
        status["Wifi"], status["Bluetooth"] = self.config.get_wifi_bt_status()
        self.buttons[key].change_toggle(status[key])

    def show_ip_address(self):
        address = detect_network() or "No address"
        # Button is OK only
        self.config.gui.show_dialog_ok_only(None, address)

    @qasync.asyncSlot()
    async def onoff_ble_uart_service(self):
        status = await self.config.ble_uart.on_off_uart_service()
        self.buttons[MenuLabel.GADGETBRIDGE].change_toggle(status)
        self.buttons[MenuLabel.GET_LOCATION].onoff_button(status)
        self.config.state.set_value("GB", status, force_apply=True)

    def onoff_gadgetbridge_gps(self):
        status = self.config.ble_uart.on_off_gadgetbridge_gps()
        self.buttons[MenuLabel.GET_LOCATION].change_toggle(status)
        self.config.state.set_value("GB_gps", status, force_apply=True)


class DebugMenuWidget(MenuWidget):
    is_log_level_debug = False
    initial_log_level = app_logger.level

    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, layout
            (
                MenuLabel.DEBUG_LOG,
                "submenu",
                partial(self.change_page, MenuLabel.DEBUG_LOG),
            ),
            (
                MenuLabel.DEBUG_LEVEL_LOG,
                "toggle",
                self.set_log_level_to_debug,
            ),
            (
                "Disable Wifi/BT",
                "dialog",
                lambda: self.config.gui.show_dialog(
                    partial(self.config.hardware_wifi_bt, False),
                    "Disable Wifi/BT\n(need reboot)",
                ),
            ),
            (
                "Enable Wifi/BT",
                "dialog",
                lambda: self.config.gui.show_dialog(
                    partial(self.config.hardware_wifi_bt, True),
                    "Enable Wifi/BT\n(need reboot)",
                ),
            ),
            (
                MenuLabel.RESTART,
                "dialog",
                lambda: self.config.gui.show_dialog(
                    self.config.restart_application, "Restart Application"
                ),
            ),
            (
                MenuLabel.REBOOT,
                "dialog",
                lambda: self.config.gui.show_dialog(self.config.reboot, "Reboot"),
            ),
        )
        self.add_buttons(button_conf)

    def set_log_level_to_debug(self):
        if self.is_log_level_debug:
            app_logger.setLevel(level=self.initial_log_level)
        else:
            app_logger.setLevel(level=logging.DEBUG)

        app_logger.log(
            app_logger.level,
            f"Log level set to {logging.getLevelName(app_logger.level)}",
        )
        self.is_log_level_debug = not self.is_log_level_debug
        self.buttons[MenuLabel.DEBUG_LEVEL_LOG].change_toggle(self.is_log_level_debug)


class BluetoothTetheringListWidget(ListWidget):
    run_bt_tethering = False

    def __init__(self, parent, page_name, config):
        # keys are used for item label
        self.settings = config.G_BT_ADDRESSES
        super().__init__(parent=parent, page_name=page_name, config=config)

    def preprocess(self, run_bt_tethering=True):
        super().preprocess()
        self.run_bt_tethering = run_bt_tethering

    def get_default_value(self):
        return self.config.G_BT_USE_ADDRESS

    async def button_func_extra(self):
        self.config.G_BT_USE_ADDRESS = self.selected_item.title_label.text()
        # save for restart
        self.config.state.set_value("G_BT_USE_ADDRESS", self.config.G_BT_USE_ADDRESS)

        if self.run_bt_tethering:
            await self.config.bluetooth_tethering()


class DebugLogViewerWidget(MenuWidget):
    def setup_menu(self):
        self.make_menu_layout(QtWidgets.QVBoxLayout)

        # self.scroll_area = QtWidgets.QScrollArea()
        # self.scroll_area.setWidgetResizable(True)
        self.debug_log_screen = QtWidgets.QTextEdit()
        self.debug_log_screen.setReadOnly(True)
        self.debug_log_screen.setLineWrapMode(QT_TEXTEDIT_NOWRAP)
        self.debug_log_screen.setHorizontalScrollBarPolicy(QT_SCROLLBAR_ALWAYSOFF)
        # self.debug_log_screen.setVerticalScrollBarPolicy(QT_SCROLLBAR_ALWAYSOFF)
        # QtWidgets.QScroller.grabGesture(self, QtWidgets.QScroller.LeftMouseButtonGesture)
        # self.scroll_area.setWidget(self.debug_log_screen) if USE_PYQT6 else self.menu_layout.addWidget(self.debug_log_screen)
        # self.menu_layout.addWidget(self.scroll_area)
        self.menu_layout.addWidget(self.debug_log_screen)

    def preprocess(self):
        try:
            with open(settings.LOG_DEBUG_FILE) as f:
                self.debug_log_screen.setText(f.read())
        except FileNotFoundError:
            self.debug_log_screen.setText("No logs found")
