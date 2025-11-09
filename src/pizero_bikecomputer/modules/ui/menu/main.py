from functools import partial

from pizero_bikecomputer.modules.constants import MenuLabel

from .base import BaseWidget, MenuItem, MenuType, MenuWidget


class MainMenuWidget(MenuWidget):
    back_index = 1  # Main widget

    def get_menu_items(self) -> list[MenuItem]:
        return [
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.SENSORS,
                action=partial(self.change_page, MenuLabel.SENSORS),
                icon="📡",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.CONNECTIVITY,
                action=partial(self.change_page, MenuLabel.CONNECTIVITY),
                icon="🌐",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.COURSES,
                action=partial(self.change_page, MenuLabel.COURSES),
                icon="🚴",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.UPLOAD_ACTIVITY,
                action=partial(self.change_page, MenuLabel.UPLOAD_ACTIVITY),
                icon="📤",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.MAP,
                action=partial(self.change_page, MenuLabel.MAP),
                icon="🌍",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.PROFILE,
                action=partial(self.change_page, MenuLabel.PROFILE),
                icon="👤",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.SYSTEM,
                action=partial(self.change_page, MenuLabel.SYSTEM),
                icon="️️⚙️",
            ),
            MenuItem(
                type=MenuType.DIALOG,
                name=MenuLabel.POWER_OFF,
                action=lambda: self.show_dialog(
                    self.config.poweroff, MenuLabel.POWER_OFF
                ),
                icon="📴",
            ),
        ]
