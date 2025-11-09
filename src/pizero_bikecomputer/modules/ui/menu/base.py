from dataclasses import dataclass
from enum import Enum
from importlib import resources
from typing import Callable, Literal

from pizero_bikecomputer.logger import app_logger
from pizero_bikecomputer.modules._pyqt import (
    QT_ALIGN_CENTER,
    QT_ALIGN_LEFT,
    QT_EXPANDING,
    QT_KEY_SPACE,
    QT_NO_FOCUS,
    QT_SCROLLBAR_ALWAYSOFF,
    QT_STRONG_FOCUS,
    QtCore,
    QtGui,
    QtWidgets,
    Signal,
    Slot,
    qasync,
)

from ..components import icons, topbar
from ..themes import ThemeManager

BASE_DIR = resources.files("pizero_bikecomputer.img")

#################################
# Menu
#################################


class MenuType(Enum):
    DIALOG = 0
    MENU = 1
    TOGGLE = 2
    UPLOAD = 3
    TASK = 4


@dataclass
class MenuItem:
    type: MenuType
    name: str
    action: Callable | None = None
    icon: str | QtGui.QIcon = None


class MenuItemWidget(QtWidgets.QPushButton):
    config = None
    menu_item = None
    status = False

    # Icon states
    original_icon = None
    loading_movie = None
    success_icon = None
    fail_icon = None
    current_state: Literal["loading", "success", "fail"] | None = None

    def __init__(self, config, menu_item: MenuItem):
        # if icon is passed, no text is used
        super().__init__()

        self.config = config
        self.menu_item = menu_item
        self.theme_manager = ThemeManager()

        self.setup_ui()
        self.setup_style()
        self.connect_signals()

    def setup_ui(self):
        """Setup menu item UI as a square tile"""
        # For 4 tiles in 340x200:
        # Each tile gets ~85x100 (including spacing)
        # Target square tile: 70x70 with minimal spacing
        self.setMinimumSize(70, 70)
        self.setMaximumSize(80, 80)
        self.setSizePolicy(QT_EXPANDING, QT_EXPANDING)

        # Create compact square tile layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.setAlignment(QT_ALIGN_CENTER)

        # Handle toggle button type with MenuToggleIcon
        if self.menu_item.type == MenuType.TOGGLE:
            self.toggle_icon = icons.MenuToggleIcon()
            self.toggle_icon.setParent(self)
            self.toggle_icon.toggle(self.status, self.hasFocus())
            layout.addWidget(self.toggle_icon, 0, QT_ALIGN_CENTER)
            self.icon_label = None  # Don't use regular icon for toggles
        else:
            # Regular icon label - smaller
            self.icon_label = QtWidgets.QLabel()
            self.icon_label.setAlignment(QT_ALIGN_CENTER)
            self.icon_label.setFixedHeight(30)
            layout.addWidget(self.icon_label)
            self.toggle_icon = None  # No toggle icon for non-toggle items

        # Title label - smaller, word wrapped
        self.title_label = QtWidgets.QLabel(self.menu_item.name)
        self.title_label.setAlignment(QT_ALIGN_CENTER)
        self.title_label.setWordWrap(True)
        self.title_label.setFixedHeight(28)
        layout.addWidget(self.title_label)

        layout.addStretch()

    def setup_style(self):
        """Apply theme-based styling for tile"""
        theme = self.theme_manager.get_theme()

        # Tile style
        style = f"""
                QWidget {{
                    background-color: transparent;
                }}
                MenuItemWidget {{
                    background-color: {theme.colors["surface"]};
                    border: 1px solid {theme.colors["border"]};
                    border-radius: 12px;
                    color: {theme.colors["on_surface"]};
                    font-size: 12px;
                    font-weight: 600;
                }}
                MenuItemWidget:hover {{
                    background-color: {theme.colors["surface_variant"]};
                    border: 2px solid {theme.colors["primary"]};
                }}
                MenuItemWidget:pressed {{
                    background-color: {theme.colors["primary_container"]};
                }}
                MenuItemWidget:disabled {{
                    background-color: {theme.colors["surface_variant"]};
                    color: {theme.colors["on_surface_variant"]};
                    border: 1px solid {theme.colors["divider"]};
                }}
            """

        self.setStyleSheet(style)

        # Set icon - skip for toggle buttons
        if self.menu_item.icon and self.icon_label is not None:
            if isinstance(self.menu_item.icon, str):
                self.icon_label.setText(self.menu_item.icon)
                self.icon_label.setStyleSheet(
                    f"font-size: 18px; color: {theme.colors['primary']};"
                )
                # Save original text icon
                self.original_icon = self.menu_item.icon
            else:
                pixmap = self.menu_item.icon.pixmap(24, 24)
                self.icon_label.setPixmap(pixmap)
                # Save original pixmap icon
                self.original_icon = pixmap

        # Initialize success/fail icons
        self.success_icon = QtGui.QIcon(str(BASE_DIR / "cloud_upload_done.svg"))
        self.fail_icon = QtGui.QIcon(str(BASE_DIR / "button_warning.svg"))

        # Configure title style - smaller font
        self.title_label.setStyleSheet(f"""
                color: {theme.colors["on_surface"]};
                font-size: 9px;
                font-weight: 600;
            """)

    def connect_signals(self):
        # connect_signals
        if self.menu_item.action:
            self.clicked.connect(self.menu_item.action)
        else:
            self.setEnabled(False)
            self.setProperty("style", "unavailable")

    def set_state(self, state: bool):
        if state:
            self.enable()
        else:
            self.disable()

    def disable(self):
        self.setEnabled(False)
        self.setProperty("style", "unavailable")

    def enable(self):
        self.setEnabled(True)
        self.setProperty("style", None)

    def resizeEvent(self, event):
        short_side_length = min(self.size().height(), self.size().width())

        if short_side_length < 3:
            return

        q = self.font()
        q.setPixelSize(int(short_side_length / 2.5))
        self.setFont(q)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        # Update toggle icon when focus changes
        if self.menu_item.type == MenuType.TOGGLE and self.toggle_icon is not None:
            self.toggle_icon.toggle(self.status, True)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        # Update toggle icon when focus changes
        if self.menu_item.type == MenuType.TOGGLE and self.toggle_icon is not None:
            self.toggle_icon.toggle(self.status, False)

    def change_toggle(self, status):
        self.status = status

        # Handle toggle icon implementation
        if hasattr(self, "toggle_icon") and self.toggle_icon is not None:
            self.toggle_icon.toggle(status, self.hasFocus())

    @Slot()
    def loading_start(self):
        """Show loading animation, replacing the main icon"""
        if not self.status and self.icon_label is not None:
            self.status = True
            self.current_state = "loading"

            # Create loading movie if not exists
            if self.loading_movie is None:
                self.loading_movie = QtGui.QMovie(self)
                self.loading_movie.setFileName(str(BASE_DIR / "loading.gif"))
                self.loading_movie.frameChanged.connect(self.on_loading_frame_changed)

            # Start loading animation
            self.loading_movie.start()

    @Slot()
    def loading_stop(self, success: bool):
        """Stop loading and show success/fail icon"""
        if self.status and self.icon_label is not None:
            self.status = False

            # Stop loading animation
            if self.loading_movie:
                self.loading_movie.stop()

            # Show success or fail icon
            if success:
                self.current_state = "success"
                if isinstance(self.original_icon, str):
                    self.icon_label.setText("✓")  # Checkmark for text icons
                    self.icon_label.setStyleSheet("font-size: 20px; color: #4CAF50;")
                else:
                    self.icon_label.setPixmap(self.success_icon.pixmap(24, 24))
            else:
                self.current_state = "fail"
                if isinstance(self.original_icon, str):
                    self.icon_label.setText("✗")  # X mark for text icons
                    self.icon_label.setStyleSheet("font-size: 20px; color: #F44336;")
                else:
                    self.icon_label.setPixmap(self.fail_icon.pixmap(24, 24))

    def on_loading_frame_changed(self, frameNumber):
        """Update icon with current loading frame"""
        if self.status and self.loading_movie and self.icon_label is not None:
            current_pixmap = self.loading_movie.currentPixmap()
            if not current_pixmap.isNull():
                self.icon_label.setPixmap(current_pixmap.scaled(24, 24))

    def reset_icon(self):
        """Reset icon to original state"""
        if self.icon_label is not None and self.original_icon is not None:
            self.current_state = None

            # Stop any ongoing loading animation
            if self.loading_movie:
                self.loading_movie.stop()

            # Restore original icon
            if isinstance(self.original_icon, str):
                self.icon_label.setText(self.original_icon)
                theme = self.theme_manager.get_theme()
                self.icon_label.setStyleSheet(
                    f"font-size: 18px; color: {theme.colors['primary']};"
                )
            else:
                self.icon_label.setPixmap(self.original_icon)

    async def run(self, func):
        """Run async function with loading animation and result display"""
        if self.status:
            return

        self.loading_start()

        try:
            result = await func()
            self.loading_stop(result)
        except Exception as e:
            app_logger.exception(e)
            self.loading_stop(False)

    def focusOutEvent(self, event):
        """Reset icon when user moves away from the menu item"""
        super().focusOutEvent(event)
        # Only reset if we're not currently loading
        if self.current_state is not None:
            self.reset_icon()


class BaseWidget(QtWidgets.QWidget):
    config = None
    page_name = None
    back_index = None
    focus_widget = None

    layout = None

    def __init__(self, parent, page_name, config):
        QtWidgets.QWidget.__init__(self, parent=parent, objectName=page_name)
        self.config = config
        self.page_name = page_name

    @property
    def is_vertical(self):
        return self.parent().size().height() > self.parent().size().width()

    def back(self):
        self.config.gui.change_menu_page(self.back_index, focus_reset=False)

    def change_page(self, page, **kwargs):
        # always set back index
        parent = self.parentWidget()
        widget = parent.findChild(QtWidgets.QWidget, page)
        widget.back_index = parent.indexOf(self)

        if hasattr(widget, "preprocess"):
            widget.preprocess(**kwargs)

        self.config.gui.change_menu_page(parent.indexOf(widget))
        return widget

    def show_dialog(self, fn, title):
        return self.config.gui.show_dialog(fn, title)

    def setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # top bar
        self.top_bar = topbar.TopBar()

        self.back_button = topbar.TopBarBackButton()

        self.top_bar_layout = QtWidgets.QHBoxLayout()
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(0)
        self.top_bar_layout.addWidget(self.back_button)
        self.top_bar_layout.addStretch()

        self.top_bar.setLayout(self.top_bar_layout)

        # connect back button
        self.back_button.clicked.connect(self.back)

        self.layout.addWidget(self.top_bar)


class MenuWidget(BaseWidget):
    menu_items: dict[str, MenuItemWidget] | None = None

    def __init__(self, parent, page_name, config):
        super().__init__(parent, page_name, config)

        self.menu_items = {}
        self.theme_manager = ThemeManager()

        # Grid configuration - optimized for small screens
        self.min_tile_size = 70
        self.max_tile_size = 80
        self.tile_spacing = 8
        self.grid_columns = self._calculate_optimal_columns()

        # Animation
        self.animation_duration = 300
        self.slide_animation = QtCore.QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(self.animation_duration)
        self.slide_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)

        self.setup_ui()
        self.setup_style()
        self.load_menu_items()

    def _calculate_optimal_columns(self) -> int:
        """Calculate optimal number of columns based on screen width"""
        available_width = self.width() if self.width() > 0 else 340
        # Account for margins and padding
        usable_width = available_width - 32  # 16px margins on each side

        # Calculate columns based on tile size (70px min + 8px spacing)
        columns = max(1, usable_width // (self.min_tile_size + self.tile_spacing))
        return min(columns, 4)  # Cap at 4 columns for usability

    def setup_ui(self):
        super().setup_ui()

        # Menu content with grid layout
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.menu_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.menu_container)
        self.grid_layout.setContentsMargins(12, 12, 12, 12)
        self.grid_layout.setSpacing(self.tile_spacing)

        self.scroll_area.setWidget(self.menu_container)
        self.layout.addWidget(self.scroll_area)

    def setup_style(self):
        """Apply theme-based styling"""
        theme = self.theme_manager.get_theme()
        self.setStyleSheet(f"""
            MenuWidget {{
                background-color: {theme.colors["background"]};
            }}
            QScrollArea {{
                background-color: transparent;
            }}
            #back_button {{
                background-color: {theme.colors["surface"]};
                border: none;
                border-radius: 6px;
                color: {theme.colors["on_surface"]};
                padding: 8px 16px;
                font-size: 14px;
            }}
            #back_button:hover {{
                background-color: {theme.colors["surface_variant"]};
            }}
        """)

    def get_menu_items(self) -> list[MenuItem]:
        return []
        # raise NotImplementedError

    def load_menu_items(self):
        self.menu_items = {
            x.name: MenuItemWidget(self.config, x) for x in self.get_menu_items()
        }

    def render_menu_items(self):
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        # Add new items in grid format
        for i, item_widget in enumerate(self.menu_items.values()):
            try:
                # Calculate grid position
                row = i // self.grid_columns
                col = i % self.grid_columns

                self.grid_layout.addWidget(item_widget, row, col)
            except Exception as e:
                print(f"Error creating menu item {i}: {e}")
                import traceback

                traceback.print_exc()

        # Add vertical stretch at the bottom to push content up
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)

    def resizeEvent(self, event):
        """Handle window resize and adjust grid columns"""
        super().resizeEvent(event)
        new_columns = self._calculate_optimal_columns()

        if new_columns != self.grid_columns:
            self.grid_columns = new_columns
            self.render_menu_items()

        # n = len(menu_items)
        # vertical = self.is_vertical
        #
        # if n <= 4 or vertical:
        #     layout_type = QtWidgets.QVBoxLayout
        # else:
        #     layout_type = QtWidgets.QGridLayout
        #
        # self.make_menu_layout(layout_type)
        #
        # i = 0
        #
        # for idx, item in enumerate(menu_items):
        #     widget = MenuItemWidget(self.config, item)
        #
        #     if layout_type == QtWidgets.QVBoxLayout:
        #         self.menu_layout.addWidget(widget)
        #     else:
        #         self.menu_layout.addWidget(widget, i % 4, i // 4)
        #         i += 1
        #
        #     # set first focus
        #     if not self.config.display.has_touch and not idx:
        #         self.focus_widget = widget
        #
        #     self.menu_items[item.name] = widget

    def setup_menu(self):
        """Subclasses must implement this method"""
        raise NotImplementedError("Subclasses must implement setup_menu()")


#################################
# List
#################################


class ListDetailLabel(QtWidgets.QLabel):
    @property
    def STYLES(self):
        return """
          border-bottom: 1px solid #AAAAAA;
          padding-bottom: 2%;
          padding-left: 20%;
        """

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setMargin(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(self.STYLES)


class ListTitleLabel(QtWidgets.QLabel):
    @property
    def STYLES(self):
        border_style = "border-bottom: 1px solid #AAAAAA;" if self.with_border else ""
        return f"""
          {border_style}
          padding-left: 10%;
          padding-top: 2%;
        """

    def __init__(self, with_border=False, *__args):
        self.with_border = with_border
        super().__init__(*__args)
        self.setMargin(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(self.STYLES)


class ListItemWidget(QtWidgets.QWidget):
    enter_signal = Signal()
    title = ""
    detail = ""

    @property
    def STYLES(self):
        return """
        QWidget {
            background-color: transparent;
        }
        """

    def __init__(self, parent, title, detail=None):
        self.title = title
        self.detail = detail
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.setup_ui()
        self.setStyleSheet(self.STYLES)

    def setup_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(QT_STRONG_FOCUS)

        inner_layout = QtWidgets.QVBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        self.title_label = ListTitleLabel(with_border=not self.detail)
        self.title_label.setText(self.title)
        inner_layout.addWidget(self.title_label)

        if self.detail:
            self.detail_label = ListDetailLabel()
            self.detail_label.setText(self.detail)
            inner_layout.addWidget(self.detail_label)

        self.outer_layout = QtWidgets.QHBoxLayout(self)
        self.outer_layout.setSpacing(0)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)

        self.outer_layout.addLayout(inner_layout, QT_ALIGN_LEFT)

    def keyPressEvent(self, e):
        if e.key() == QT_KEY_SPACE:
            self.enter_signal.emit()

    @staticmethod
    def resize_label(label, font_size):
        q = label.font()
        q.setPixelSize(font_size)
        label.setFont(q)

    def resizeEvent(self, event):
        short_side_length = min(self.size().height(), self.size().width())
        self.resize_label(self.title_label, int(short_side_length * 0.45))

        if self.detail:
            self.resize_label(self.detail_label, int(short_side_length * 0.4))


class ListWidget(BaseWidget):
    list_type = None
    selected_item = None
    size_hint = None

    # for simple list
    settings = None

    def __init__(self, parent, page_name, config):
        super().__init__(parent, page_name, config)
        self.setup_ui()

    def setup_ui(self):
        super().setup_ui()

        self.list = QtWidgets.QListWidget()
        self.list.setHorizontalScrollBarPolicy(QT_SCROLLBAR_ALWAYSOFF)
        self.list.setVerticalScrollBarPolicy(QT_SCROLLBAR_ALWAYSOFF)
        self.list.setFocusPolicy(QT_NO_FOCUS)

        self.layout.addWidget(self.list)

        if self.settings and self.settings.keys():
            for k in self.settings.keys():
                item = ListItemWidget(self, k)
                item.enter_signal.connect(self._on_click)
                self.add_list_item(item)

        self.list.itemSelectionChanged.connect(self.changed_item)
        self.list.itemClicked.connect(self._on_click)

    @qasync.asyncSlot()
    async def _on_click(self):
        await self.on_click()
        self.back()

    async def on_click(self):
        pass

    def changed_item(self):
        # item is QListWidgetItem
        item = self.list.selectedItems()
        if len(item):
            self.selected_item = self.list.itemWidget(item[0])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rows = 8 if self.is_vertical else 4
        h = int((self.height() - self.top_bar.height()) / rows)
        self.size_hint = QtCore.QSize(self.top_bar.width(), h)
        for i in range(self.list.count()):
            self.list.item(i).setSizeHint(self.size_hint)

    def preprocess(self, **kwargs):
        self.list_type = kwargs.get("list_type")
        reset = kwargs.get("reset", False)

        if reset:
            self.selected_item = None
            self.list.clear()
            self.list.verticalScrollBar().setValue(0)

        if self.settings:
            default_value = self.get_default_value()
            default_index = None

            for i, k in enumerate(self.settings):
                if k == default_value:
                    default_index = i
                    break
            if default_index is not None:
                self.list.setCurrentRow(default_index)
                self.list.itemWidget(self.list.currentItem()).setFocus()

    def get_default_value(self):
        return None

    def add_list_item(self, item):
        list_item = QtWidgets.QListWidgetItem(self.list)
        if self.size_hint:
            list_item.setSizeHint(self.size_hint)
        self.list.setItemWidget(list_item, item)
