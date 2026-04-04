import logging
from functools import partial

from pizero_bikecomputer.logger import app_logger
from pizero_bikecomputer.modules._pyqt import (
    QT_SCROLLBAR_ALWAYSOFF,
    QT_TEXTEDIT_NOWRAP,
    QtCore,
    QtWidgets,
    Signal,
    Slot,
)
from pizero_bikecomputer.modules.constants import MenuLabel
from pizero_bikecomputer.modules.settings import settings

from ..components import topbar
from .base import BaseWidget, MenuItem, MenuType, MenuWidget


class QtLogHandler(QtCore.QObject, logging.Handler):
    """Custom logging handler that emits Qt signals for real-time log display"""

    log_received = Signal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_received.emit(msg + "\n")
        except Exception:
            self.handleError(record)


class SystemMenuWidget(MenuWidget):
    def get_menu_items(self):
        return [
            MenuItem(
                type=MenuType.DIALOG,
                name=MenuLabel.UPDATE,
                action=lambda: self.show_dialog(
                    self.config.update_application, MenuLabel.UPDATE
                ),
                icon="🔃",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.LOGS,
                action=partial(self.change_page, MenuLabel.LOGS),
                icon="📜",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.DEBUG,
                action=partial(self.change_page, MenuLabel.DEBUG),
                icon="🪄",
            ),
        ]


class DebugMenuWidget(MenuWidget):
    def __init__(self, parent, page_name, config):
        super().__init__(parent, page_name, config)
        self.monitoring_enabled = settings.SYSTEM_MONITORING

    def get_menu_items(self):
        return [
            MenuItem(
                type=MenuType.TOGGLE,
                name=MenuLabel.MONITORING,
                action=self.toggle_monitoring,
                icon="📊",
            ),
            MenuItem(
                type=MenuType.DIALOG,
                name="Disable Wifi/BT",
                action=lambda: self.show_dialog(
                    partial(self.config.hardware_wifi_bt, False),
                    "Disable Wifi/BT\n(need reboot)",
                ),
                icon="",
            ),
            MenuItem(
                type=MenuType.DIALOG,
                name="Enable Wifi/BT",
                action=lambda: self.show_dialog(
                    partial(self.config.hardware_wifi_bt, True),
                    "Enable Wifi/BT\n(need reboot)",
                ),
                icon="",
            ),
            MenuItem(
                type=MenuType.DIALOG,
                name=MenuLabel.RESTART,
                action=lambda: self.show_dialog(
                    self.config.restart_application, "Restart application"
                ),
                icon="🔄",
            ),
            MenuItem(
                type=MenuType.DIALOG,
                name=MenuLabel.REBOOT,
                action=lambda: self.show_dialog(self.config.reboot, "Reboot"),
                icon="🔌",
            ),
        ]

    def toggle_monitoring(self):
        """Toggle system monitoring on/off"""
        self.monitoring_enabled = not self.monitoring_enabled
        settings.update_setting("SYSTEM_MONITORING", self.monitoring_enabled)
        # Update the button's visual toggle state
        self.menu_items[MenuLabel.MONITORING].change_toggle(self.monitoring_enabled)
        app_logger.info(
            f"System monitoring {'enabled' if self.monitoring_enabled else 'disabled'}"
        )

    def preprocess(self, **kwargs):
        """Update toggle state when entering the menu"""
        self.monitoring_enabled = settings.SYSTEM_MONITORING
        # Update the toggle button if it exists
        self.menu_items[settings.MONITORING].change_toggle(self.monitoring_enabled)


class LogViewerWidget(BaseWidget):
    is_log_level_debug = False
    initial_log_level = app_logger.level

    def __init__(self, parent, page_name, config):
        super().__init__(parent, page_name, config)
        self.log_switch = None
        self.log_handler = None
        self.max_lines = 1000  # Maximum number of lines to keep in the viewer
        self.setup_ui()

    def setup_ui(self):
        super().setup_ui()
        # Add toggle switch to top bar
        self.debug_log_switch = topbar.TopBarToggleSwitch(
            initial_state=self.is_log_level_debug
        )
        self.debug_log_switch.toggled.connect(self.set_log_level_to_debug)
        self.top_bar_layout.addWidget(self.debug_log_switch)
        self.log_screen = QtWidgets.QTextEdit()
        self.log_screen.setReadOnly(True)
        self.log_screen.setLineWrapMode(QT_TEXTEDIT_NOWRAP)
        self.log_screen.setHorizontalScrollBarPolicy(QT_SCROLLBAR_ALWAYSOFF)
        self.layout.addWidget(self.log_screen)

    def preprocess(self):
        # Load existing logs from file as initial content
        try:
            with open(settings.LOG_DEBUG_FILE) as f:
                self.log_screen.setText(f.read())
        except FileNotFoundError:
            self.log_screen.setText("No logs found")

        # Scroll to bottom
        self.scroll_to_bottom()

        # Set up real-time log handler
        self.setup_log_handler()

    def setup_log_handler(self):
        """Set up custom logging handler for real-time log display"""
        if self.log_handler is not None:
            return  # Already set up

        # Create and configure the handler with same format as file
        self.log_handler = QtLogHandler()
        self.log_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))

        # Connect the signal to update the log screen
        self.log_handler.log_received.connect(self.append_log)

        # Add handler to app_logger
        app_logger.addHandler(self.log_handler)

    def cleanup_log_handler(self):
        """Remove the log handler when leaving the page"""
        if self.log_handler is not None:
            app_logger.removeHandler(self.log_handler)
            self.log_handler.log_received.disconnect(self.append_log)
            self.log_handler = None

    @Slot(str)
    def append_log(self, log_message: str):
        """Append a new log message to the log screen"""
        # Get current text
        current_text = self.log_screen.toPlainText()

        # Check if we need to trim old lines
        lines = current_text.split("\n")
        if len(lines) >= self.max_lines:
            # Remove oldest lines to stay under the limit
            lines_to_remove = len(lines) - self.max_lines + 100
            current_text = "\n".join(lines[lines_to_remove:])

        # Append new message
        self.log_screen.setPlainText(current_text + log_message)

        # Auto-scroll to bottom to show latest logs
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Scroll the log screen to the bottom"""
        scrollbar = self.log_screen.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def back(self):
        """Override back to clean up the log handler"""
        self.cleanup_log_handler()
        super().back()

    def set_log_level_to_debug(self, is_debug: bool):
        """Set log level to DEBUG or restore initial level"""
        if is_debug:
            app_logger.setLevel(level=logging.DEBUG)
        else:
            app_logger.setLevel(level=self.initial_log_level)

        app_logger.log(
            app_logger.level,
            f"Log level set to {logging.getLevelName(app_logger.level)}",
        )
        self.is_log_level_debug = is_debug
