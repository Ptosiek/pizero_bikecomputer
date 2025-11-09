from functools import partial

from pizero_bikecomputer.modules._pyqt import qasync
from pizero_bikecomputer.modules.constants import MenuLabel
from pizero_bikecomputer.modules.settings import settings

from ..components import topbar
from .base import ListWidget, MenuItem, MenuType, MenuWidget


class ConnectivityMenuWidget(MenuWidget):
    def get_menu_items(self):
        if settings.IS_RASPI:
            wifi_bt_button_func_wifi = partial(self.onoff_wifi_bt, True, "Wifi")
            wifi_bt_button_func_bt = partial(self.onoff_wifi_bt, True, "Bluetooth")
        else:
            wifi_bt_button_func_wifi = None
            wifi_bt_button_func_bt = None

        return [
            MenuItem(
                type=MenuType.TOGGLE,
                name=MenuLabel.WIFI,
                action=wifi_bt_button_func_wifi,
                icon="Wifi",
            ),
            MenuItem(
                type=MenuType.TOGGLE,
                name=MenuLabel.BLUETOOTH,
                action=wifi_bt_button_func_bt,
                icon="BT",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.BT_TETHERING_DEVICE,
                action=partial(self.change_page, MenuLabel.BT_TETHERING_DEVICE),
                icon="BT",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.GADGETBRIDGE,
                action=partial(self.change_page, MenuLabel.GADGETBRIDGE),
                icon="GB",
            ),
        ]

    def preprocess(self):
        self.menu_items[MenuLabel.BT_TETHERING_DEVICE].set_state(
            bool(self.config.bt_pan)
        )
        self.menu_items[MenuLabel.GADGETBRIDGE].set_state(bool(self.config.ble_uart))

        if settings.IS_RASPI:
            self.onoff_wifi_bt(change=False, key="Wifi")
            self.onoff_wifi_bt(change=False, key="Bluetooth")

    def onoff_wifi_bt(self, change=True, key=None):
        if change:
            self.config.onoff_wifi_bt(key)

        status = {}
        status["Wifi"], status["Bluetooth"] = self.config.get_wifi_bt_status()
        self.menu_items[key].change_toggle(status[key])


class GadgetBridgeMenuWidget(MenuWidget):
    def setup_ui(self):
        super().setup_ui()
        # also set extra button for topbar
        switch = topbar.TopBarToggleSwitch(
            initial_state=self.config.ble_uart and self.config.ble_uart.status
        )
        switch.toggled.connect(self.toggle_ble_uart_service)
        self.top_bar_layout.addWidget(switch)

    def get_menu_items(self):
        return [
            MenuItem(
                type=MenuType.TOGGLE,
                name=MenuLabel.GET_LOCATION,
                action=self.toggle_gadgetbridge_gps,
                icon="🛰️",
            ),
        ]

    def preprocess(self):
        self.menu_items[MenuLabel.GET_LOCATION].set_state(bool(self.config.ble_uart))

        if self.config.ble_uart:
            self.menu_items[MenuLabel.GET_LOCATION].change_toggle(
                self.config.ble_uart.gps_status
            )

    @qasync.asyncSlot()
    async def toggle_ble_uart_service(self):
        status = await self.config.ble_uart.on_off_uart_service()
        self.menu_items[MenuLabel.GET_LOCATION].change_toggle(status)
        self.menu_items[MenuLabel.GET_LOCATION].set_state(status)
        self.config.state.set_value("GB", status, force_apply=True)

    def toggle_gadgetbridge_gps(self):
        status = self.config.ble_uart.on_off_gadgetbridge_gps()
        self.menu_items[MenuLabel.GET_LOCATION].change_toggle(status)
        self.config.state.set_value("GB_gps", status, force_apply=True)


class BluetoothTetheringListWidget(ListWidget):
    run_bt_tethering = False

    def __init__(self, parent, page_name, config):
        # keys are used for item label
        if config.bt_pan:
            self.settings = {v["name"]: k for k, v in config.bt_pan.devices.items()}
        else:
            self.settings = {}
        super().__init__(parent=parent, page_name=page_name, config=config)

    def setup_ui(self):
        super().setup_ui()
        # also set extra button for topbar
        switch = topbar.TopBarToggleSwitch(initial_state=settings.BT_AUTO_TETHERING)
        switch.toggled.connect(self.bt_auto_tethering)
        self.top_bar_layout.addWidget(switch)

    def preprocess(self, run_bt_tethering=True):
        super().preprocess()
        self.run_bt_tethering = run_bt_tethering

    def get_default_value(self):
        try:
            return self.config.bt_pan.devices[settings.BT_TETHERING_DEVICE]["name"]
        except (AttributeError, KeyError, TypeError, ValueError):
            return None

    def bt_auto_tethering(self):
        settings.update_setting("BT_AUTO_TETHERING", not settings.BT_AUTO_TETHERING)
        # self.config.state.set_value("BT_AUTO_TETHERING", new_value, force_apply=True)

    async def on_click(self):
        bt_address = self.settings[self.selected_item.title_label.text()]
        settings.update_setting("BT_TETHERING_DEVICE", bt_address)

        if self.run_bt_tethering:
            res = await self.config.bt_pan.bluetooth_tethering(bt_address)

            if not res:
                self.config.gui.show_popup("[BT] conn. failed", 2)
