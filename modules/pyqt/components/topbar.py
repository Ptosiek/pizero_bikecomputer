from modules._pyqt import QT_ALIGN_CENTER, QtCore, QtWidgets

from .icons import BackIcon, NextIcon
from .navi_button import NaviButton


# for some weird reason, inheriting from QtWidgets.QWidget is not working
# if you want to apply styles (neither on Qt5 nor Qt6)
class TopBar:
    def __new__(cls, *args, **kwargs):
        instance = QtWidgets.QWidget(*args, **kwargs)
        return instance


class TopBarLabel(QtWidgets.QLabel):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAlignment(QT_ALIGN_CENTER)


class TopBarBackButton(NaviButton):
    def __init__(self, *args):
        super().__init__(BackIcon(), "", *args)
        self.setIconSize(QtCore.QSize(20, 20))
        self.setProperty("style", "menu")
        self.setFixedSize(40, 32)


class TopBarNextButton(NaviButton):
    def __init__(self, *args):
        super().__init__(NextIcon(), "", *args)
        self.setIconSize(QtCore.QSize(20, 20))
        self.setProperty("style", "menu")
        self.setFixedSize(40, 32)
