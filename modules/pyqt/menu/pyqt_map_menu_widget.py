import asyncio
from functools import partial

from modules.settings import settings
from modules.utils.map import check_map_dir
from .pyqt_menu_widget import MenuWidget, ListWidget


class MapMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, layout
            ("Select Map", "submenu", self.select_map),
            ("Map Overlay", "submenu", self.map_overlay),
            ("Course Calc", None, None),
        )
        self.add_buttons(button_conf)

    def select_map(self):
        self.change_page("Select Map", preprocess=True)

    def map_overlay(self):
        self.change_page("Map Overlay")


class MapListWidget(ListWidget):
    settings = settings.MAP_CONFIG

    def get_default_value(self):
        return settings.MAP

    async def button_func_extra(self):
        settings.update_setting("MAP", self.selected_item.title_label.text())
        # reset map
        check_map_dir()
        self.config.gui.map_widget.reset_map()


class MapOverlayMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, layout
            ("Heatmap", "toggle", partial(self.onoff_map, "Heatmap")),
            ("Heatmap List", "submenu", self.select_heatmap),
            ("Rain map", "toggle", partial(self.onoff_map, "Rain map")),
            ("Rain map List", "submenu", self.select_rainmap),
            ("Wind map", "toggle", partial(self.onoff_map, "Wind map")),
            ("Wind map List", "submenu", self.select_windmap),
        )
        self.add_buttons(button_conf)

        self.buttons["Heatmap List"].disable()
        self.buttons["Rain map List"].disable()
        self.buttons["Wind map List"].disable()

    def onoff_map(self, overlay_type):
        if self.config.gui.map_widget is not None:
            map_widget = self.config.gui.map_widget

            status = map_widget.toggle_overlay(overlay_type)

            self.buttons[overlay_type].change_toggle(status)

            # toggle list
            self.buttons[f"{overlay_type} List"].onoff_button(status)

    def select_heatmap(self):
        self.change_page("Heatmap List", preprocess=True)

    def select_rainmap(self):
        self.change_page("Rain map List", preprocess=True)

    def select_windmap(self):
        self.change_page("Wind map List", preprocess=True)


class HeatmapListWidget(ListWidget):
    settings = settings.HEATMAP_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.HEATMAP_OVERLAY_MAP

    async def button_func_extra(self):
        settings.update_setting(
            "HEATMAP_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        # reset map
        check_map_dir()
        self.config.gui.map_widget.reset_map()

        # update strava cookie
        if "strava_heatmap" in settings.HEATMAP_OVERLAY_MAP:
            asyncio.get_running_loop().run_in_executor(
                None, self.config.api.get_strava_cookie
            )


class RainmapListWidget(ListWidget):
    settings = settings.RAIN_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.RAIN_OVERLAY_MAP

    async def button_func_extra(self):
        settings.update_setting(
            "RAIN_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        # reset map
        check_map_dir()
        self.config.gui.map_widget.reset_map()


class WindmapListWidget(ListWidget):
    settings = settings.WIND_OVERLAY_MAP_CONFIG

    def get_default_value(self):
        return settings.WIND_OVERLAY_MAP

    async def button_func_extra(self):
        settings.update_setting(
            "WIND_OVERLAY_MAP", self.selected_item.title_label.text()
        )
        # reset map
        check_map_dir()
        self.config.gui.map_widget.reset_map()
