from pathlib import Path

from modules._pyqt import (
    QT_COMPOSITION_MODE_SOURCEIN,
    QT_WA_TRANSLUCENT_BACKGROUND,
    QT_WA_TRANSPARENT_FOR_MOUSE_EVENTS,
    QtCore,
    QtGui,
    QtWidgets,
)

BASE_LOGO_SIZE = 30


class _QIconWithPath(QtGui.QIcon):
    path = ""

    def __init__(self, color=None):
        if color and Path(self.path).suffix == ".svg":
            img = QtGui.QPixmap(self.path)
            qp = QtGui.QPainter(img)
            qp.setCompositionMode(QT_COMPOSITION_MODE_SOURCEIN)
            qp.fillRect(img.rect(), QtGui.QColor(color))
            qp.end()
            super().__init__(img)
        else:
            super().__init__(self.path)


class BackIcon(_QIconWithPath):
    path = "img/back.svg"


class LapIcon(_QIconWithPath):
    path = "img/box_menu/lap.svg"


class MenuIcon(_QIconWithPath):
    path = "img/box_menu/menu.svg"


class NextIcon(_QIconWithPath):
    path = "img/next.svg"


class PauseIcon(_QIconWithPath):
    path = "img/box_menu/pause.svg"


class StartIcon(_QIconWithPath):
    path = "img/box_menu/start.svg"


class ToggleOffIcon(_QIconWithPath):
    path = "img/toggle_off.svg"


class ToggleOffHoverIcon(_QIconWithPath):
    path = "img/toggle_off_hover.svg"


class ToggleOnIcon(_QIconWithPath):
    path = "img/toggle_on_blue.svg"


class CloudIcon(_QIconWithPath):
    path = "img/cloud_upload.svg"


class ZoomInIcon(_QIconWithPath):
    path = "img/map/zoom_in.svg"


class ZoomOutIcon(_QIconWithPath):
    path = "img/map/zoom_out.svg"


class LockIcon(_QIconWithPath):
    path = "img/map/lock.svg"


class LockOpenIcon(_QIconWithPath):
    path = "img/map/lock_open.svg"


class ArrowNorthIcon(_QIconWithPath):
    path = "img/map/arrow_north.svg"


class ArrowSouthIcon(_QIconWithPath):
    path = "img/map/arrow_south.svg"


class ArrowWestIcon(_QIconWithPath):
    path = "img/map/arrow_west.svg"


class ArrowEastIcon(_QIconWithPath):
    path = "img/map/arrow_east.svg"


class DirectionsIcon(_QIconWithPath):
    path = "img/map/directions.svg"


class MapLayersIcon(_QIconWithPath):
    path = "img/map/map_layers.svg"


# "Icons label"
class BaseMenuIcon(QtWidgets.QLabel):
    icon = None  # icon class
    icon_hover = None  # icon hover class
    size = 24  # default icon size
    margin = 10  # default icon margin

    def set_icon(self, icon):
        self.setPixmap(icon.pixmap(self.size))

    def hover(self, hover):
        icon = self.icon_hover if hover else self.icon
        self.set_icon(icon())

    def __init__(self, *args):
        super().__init__(*args)
        self.setAttribute(QT_WA_TRANSLUCENT_BACKGROUND)
        self.setAttribute(QT_WA_TRANSPARENT_FOR_MOUSE_EVENTS)
        self.size = QtCore.QSize(self.size, self.size)
        self.set_icon(self.icon())


class MenuBackgroundIcon(BaseMenuIcon):
    icon = QtGui.QIcon


class MenuRightIcon(BaseMenuIcon):
    icon = NextIcon
    size = 20
    margin = 1

    @staticmethod
    def icon_hover():
        return NextIcon(color="white")


class MenuToggleIcon(BaseMenuIcon):
    icon = ToggleOffIcon
    icon_hover = ToggleOffHoverIcon
    size = 36
    margin = 5

    def toggle(self, status, has_focus):
        if status:
            icon = ToggleOnIcon
        elif has_focus:
            icon = self.icon_hover
        else:
            icon = self.icon
        self.set_icon(icon())


class MenuCloudUploadIcon(BaseMenuIcon):
    icon = CloudIcon


class CourseRightIcon(QtWidgets.QLabel):
    STYLES = """
      border-bottom: 1px solid #AAAAAA;
    """
    margin = 1

    def __init__(self, *args):
        super().__init__(*args)
        icon = NextIcon()
        self.setPixmap(icon.pixmap(QtCore.QSize(20, 20)))
        self.setStyleSheet(self.STYLES)


# LogoIcon
class GarminIcon(_QIconWithPath):
    path = "img/logos/garmin.svg"

    def __init__(self, color=None):
        super().__init__(color)


class RideWithGPSIcon(_QIconWithPath):
    path = "img/logos/rwgps.svg"

    def __init__(self, color=None):
        super().__init__(color)


class StravaIcon(_QIconWithPath):
    path = "img/logos/strava.svg"

    def __init__(self, color=None):
        super().__init__(color)
