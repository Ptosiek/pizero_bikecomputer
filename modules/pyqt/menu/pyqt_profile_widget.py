from .pyqt_menu_widget import MenuWidget


class ProfileWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, layout
            ("Wheel Size", "submenu", self.adjust_wheel_circumference),
            ("CP", "submenu", self.adjust_cp),
            ("W Prime Balance", "submenu", self.adjust_w_prime_balance),
        )
        self.add_buttons(button_conf)

    def adjust_cp(self):
        self.change_page("CP", preprocess=True)

    def adjust_w_prime_balance(self):
        self.change_page("W Prime Balance", preprocess=True)

    def adjust_wheel_circumference(self):
        self.change_page("Wheel Size", preprocess=True)
