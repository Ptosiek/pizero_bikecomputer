from functools import partial

from modules.constants import MenuLabel
from .pyqt_menu_widget import MenuWidget


class ProfileWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions
            (
                MenuLabel.WHEEL_SIZE,
                "submenu",
                partial(self.change_page, MenuLabel.WHEEL_SIZE),
            ),
            (
                MenuLabel.CP,
                "submenu",
                partial(self.change_page, MenuLabel.CP),
            ),
            (
                MenuLabel.W_PRIME_BALANCE,
                "submenu",
                partial(self.change_page, MenuLabel.W_PRIME_BALANCE),
            ),
        )
        self.add_buttons(button_conf)
