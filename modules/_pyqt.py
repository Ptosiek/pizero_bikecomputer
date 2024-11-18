import os

__all__ = [
    "QtCore",
    "QtWidgets",
    "QtGui",
    "Signal",
    "Slot",
    "pg",
    "qasync",
]

import PyQt6.QtCore as QtCore
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui

QT_VERSION_STR = QtCore.QT_VERSION_STR
Signal = QtCore.pyqtSignal
Slot = QtCore.pyqtSlot

# import qasync once pyQt is imported so the correct version is used (it starts with PyQt5 then tries PyQt6)
import qasync  # noqa

# make sure the version is correct in case the underlying code for qasync changed
if qasync.QtModuleName != "PyQt6":
    raise AssertionError(
        f"Wrong version of PyQt6 used for qasync: {qasync.QtModuleName}"
    )

# pyqtgraph will check/try to import PyQT6 on load and might fail if some packages were imported
# (if pyQt6 is halfway installed): so we force the version here
os.environ.setdefault("PYQTGRAPH_QT_LIB", qasync.QtModuleName)

# make sure pyqtgraph it imported from here so PYQTGRAPH_QT_LIB will always be set
import pyqtgraph as pg  # noqa

# set default configuration
pg.setConfigOptions(antialias=True)
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


QT_KEY_BACKTAB = QtCore.Qt.Key.Key_Backtab
QT_KEY_TAB = QtCore.Qt.Key.Key_Tab
QT_KEY_SPACE = QtCore.Qt.Key.Key_Space
QT_KEY_PRESS = QtCore.QEvent.Type.KeyPress
QT_KEY_RELEASE = QtCore.QEvent.Type.KeyRelease
QT_NO_MODIFIER = QtCore.Qt.KeyboardModifier.NoModifier

QT_ALIGN_LEFT = QtCore.Qt.AlignmentFlag.AlignLeft
QT_ALIGN_CENTER = QtCore.Qt.AlignmentFlag.AlignCenter
QT_ALIGN_H_CENTER = QtCore.Qt.AlignmentFlag.AlignHCenter
QT_ALIGN_V_CENTER = QtCore.Qt.AlignmentFlag.AlignVCenter
QT_ALIGN_RIGHT = QtCore.Qt.AlignmentFlag.AlignRight
QT_ALIGN_BOTTOM = QtCore.Qt.AlignmentFlag.AlignBottom
QT_ALIGN_TOP = QtCore.Qt.AlignmentFlag.AlignTop
QT_EXPANDING = QtWidgets.QSizePolicy.Policy.Expanding
QT_FIXED = QtWidgets.QSizePolicy.Policy.Fixed

QT_NO_FOCUS = QtCore.Qt.FocusPolicy.NoFocus
QT_STRONG_FOCUS = QtCore.Qt.FocusPolicy.StrongFocus
QT_TAB_FOCUS_REASON = QtCore.Qt.FocusReason.TabFocusReason
QT_BACKTAB_FOCUS_REASON = QtCore.Qt.FocusReason.BacktabFocusReason

QT_SCROLLBAR_ALWAYSOFF = QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
QT_TEXTEDIT_NOWRAP = QtWidgets.QTextEdit.LineWrapMode.NoWrap

# TODO => QT_STACKONE
QT_STACKINGMODE_STACKONE = QtWidgets.QStackedLayout.StackingMode.StackOne
# TODO => QT_STACKALL
QT_STACKINGMODE_STACKALL = QtWidgets.QStackedLayout.StackingMode.StackAll

QT_PE_WIDGET = QtWidgets.QStyle.PrimitiveElement.PE_Widget

QT_WA_TRANSLUCENT_BACKGROUND = QtCore.Qt.WidgetAttribute.WA_TranslucentBackground

QT_WA_TRANSPARENT_FOR_MOUSE_EVENTS = (
    QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents
)

# for draw_display
QT_FORMAT_RGB888 = QtGui.QImage.Format.Format_RGB888

QT_FORMAT_MONO = QtGui.QImage.Format.Format_Mono

QT_COMPOSITION_MODE_SOURCEIN = QtGui.QPainter.CompositionMode.CompositionMode_SourceIn

QT_COMPOSITION_MODE_DARKEN = QtGui.QPainter.CompositionMode.CompositionMode_Darken
