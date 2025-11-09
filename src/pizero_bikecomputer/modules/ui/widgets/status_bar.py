"""
Modern status bar component for bike computer
"""

from datetime import datetime
from typing import Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ..themes import ThemeManager


class StatusIndicator(QLabel):
    """Individual status indicator widget"""

    def __init__(self, icon: str, tooltip: str = "", active: bool = False, parent=None):
        super().__init__(icon, parent)
        self.icon = icon
        self.tooltip_text = tooltip
        self.is_active = active
        self.theme_manager = ThemeManager()

        self._setup_style()
        self._update_state()

    def _setup_style(self):
        """Setup indicator styling"""
        self.setFixedSize(20, 20)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip(self.tooltip_text)

    def _update_state(self):
        """Update visual state"""
        theme = self.theme_manager.get_theme()

        if self.is_active:
            color = theme.colors["primary"]
            font_size = 14
        else:
            color = theme.colors["on_surface_variant"]
            font_size = 12

        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
                background-color: transparent;
            }}
            QWidget#battery_widget {{
                background-color: transparent;
            }}
        """)

    def set_active(self, active: bool):
        """Set active state"""
        self.is_active = active
        self._update_state()

    def update_tooltip(self, tooltip: str):
        """Update tooltip text"""
        self.tooltip_text = tooltip
        self.setToolTip(tooltip)


class StatusBar(QWidget):
    """
    Modern status bar with system information and indicators
    Inspired by smartphone status bars and Garmin devices
    """

    battery_clicked = pyqtSignal()
    indicator_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.theme_manager = ThemeManager()

        # Status data
        self.time_format = 24  # 12 or 24 hour format
        self.show_seconds = False
        self.battery_level = 100
        self.battery_charging = False
        self.connection_status = {
            "gps": False,
            "bluetooth": False,
            "ant+": False,
            "wifi": False,
        }

        # Indicators
        self.indicators = {}

        # Animation
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._blink_indicators)
        self.blink_state = False

        self.setup_ui()
        self.setup_style()
        self.setup_timer()

    def setup_ui(self):
        self.setFixedHeight(40)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 4, 16, 4)
        main_layout.setSpacing(16)

        # Left side - Time
        self.time_label = QLabel("00:00")
        self.time_label.setObjectName("time_label")
        main_layout.addWidget(self.time_label)

        # Spacer
        main_layout.addStretch()

        # Center - Connection indicators
        self.indicators_layout = QHBoxLayout()
        self.indicators_layout.setContentsMargins(0, 0, 0, 0)
        self.indicators_layout.setSpacing(12)

        # GPS indicator
        self.indicators["gps"] = StatusIndicator("🛰️", "GPS: Disconnected", False)
        self.indicators_layout.addWidget(self.indicators["gps"])

        # Bluetooth indicator
        self.indicators["bluetooth"] = StatusIndicator(
            "📶", "Bluetooth: Disconnected", False
        )
        self.indicators_layout.addWidget(self.indicators["bluetooth"])

        # ANT+ indicator
        self.indicators["ant+"] = StatusIndicator("📡", "ANT+: Disconnected", False)
        self.indicators_layout.addWidget(self.indicators["ant+"])

        # WiFi indicator
        self.indicators["wifi"] = StatusIndicator("🌐", "WiFi: Disconnected", False)
        self.indicators_layout.addWidget(self.indicators["wifi"])

        main_layout.addLayout(self.indicators_layout)

        # Spacer
        main_layout.addStretch()

        # Right side - Battery
        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Battery indicator
        self.battery_widget = self._create_battery_widget()
        right_layout.addWidget(self.battery_widget)

        main_layout.addLayout(right_layout)

    def setup_style(self):
        """Apply theme-based styling"""
        theme = self.theme_manager.get_theme()

        style = f"""
            StatusBar {{
                background-color: {theme.colors["surface"]};
                border-top: 1px solid {theme.colors["border"]};
            }}
            #time_label {{
                color: {theme.colors["on_surface"]};
                font-size: 14px;
                font-weight: 500;
                background-color: transparent;
            }}
            #battery_icon, #battery_label {{
                color: {theme.colors["on_surface_variant"]};
                font-size: 12px;
                background-color: transparent;
            }}
            QWidget#battery_widget {{
                background-color: transparent;
            }}
        """

        self.setStyleSheet(style)

        self.time_label.setFont(self.theme_manager.get_font("body"))

    def setup_timer(self):
        """Setup update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_time)
        self.update_timer.start(1000)  # Update every second

    def _create_battery_widget(self) -> QWidget:
        """Create battery status widget"""
        widget = QWidget()
        widget.setObjectName("battery_widget")
        widget.setFixedSize(50, 24)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        widget.mousePressEvent = lambda e: self.battery_clicked.emit()

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Battery icon
        self.battery_icon = QLabel("🔋")
        self.battery_icon.setObjectName("battery_icon")
        self.battery_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Battery percentage
        self.battery_label = QLabel("100%")
        self.battery_label.setObjectName("battery_label")
        self.battery_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.battery_icon)
        layout.addWidget(self.battery_label)

        return widget

    def _update_time(self):
        """Update time display"""
        now = datetime.now()
        if self.time_format == 24:
            if self.show_seconds:
                time_str = now.strftime("%H:%M:%S")
            else:
                time_str = now.strftime("%H:%M")
        else:
            if self.show_seconds:
                time_str = now.strftime("%I:%M:%S %p")
            else:
                time_str = now.strftime("%I:%M %p")

        self.time_label.setText(time_str)

    def _blink_indicators(self):
        """Blink indicators for attention"""
        self.blink_state = not self.blink_state

        # Blink indicators that need attention
        for name, indicator in self.indicators.items():
            if name == "gps" and not self.connection_status["gps"]:
                # Blink GPS when searching
                if self.blink_state:
                    indicator.setStyleSheet("color: #FF9800;")
                else:
                    indicator.setStyleSheet("color: #555555;")

    def set_time_format(self, format_24: bool, show_seconds: bool = False):
        """Set time display format"""
        self.time_format = 24 if format_24 else 12
        self.show_seconds = show_seconds

    def update_battery_status(self, level: int, charging: bool = False):
        """Update battery status display"""
        self.battery_level = max(0, min(100, level))
        self.battery_charging = charging

        # Update icon
        if charging:
            icon = "🔌"
        elif self.battery_level < 20:
            icon = "🪫"
        else:
            icon = "🔋"

        if hasattr(self, "battery_icon"):
            self.battery_icon.setText(icon)
        if hasattr(self, "battery_label"):
            self.battery_label.setText(f"{self.battery_level}%")
        if hasattr(self, "battery_text"):
            self.battery_text.setText(f"{self.battery_level}%")

        # Update tooltip
        if hasattr(self, "battery_widget"):
            status = "Charging" if charging else f"{self.battery_level}% remaining"
            self.battery_widget.setToolTip(f"Battery: {status}")

    def update_connection_status(
        self,
        gps: bool = False,
        bluetooth: bool = False,
        ant_plus: bool = False,
        wifi: bool = False,
    ):
        """Update connection status indicators"""
        self.connection_status["gps"] = gps
        self.connection_status["bluetooth"] = bluetooth
        self.connection_status["ant+"] = ant_plus
        self.connection_status["wifi"] = wifi

        # Update GPS indicator
        if "gps" in self.indicators:
            if gps:
                self.indicators["gps"].set_active(True)
                self.indicators["gps"].update_tooltip("GPS: Connected")
                self.indicators["gps"].setText("🛰️")
            else:
                self.indicators["gps"].set_active(False)
                self.indicators["gps"].update_tooltip("GPS: Searching...")
                self.indicators["gps"].setText("🛰️")

        # Update Bluetooth indicator
        if "bluetooth" in self.indicators:
            if bluetooth:
                self.indicators["bluetooth"].set_active(True)
                self.indicators["bluetooth"].update_tooltip("Bluetooth: Connected")
                self.indicators["bluetooth"].setText("📶")
            else:
                self.indicators["bluetooth"].set_active(False)
                self.indicators["bluetooth"].update_tooltip("Bluetooth: Disconnected")
                self.indicators["bluetooth"].setText("📶")

        # Update ANT+ indicator
        if "ant+" in self.indicators:
            if ant_plus:
                self.indicators["ant+"].set_active(True)
                self.indicators["ant+"].update_tooltip("ANT+: Connected")
                self.indicators["ant+"].setText("📡")
            else:
                self.indicators["ant+"].set_active(False)
                self.indicators["ant+"].update_tooltip("ANT+: Disconnected")
                self.indicators["ant+"].setText("📡")

        # Update WiFi indicator
        if "wifi" in self.indicators:
            if wifi:
                self.indicators["wifi"].set_active(True)
                self.indicators["wifi"].update_tooltip("WiFi: Connected")
                self.indicators["wifi"].setText("🌐")
            else:
                self.indicators["wifi"].set_active(False)
                self.indicators["wifi"].update_tooltip("WiFi: Disconnected")
                self.indicators["wifi"].setText("🌐")

        # Start/stop blinking for GPS
        if gps:
            self.blink_timer.stop()
            self.indicators["gps"].setStyleSheet("")  # Reset blinking
        else:
            self.blink_timer.start(1000)  # Start blinking

    def set_gps_satellites(self, satellites: int):
        """Update GPS satellite count"""
        if "gps" in self.indicators:
            tooltip = (
                f"GPS: {satellites} satellites"
                if self.connection_status["gps"]
                else f"GPS: Searching... ({satellites} satellites)"
            )
            self.indicators["gps"].update_tooltip(tooltip)

    def show_temporary_message(self, message: str, duration: int = 3000):
        """Show temporary message in status bar"""
        original_time = self.time_label.text()
        self.time_label.setText(message)
        self.time_label.setStyleSheet("color: #2196F3; font-weight: bold;")

        QTimer.singleShot(duration, lambda: self._restore_time_display(original_time))

    def _restore_time_display(self, original_time: str):
        """Restore original time display"""
        self.time_label.setText(original_time)
        self._setup_style()  # Restore original styling

    def get_status_summary(self) -> dict[str, Any]:
        """Get current status summary"""
        return {
            "time": self.time_label.text(),
            "battery_level": self.battery_level,
            "battery_charging": self.battery_charging,
            "connections": self.connection_status.copy(),
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        theme = self.theme_manager.get_theme()

        # Draw subtle gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(theme.colors["surface"]))
        gradient.setColorAt(1.0, QColor(theme.colors["surface_variant"]))

        painter.fillRect(self.rect(), gradient)
        super().paintEvent(event)
