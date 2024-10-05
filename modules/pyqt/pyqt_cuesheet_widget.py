from modules._pyqt import QtCore, QtWidgets, QtGui, qasync
from modules.settings import settings

from .pyqt_screen_widget import ScreenWidget

#################################
# values only widget
#################################


# https://stackoverflow.com/questions/46505130/creating-a-marquee-effect-in-pyside/
class MarqueeLabel(QtWidgets.QLabel):
    STYLES = """
      QLabel {
        border-bottom: 1px solid #CCCCCC;
      }
    """
    has_scroll = settings.CUESHEET_SCROLL
    speed = 5
    time = None
    timer_interval = 200  # [ms]

    def __init__(self, config, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.config = config
        self.px = 0
        self.py = 18
        self.textLength = 0

        if self.has_scroll:
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update)

        self.setWordWrap(False)
        self.setStyleSheet(self.STYLES)

    def get_text_length(self, text):
        return self.fontMetrics().horizontalAdvance(text)

    def setText(self, text):
        super().setText(text)
        self.textLength = self.get_text_length(text)

        if self.has_scroll and self.textLength > self.width():
            self.timer.start(self.timer_interval)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.py = int(self.height() * 0.9)

        if not self.has_scroll or self.textLength <= self.width():
            painter.drawText(self.px + 5, self.py, self.text())
            return

        if self.px <= -self.get_text_length(self.text()):
            self.px = self.width()

        painter.drawText(self.px, self.py, self.text())
        painter.translate(self.px, 0)
        self.px -= self.speed


class DistanceLabel(QtWidgets.QLabel):
    STYLES = """
      QLabel {
        padding: 0px 0px 0px 0px;
      }
    """

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setWordWrap(False)
        self.setStyleSheet(self.STYLES)


class CueSheetItem(QtWidgets.QVBoxLayout):
    dist = None
    name = None

    # used on map to set zoom level
    dist_num = 0

    # image used on map
    @property
    def image(self):
        text = self.name.text()
        image = "img/navigation/flag.svg"

        if text == "Right":
            image = "img/navigation/turn_right.svg"
        elif text == "Left":
            image = "img/navigation/turn_left.svg"
        elif text == "Summit":
            image = "img/navigation/summit.svg"

        return image

    @staticmethod
    def get_formatted_distance(distance):
        return f"{distance / 1000:4.1f}km" if distance > 1000 else f"{distance:6.0f}m"

    def __init__(self, parent, config):
        self.config = config

        QtWidgets.QVBoxLayout.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.dist = DistanceLabel()
        self.name = MarqueeLabel(self.config)

        self.addWidget(self.dist)
        self.addWidget(self.name)

    def set(self, dist, name):
        self.dist_num = dist

        # TODO, to fix as for first item if null we compare 0 to 0.0 (so always false)
        #  do we even want to have this (initial point) on the cuesheet anyway?
        if dist < 0:
            return

        self.dist.setText(self.get_formatted_distance(dist))
        self.name.setText(name)

    def reset(self):
        self.dist.setText("")
        self.name.setText("")

    def update_font_size(self, font_size):
        for text, fsize in zip(
            [self.dist, self.name], [int(font_size * 0.9), font_size]
        ):
            q = text.font()
            q.setPixelSize(fsize)
            # q.setStyleStrategy(QtGui.QFont.NoSubpixelAntialias) #avoid subpixel antialiasing on the fonts if possible
            # q.setStyleStrategy(QtGui.QFont.NoAntialias) #don't antialias the fonts
            text.setFont(q)


class CueSheetWidget(ScreenWidget):
    cuesheet = None
    display_num = None
    layout_class = QtWidgets.QVBoxLayout

    def set_font_size(self, length):
        self.font_size = int(length / 7)

    def setup_ui_extra(self):
        self.cuesheet = []

        self.display_num = 5 if settings.VERTICAL else 3

        for i in range(self.display_num):
            cuesheet_point_layout = CueSheetItem(self, self.config)
            self.cuesheet.append(cuesheet_point_layout)
            self.layout.addLayout(cuesheet_point_layout)

    def reset(self):
        for elem in self.cuesheet:
            elem.reset()

    def resizeEvent(self, event):
        self.set_font_size(min(self.size().height(), self.size().width()))

        for i in self.cuesheet:
            i.update_font_size(int(self.font_size))  # for 3 rows

    @qasync.asyncSlot()
    async def update_display(self):
        if not self.course_points.is_set:
            return

        cp_i = self.course.index.course_points_index

        # cuesheet
        for i, cuesheet_item in enumerate(self.cuesheet):
            next = cp_i + i

            if next > len(self.course_points.distance) - 1:
                cuesheet_item.reset()
                continue

            dist = self.course_points.distance[next] * 1000 - self.course.index.distance

            cuesheet_item.set(dist, self.course_points.type[next])
