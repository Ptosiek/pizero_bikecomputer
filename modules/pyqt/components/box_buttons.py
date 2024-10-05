from modules._pyqt import QtWidgets
from .icons import BackIcon, LapIcon, PauseIcon, MenuIcon, NextIcon, StartIcon
from .navi_button import NaviButton


class LapButton(QtWidgets.QPushButton):
    STYLES = """
      QPushButton {
        border-color: none;
        border-style: outset;
        border-width: 0px;
      }
    """

    def __init__(self, *args):
        super().__init__(LapIcon(), "", *args)
        self.setStyleSheet(self.STYLES)
        self.setFixedSize(50, 30)
        # long press
        self.setAutoRepeat(True)
        self.setAutoRepeatDelay(1000)
        self.setAutoRepeatInterval(1000)
        self._state = 0


class MenuButton(QtWidgets.QPushButton):
    STYLES = """
      QPushButton {
        border-color: none;
        border-style: outset;
        border-width: 0px;
      }
    """

    def __init__(self, *args):
        super().__init__(MenuIcon(), "", *args)
        self.setFixedSize(50, 30)
        self.setStyleSheet(self.STYLES)


class ScrollNextButton(NaviButton):
    def __init__(self, *args):
        super().__init__(NextIcon(), "", *args)
        self.setFixedSize(60, 30)


class ScrollPrevButton(NaviButton):
    def __init__(self, *args):
        super().__init__(BackIcon(), "", *args)
        self.setFixedSize(60, 30)


class StartButton(QtWidgets.QPushButton):
    STYLES = """
      QPushButton {
        border-color: none;
        border-style: outset;
        border-width: 0px;
      }
    """

    def __init__(self, *args):
        super().__init__(StartIcon(), "", *args)
        self.setStyleSheet(self.STYLES)
        self.setFixedSize(50, 30)
        # long press
        self.setAutoRepeat(True)
        self.setAutoRepeatDelay(1000)
        self.setAutoRepeatInterval(1000)
        self._state = 0

    def toggle(self, status):
        icon = PauseIcon() if status == "START" else StartIcon()
        self.setIcon(icon)
