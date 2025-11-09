"""
Modern themes and styling system for bike computer
"""

from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont


class Theme:
    """Theme definition with colors, fonts, and styles"""

    def __init__(self, name: str, colors: dict, fonts: dict):
        self.name = name
        self.colors = colors
        self.fonts = fonts


class ThemeType(Enum):
    DARK = "dark"
    LIGHT = "light"
    HIGH_CONTRAST = "high_contrast"
    OUTDOOR = "outdoor"


# Predefined modern themes
THEMES = {
    ThemeType.DARK: Theme(
        "Dark Modern",
        colors={
            # Background colors
            "background": "#0A0A0A",
            "surface": "#1A1A1A",
            "surface_variant": "#2A2A2A",
            "card": "#252525",
            # Text colors
            "on_background": "#FFFFFF",
            "on_surface": "#FFFFFF",
            "on_surface_variant": "#B0B0B0",
            "on_card": "#FFFFFF",
            # Primary colors
            "primary": "#00BCD4",
            "primary_container": "#008BA3",
            "on_primary": "#FFFFFF",
            "on_primary_container": "#FFFFFF",
            # Secondary colors
            "secondary": "#FF4081",
            "secondary_container": "#C60055",
            "on_secondary": "#FFFFFF",
            "on_secondary_container": "#FFFFFF",
            # Status colors
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336",
            "info": "#2196F3",
            # Data field colors
            "speed_color": "#00E676",
            "heart_rate_color": "#FF5252",
            "power_color": "#FFD740",
            "cadence_color": "#7C4DFF",
            "altitude_color": "#64FFDA",
            # Border and accent
            "border": "#333333",
            "border_active": "#00BCD4",
            "shadow": "#000000",
            "divider": "#2A2A2A",
            # Map colors
            "map_background": "#1E1E1E",
            "map_road": "#4A4A4A",
            "map_route": "#00BCD4",
            "map_trail": "#795548",
            "map_water": "#0277BD",
        },
        fonts={
            "display": QFont("Inter", 32, QFont.Weight.Bold),
            "headline": QFont("Inter", 24, QFont.Weight.Bold),
            "title": QFont("Inter", 20, QFont.Weight.Bold),
            "body_large": QFont("Inter", 16, QFont.Weight.Medium),
            "body": QFont("Inter", 14, QFont.Weight.Normal),
            "body_small": QFont("Inter", 12, QFont.Weight.Normal),
            "data_field": QFont("Roboto Mono", 18, QFont.Weight.Bold),
            "data_field_large": QFont("Roboto Mono", 24, QFont.Weight.Bold),
            "data_field_small": QFont("Roboto Mono", 14, QFont.Weight.Medium),
            "label": QFont("Inter", 10, QFont.Weight.Medium),
            "button": QFont("Inter", 12, QFont.Weight.Medium),
            "status": QFont("Inter", 11, QFont.Weight.Normal),
        },
    ),
    ThemeType.OUTDOOR: Theme(
        "Outdoor Optimized",
        colors={
            # High contrast for sunlight visibility
            "background": "#000000",
            "surface": "#1A1A1A",
            "surface_variant": "#333333",
            "card": "#2A2A2A",
            # High contrast text
            "on_background": "#FFFFFF",
            "on_surface": "#FFFFFF",
            "on_surface_variant": "#E0E0E0",
            "on_card": "#FFFFFF",
            # Bright primary colors
            "primary": "#00E5FF",
            "primary_container": "#00ACC1",
            "on_primary": "#000000",
            "on_primary_container": "#FFFFFF",
            "secondary": "#FF6E40",
            "secondary_container": "#E64A19",
            "on_secondary": "#000000",
            "on_secondary_container": "#FFFFFF",
            # High contrast status
            "success": "#00E676",
            "warning": "#FFC107",
            "error": "#FF1744",
            "info": "#00B0FF",
            # Bright data field colors
            "speed_color": "#76FF03",
            "heart_rate_color": "#FF1744",
            "power_color": "#FFEA00",
            "cadence_color": "#E040FB",
            "altitude_color": "#1DE9B6",
            "border": "#404040",
            "border_active": "#00E5FF",
            "shadow": "#000000",
            "divider": "#333333",
            "map_background": "#000000",
            "map_road": "#FFFFFF",
            "map_route": "#00E5FF",
            "map_trail": "#FF6E40",
            "map_water": "#0277BD",
        },
        fonts={
            "display": QFont("Roboto Mono", 36, QFont.Weight.Bold),
            "headline": QFont("Inter", 28, QFont.Weight.Bold),
            "title": QFont("Inter", 22, QFont.Weight.Bold),
            "body_large": QFont("Inter", 18, QFont.Weight.Medium),
            "body": QFont("Inter", 16, QFont.Weight.Medium),
            "body_small": QFont("Inter", 13, QFont.Weight.Medium),
            "data_field": QFont("Roboto Mono", 20, QFont.Weight.Bold),
            "data_field_large": QFont("Roboto Mono", 28, QFont.Weight.Bold),
            "data_field_small": QFont("Roboto Mono", 16, QFont.Weight.Bold),
            "label": QFont("Inter", 11, QFont.Weight.Bold),
            "button": QFont("Inter", 13, QFont.Weight.Bold),
            "status": QFont("Inter", 12, QFont.Weight.Medium),
        },
    ),
}


class ThemeManager(QObject):
    """Manages themes and styling for the bike computer"""

    theme_changed = pyqtSignal(Theme)

    def __init__(self):
        super().__init__()
        self.current_theme = THEMES[ThemeType.DARK]

    def get_theme(self) -> Theme:
        """Get current theme"""
        return self.current_theme

    def set_theme(self, theme_type: ThemeType):
        """Set current theme"""
        self.current_theme = THEMES[theme_type]
        self.theme_changed.emit(self.current_theme)

    def get_color(self, color_name: str) -> str:
        """Get color by name from current theme"""
        return self.current_theme.colors.get(color_name, "#FFFFFF")

    def get_font(self, font_name: str) -> QFont:
        """Get font by name from current theme"""
        return self.current_theme.fonts.get(font_name, QFont())

    def generate_stylesheet(self, widget_type: str = "widget") -> str:
        """Generate stylesheet for widget type"""
        theme = self.current_theme

        if widget_type == "data_field":
            return f"""
                QWidget {{
                    background-color: {theme.colors["surface"]};
                    border: 2px solid {theme.colors["border"]};
                    border-radius: 8px;
                    color: {theme.colors["on_surface"]};
                }}
                QWidget:focus {{
                    border-color: {theme.colors["primary"]};
                }}
                QLabel {{
                    background-color: transparent;
                }}
            """
        elif widget_type == "button":
            return f"""
                QPushButton {{
                    background-color: {theme.colors["primary"]};
                    border: none;
                    border-radius: 6px;
                    color: {theme.colors["on_primary"]};
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {theme.colors["primary_container"]};
                }}
                QPushButton:pressed {{
                    background-color: {theme.colors["primary_container"]};
                }}
                QPushButton:disabled {{
                    background-color: {theme.colors["surface_variant"]};
                    color: {theme.colors["on_surface_variant"]};
                }}
            """
        elif widget_type == "status_bar":
            return f"""
                QWidget {{
                    background-color: {theme.colors["surface"]};
                    border-top: 1px solid {theme.colors["border"]};
                    color: {theme.colors["on_surface"]};
                }}
            """
        else:  # general widget
            return f"""
                QWidget {{
                    background-color: {theme.colors["background"]};
                    color: {theme.colors["on_background"]};
                }}
                QLabel {{
                    background-color: transparent;
                }}
            """

    def apply_theme_to_widget(self, widget, widget_type: str = "widget"):
        """Apply theme to a widget"""
        widget.setStyleSheet(self.generate_stylesheet(widget_type))

        # Apply fonts if applicable
        if widget_type == "data_field":
            # Data fields often have specific label/value widgets
            for child in widget.findChildren(object.__class__):
                if "value" in child.objectName().lower():
                    child.setFont(self.get_font("data_field"))
                elif "label" in child.objectName().lower():
                    child.setFont(self.get_font("label"))
