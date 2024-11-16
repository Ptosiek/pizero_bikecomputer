from functools import partial

from modules.constants import MenuLabel
from modules.settings import settings
from .pyqt_menu_widget import MenuWidget, ListWidget


class MapMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, layout
            (
                MenuLabel.SELECT_MAP,
                "submenu",
                partial(self.change_page, MenuLabel.SELECT_MAP),
            ),
            (
                MenuLabel.MAP_OVERLAY,
                "submenu",
                partial(self.change_page, MenuLabel.MAP_OVERLAY),
            ),
        )
        self.add_buttons(button_conf)


class MapListWidget(ListWidget):
    settings = settings.MAP_CONFIG

    def get_default_value(self):
        return settings.MAP

    async def button_func_extra(self):
        settings.update_setting("MAP", self.selected_item.title_label.text())
        self.config.gui.map_widget.reset_map()


class MapOverlayMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions
            (MenuLabel.HEAT_MAP, "toggle", partial(self.onoff_map, "Heat map")),
            (
                MenuLabel.HEAT_MAP_LIST,
                "submenu",
                partial(self.change_page, MenuLabel.HEAT_MAP_LIST),
            ),
            (MenuLabel.RAIN_MAP, "toggle", partial(self.onoff_map, "Rain map")),
            (
                MenuLabel.RAIN_MAP_LIST,
                "submenu",
                partial(self.change_page, MenuLabel.RAIN_MAP_LIST),
            ),
            (MenuLabel.WIND_MAP_LIST, "toggle", partial(self.onoff_map, "Wind map")),
            (
                MenuLabel.WIND_MAP_LIST,
                "submenu",
                partial(self.change_page, MenuLabel.WIND_MAP_LIST),
            ),
        )
        self.add_buttons(button_conf)

        self.buttons[MenuLabel.HEAT_MAP_LIST].disable()
        self.buttons[MenuLabel.RAIN_MAP_LIST].disable()
        self.buttons[MenuLabel.WIND_MAP_LIST].disable()

    def onoff_map(self, overlay_type):
        if self.config.gui.map_widget is not None:
            map_widget = self.config.gui.map_widget

            status = map_widget.toggle_overlay(overlay_type)

            self.buttons[overlay_type].change_toggle(status)

            # toggle list
            self.buttons[f"{overlay_type} List"].onoff_button(status)


class HeatmapListWidget(ListWidget):
    settings = settings.HEAT_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.HEAT_OVERLAY_MAP

    async def button_func_extra(self):
        settings.update_setting(
            "HEAT_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        self.config.gui.map_widget.reset_map()


class RainmapListWidget(ListWidget):
    settings = settings.RAIN_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.RAIN_OVERLAY_MAP

    async def button_func_extra(self):
        settings.update_setting(
            "RAIN_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        self.config.gui.map_widget.reset_map()


class WindmapListWidget(ListWidget):
    settings = settings.WIND_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.WIND_OVERLAY_MAP

    async def button_func_extra(self):
        settings.update_setting(
            "WIND_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        self.config.gui.map_widget.reset_map()
