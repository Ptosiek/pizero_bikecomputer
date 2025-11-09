from functools import partial

from pizero_bikecomputer.modules.constants import MenuLabel

from .base import MenuItem, MenuType, MenuWidget


class ProfileWidget(MenuWidget):
    def get_menu_items(self):
        return [
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.WHEEL_SIZE,
                action=partial(self.change_page, MenuLabel.WHEEL_SIZE),
                icon="WHL",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.CP,
                action=partial(self.change_page, MenuLabel.CP),
                icon="CP",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.W_PRIME_BALANCE,
                action=partial(self.change_page, MenuLabel.W_PRIME_BALANCE),
                icon="W'",
            ),
        ]
