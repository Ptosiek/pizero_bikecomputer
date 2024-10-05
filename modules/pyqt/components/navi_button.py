from modules._pyqt import QtWidgets


class NaviButton(QtWidgets.QPushButton):
    STYLES = """
      QPushButton {
        color: none;
        border: 0px solid;
        border-radius: 15px;
        outline: 0;
      }

      QPushButton[style='menu']:focus {
        border-width: 3px;
      }
    """

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setStyleSheet(self.STYLES)
