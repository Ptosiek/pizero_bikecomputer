from pizero_bikecomputer.modules._pyqt import QT_ALIGN_CENTER, QtCore, QtWidgets, Signal

from .icons import BackIcon, MenuToggleIcon, NextIcon
from .navi_button import NaviButton


# for some weird reason, inheriting from QtWidgets.QWidget is not working
# if you want to apply styles (neither on Qt5 nor Qt6)
class TopBar:
    def __new__(cls, *args, **kwargs):
        instance = QtWidgets.QWidget(*args, **kwargs)
        instance.setFixedHeight(45)
        return instance


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


class TopBarToggleSwitch(QtWidgets.QWidget):
    """Toggle switch using existing MenuToggleIcon for consistent styling"""

    # Signal emitted when toggle state changes
    toggled = Signal(bool)

    def __init__(self, *args, initial_state: bool = False):
        super().__init__(*args)
        self.is_on = initial_state
        self.setFixedSize(40, 36)  # Match other topbar buttons
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setup_ui()
        self.update_state()

    def setup_ui(self):
        """Setup UI with MenuToggleIcon"""
        # Use horizontal layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create the toggle icon
        self.toggle_icon = MenuToggleIcon(self)
        layout.addWidget(self.toggle_icon)

        # Make the whole widget clickable
        self.mousePressEvent = self._on_click

    def _on_click(self, event):
        """Handle mouse click"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._toggle()

    def _toggle(self):
        """Toggle the switch state"""
        self.is_on = not self.is_on
        self.update_state()
        self.toggled.emit(self.is_on)

    def update_state(self):
        """Update the icon state"""
        # Check if widget has focus for proper icon display
        has_focus = self.hasFocus()
        self.toggle_icon.toggle(self.is_on, has_focus)

    def set_state(self, state: bool):
        """Set the toggle state programmatically"""
        if self.is_on != state:
            self._toggle()

    def get_state(self) -> bool:
        """Get current toggle state"""
        return self.is_on

    def focusInEvent(self, event):
        """Handle focus in event"""
        super().focusInEvent(event)
        self.update_state()

    def focusOutEvent(self, event):
        """Handle focus out event"""
        super().focusOutEvent(event)
        self.update_state()

    def keyPressEvent(self, event):
        """Handle key press for accessibility"""
        if event.key() in (QtCore.Qt.Key.Key_Space, QtCore.Qt.Key.Key_Return):
            self._toggle()
        else:
            super().keyPressEvent(event)


class TopBarLoadingIndicator(QtWidgets.QLabel):
    """Loading indicator for topbar - reusable animated spinner"""

    def __init__(self, *args):
        super().__init__(*args)
        self.is_loading = False
        self.setFixedSize(32, 32)
        self.setAlignment(QT_ALIGN_CENTER)
        self.setup_style()
        self.setup_animation()

    def setup_style(self):
        """Setup initial styling"""
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #00BCD4;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.setText("⏳")  # Initial hourglass icon

    def setup_animation(self):
        """Setup animation timer"""
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.animate)
        self.animation_frames = ["⏳", "⌛", "⏳", "⌛"]  # Hourglass animation
        self.current_frame = 0

    def start_loading(self):
        """Start the loading animation"""
        if not self.is_loading:
            self.is_loading = True
            self.setVisible(True)
            self.timer.start(800)  # Animate every 800ms
            self.animate()

    def stop_loading(self):
        """Stop the loading animation"""
        if self.is_loading:
            self.is_loading = False
            self.timer.stop()
            self.setVisible(False)

    def animate(self):
        """Animate the loading icon"""
        self.setText(self.animation_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
