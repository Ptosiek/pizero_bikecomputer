import time

import numpy as np

from logger import app_logger
from modules._pyqt import QT_ALIGN_CENTER, QtWidgets


class ItemLabel(QtWidgets.QLabel):
    right = False

    @property
    def STYLES(self):
        right_border_width = "0px" if self.right else "1px"
        return f"""
            border-width: 0px {right_border_width} 0px 0px;
            border-style: solid;
            border-color: #AAAAAA;
        """

    def __init__(self, right, *__args):
        self.right = right
        super().__init__(*__args)
        self.setAlignment(QT_ALIGN_CENTER)
        self.setStyleSheet(self.STYLES)


class ItemValue(QtWidgets.QLabel):
    bottom = False
    right = False

    @property
    def STYLES(self):
        bottom_border_width = "0px" if self.bottom else "1px"
        right_border_width = "0px" if self.right else "1px"
        return f"""
            border-width: 0px {right_border_width} {bottom_border_width} 0px;
            border-style: solid;
            border-color: #AAAAAA;
        """

    def __init__(self, right, bottom, *__args):
        self.right = right
        self.bottom = bottom
        super().__init__(*__args)
        self.setAlignment(QT_ALIGN_CENTER)
        self.setStyleSheet(self.STYLES)


#################################
# Item Class
#################################
class Item(QtWidgets.QVBoxLayout):
    config = None
    label = None
    value = None
    name = ""

    font_size_unit = 0
    font_size_unit_set = False

    def __init__(self, config, name, font_size, bottom_flag, right_flag, *args):
        super().__init__(*args)
        self.config = config
        self.name = name

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.label = ItemLabel(right_flag, name)
        self.value = ItemValue(right_flag, bottom_flag)

        self.item_format = self.config.gui.gui_config.G_ITEM_DEF[name][0]

        self.addWidget(self.label)
        self.addWidget(self.value)

        self.update_font_size(font_size)
        self.update_value(np.nan)

    def update_value(self, value):
        formatted_value = self.item_format.format_text(value)

        if self.item_format.unit:
            if self.font_size_unit_set:
                formatted_unit = f"<span style='font-size: {self.font_size_unit}px;'> {self.item_format.unit}</span>"
            else:
                formatted_unit = f"<font size=small> {self.item_format.unit}</font>"

            formatted_value = f"{formatted_value} {formatted_unit}"

        self.value.setText(formatted_value)

    def update_font_size(self, font_size):
        # wait one 'refresh cycle' before setting the font size for unit
        if not self.font_size_unit_set and self.font_size_unit != 0:
            self.font_size_unit_set = True

        self.font_size_unit = int(font_size * 0.7)

        for text, fsize in zip(
            [self.label, self.value], [int(font_size * 0.66), font_size]
        ):
            q = text.font()
            q.setPixelSize(fsize)
            # q.setStyleStrategy(QtGui.QFont.NoSubpixelAntialias) # avoid subpixel antialiasing on the fonts if possible
            # q.setStyleStrategy(QtGui.QFont.NoAntialias) # don't antialias the fonts
            text.setFont(q)
