from importlib import resources
from pathlib import Path

from pizero_bikecomputer.modules._pyqt import (
    QT_COMPOSITION_MODE_SOURCEIN,
    QT_WA_TRANSLUCENT_BACKGROUND,
    QT_WA_TRANSPARENT_FOR_MOUSE_EVENTS,
    QtCore,
    QtGui,
    QtWidgets,
)

BASE_DIR = resources.files("pizero_bikecomputer.img")
BASE_LOGO_SIZE = 30


class _QIconWithPath(QtGui.QIcon):
    path: Path = Path("")

    def __init__(self, color=None):
        if color and self.path.suffix == ".svg":
            img = QtGui.QPixmap(str(self.path))
            qp = QtGui.QPainter(img)
            qp.setCompositionMode(QT_COMPOSITION_MODE_SOURCEIN)
            qp.fillRect(img.rect(), QtGui.QColor(color))
            qp.end()
            super().__init__(img)
        else:
            super().__init__(str(self.path))


class BackIcon(_QIconWithPath):
    path = BASE_DIR / "back.svg"


class LapIcon(_QIconWithPath):
    path = BASE_DIR / "box_menu/lap.svg"


class MenuIcon(_QIconWithPath):
    path = BASE_DIR / "box_menu/menu.svg"


class NextIcon(_QIconWithPath):
    path = BASE_DIR / "next.svg"


class PauseIcon(_QIconWithPath):
    path = BASE_DIR / "box_menu/pause.svg"


class StartIcon(_QIconWithPath):
    path = str(resources.files("pizero_bikecomputer.img") / "box_menu/start.svg")


class ToggleOffIcon(_QIconWithPath):
    path = BASE_DIR / "toggle_off.svg"


class ToggleOffHoverIcon(_QIconWithPath):
    path = BASE_DIR / "toggle_off_hover.svg"


class ToggleOnIcon(_QIconWithPath):
    path = BASE_DIR / "toggle_on_blue.svg"


class ZoomInIcon(_QIconWithPath):
    path = BASE_DIR / "map/zoom_in.svg"


class ZoomOutIcon(_QIconWithPath):
    path = BASE_DIR / "map/zoom_out.svg"


class LockIcon(_QIconWithPath):
    path = BASE_DIR / "map/lock.svg"


class LockOpenIcon(_QIconWithPath):
    path = BASE_DIR / "map/lock_open.svg"


class ArrowNorthIcon(_QIconWithPath):
    path = BASE_DIR / "map/arrow_north.svg"


class ArrowSouthIcon(_QIconWithPath):
    path = BASE_DIR / "map/arrow_south.svg"


class ArrowWestIcon(_QIconWithPath):
    path = BASE_DIR / "map/arrow_west.svg"


class ArrowEastIcon(_QIconWithPath):
    path = BASE_DIR / "map/arrow_east.svg"


class DirectionsIcon(_QIconWithPath):
    path = BASE_DIR / "map/directions.svg"


class MapLayersIcon(_QIconWithPath):
    path = BASE_DIR / "map/map_layers.svg"


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


class MenuToggleIcon(BaseMenuIcon):
    icon = ToggleOffIcon
    icon_hover = ToggleOffHoverIcon
    size = 36
    margin = 5

    def __init__(self, *args):
        super().__init__(*args)
        # Set fixed size to ensure consistent alignment
        self.setFixedSize(self.size)

    def toggle(self, status, has_focus):
        if status:
            icon = ToggleOnIcon
        elif has_focus:
            icon = self.icon_hover
        else:
            icon = self.icon
        self.set_icon(icon())


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
    path = BASE_DIR / "logos/garmin.svg"

    def __init__(self, color=None):
        super().__init__(color)


class RideWithGPSIcon(_QIconWithPath):
    path = BASE_DIR / "logos/rwgps.svg"

    def __init__(self, color=None):
        super().__init__(color)


class StravaIcon(_QIconWithPath):
    path = BASE_DIR / "logos/strava.svg"

    def __init__(self, color=None):
        super().__init__(color)
