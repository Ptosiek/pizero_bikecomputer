from functools import partial

from pizero_bikecomputer.modules.constants import MenuLabel, OverlayMap
from pizero_bikecomputer.modules.settings import settings

from ..components import topbar
from .base import ListWidget, MenuItem, MenuType, MenuWidget


class MapMenuWidget(MenuWidget):
    def get_menu_items(self):
        return [
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.SELECT_MAP,
                action=partial(self.change_page, MenuLabel.SELECT_MAP),
                icon="🌍",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.HEAT_MAP,
                action=partial(self.change_page, MenuLabel.HEAT_MAP),
                icon="🔥",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.RAIN_MAP,
                action=partial(self.change_page, MenuLabel.RAIN_MAP),
                icon="💧",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.WIND_MAP,
                action=partial(self.change_page, MenuLabel.WIND_MAP),
                icon="🌪️",
            ),
        ]


class MapListWidget(ListWidget):
    settings = settings.MAP_CONFIG

    def get_default_value(self):
        return settings.MAP

    async def on_click(self):
        settings.update_setting("MAP", self.selected_item.title_label.text())
        self.config.gui.map_widget.reset_map()


class OverlayMapWidget(ListWidget):
    map_name: OverlayMap

    def setup_ui(self):
        super().setup_ui()
        # also set extra button for topbar
        switch = topbar.TopBarToggleSwitch()
        switch.toggled.connect(partial(self.toggle_overlay, self.map_name))
        self.top_bar_layout.addWidget(switch)

    def toggle_overlay(self, overlay_type: OverlayMap):
        if self.config.gui.map_widget is not None:
            self.config.gui.map_widget.toggle_overlay(overlay_type)


class HeatmapListWidget(OverlayMapWidget):
    map_name = OverlayMap.HEAT_MAP
    settings = settings.HEAT_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.HEAT_OVERLAY_MAP

    async def on_click(self):
        settings.update_setting(
            "HEAT_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        self.config.gui.map_widget.reset_map()


class RainmapListWidget(OverlayMapWidget):
    map_name = OverlayMap.RAIN_MAP
    settings = settings.RAIN_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.RAIN_OVERLAY_MAP

    async def on_click(self):
        settings.update_setting(
            "RAIN_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        self.config.gui.map_widget.reset_map()


class WindmapListWidget(OverlayMapWidget):
    map_name = OverlayMap.WIND_MAP
    settings = settings.WIND_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.WIND_OVERLAY_MAP

    async def on_click(self):
        settings.update_setting(
            "WIND_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        self.config.gui.map_widget.reset_map()
