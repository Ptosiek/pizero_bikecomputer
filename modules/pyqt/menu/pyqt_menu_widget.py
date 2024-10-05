from modules._pyqt import (
    QT_ALIGN_LEFT,
    QT_KEY_SPACE,
    QT_NO_FOCUS,
    QT_SCROLLBAR_ALWAYSOFF,
    QT_STRONG_FOCUS,
    QtCore,
    QtWidgets,
    Signal,
    qasync,
)
from modules.pyqt.components import icons, topbar

from .pyqt_menu_button import MenuButton

#################################
# Menu
#################################


class MenuWidget(QtWidgets.QWidget):
    config = None
    page_name = None
    back_index_key = None
    focus_widget = None

    buttons = None
    menu_layout = None

    @property
    def is_vertical(self):
        return self.parent().size().height() > self.parent().size().width()

    def __init__(self, parent, page_name, config):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.config = config
        self.page_name = page_name

        self.buttons = {}
        self.setup_ui()

    def setup_ui(self):
        self.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # top bar
        self.top_bar = topbar.TopBar()

        self.back_button = topbar.TopBarBackButton()
        self.page_name_label = topbar.TopBarLabel(self.page_name)

        self.top_bar_layout = QtWidgets.QHBoxLayout()
        self.top_bar_layout.setContentsMargins(5, 5, 5, 5)
        self.top_bar_layout.setSpacing(0)
        self.top_bar_layout.addWidget(self.back_button)
        self.top_bar_layout.addWidget(self.page_name_label)

        self.top_bar.setLayout(self.top_bar_layout)

        self.menu = QtWidgets.QWidget()
        self.setup_menu()

        layout.addWidget(self.top_bar)
        layout.addWidget(self.menu)

        # connect back button
        self.back_button.clicked.connect(self.back)
        self.connect_buttons()

    def make_menu_layout(self, qt_layout):
        self.menu_layout = qt_layout(self.menu)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(0)

    def add_buttons(self, buttons):
        n = len(buttons)
        vertical = self.is_vertical

        if n <= 4 or vertical:
            layout_type = QtWidgets.QVBoxLayout
        else:
            layout_type = QtWidgets.QGridLayout

        self.make_menu_layout(layout_type)

        i = 0
        for b in buttons:
            icon = None
            name, button_type, func, *rest = b
            if rest:
                icon = rest[0]

            self.buttons[name] = MenuButton(button_type, name, self.config, icon=icon)

            if func is not None:
                self.buttons[name].clicked.connect(func)
            else:
                self.buttons[name].setEnabled(False)
                self.buttons[name].setProperty("style", "unavailable")

            if layout_type == QtWidgets.QVBoxLayout:
                self.menu_layout.addWidget(self.buttons[name])
            else:
                self.menu_layout.addWidget(self.buttons[name], i % 4, i // 4)
                i += 1

        # add dummy button
        # TODO we should remove this but that's for later
        if not vertical and n in (1, 2, 3):
            for j in range(4 - n):
                self.menu_layout.addWidget(MenuButton("dummy", "", self.config))
        elif vertical:
            for j in range(self.menu_layout.count(), 8):
                self.menu_layout.addWidget(MenuButton("dummy", "", self.config))

        # set first focus
        if not self.config.display.has_touch:
            self.focus_widget = self.buttons[buttons[0][0]]

    def setup_menu(self):
        pass

    def resizeEvent(self, event):
        h = self.size().height()
        w = self.size().width()

        rows = 9 if h > w else 5
        short_side_length = min(h, w)

        self.top_bar.setFixedHeight(int(h / rows))

        q = self.page_name_label.font()
        q.setPixelSize(int(short_side_length / 12))
        self.page_name_label.setFont(q)

    def connect_buttons(self):
        pass

    def back(self):
        index = self.config.gui.gui_config.G_GUI_INDEX.get(self.back_index_key, 0)
        self.on_back_menu()
        self.config.gui.change_menu_page(index, focus_reset=False)

    def on_back_menu(self):
        pass

    def change_page(self, page, preprocess=False, **kwargs):
        # always set back index
        index = self.config.gui.gui_config.G_GUI_INDEX[page]
        widget = self.parentWidget().widget(index)
        widget.back_index_key = self.page_name

        if preprocess:
            widget.preprocess(**kwargs)
        self.config.gui.change_menu_page(index)
        return widget


class TopMenuWidget(MenuWidget):
    back_index_key = "Main"

    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, layout
            ("Sensors", "submenu", self.sensors_menu),
            ("Courses", "submenu", self.courses_menu),
            ("Upload Activity", "submenu", self.cloud_services_menu),
            ("Map", "submenu", self.map_menu),
            ("Profile", "submenu", self.profile_menu),
            ("System", "submenu", self.setting_menu),
        )
        self.add_buttons(button_conf)

    def sensors_menu(self):
        self.change_page("Sensors")

    def cloud_services_menu(self):
        self.change_page("Upload Activity")

    def courses_menu(self):
        self.change_page("Courses", preprocess=True)

    def map_menu(self):
        self.change_page("Map")

    def profile_menu(self):
        self.change_page("Profile")

    def setting_menu(self):
        self.change_page("System")


class ListWidget(MenuWidget):
    STYLES = """
      background-color: transparent;
    """

    list_type = None
    selected_item = None
    size_hint = None

    # for simple list
    settings = None

    def setup_menu(self):
        self.make_menu_layout(QtWidgets.QVBoxLayout)

        self.list = QtWidgets.QListWidget()
        self.list.setHorizontalScrollBarPolicy(QT_SCROLLBAR_ALWAYSOFF)
        self.list.setVerticalScrollBarPolicy(QT_SCROLLBAR_ALWAYSOFF)
        self.list.setFocusPolicy(QT_NO_FOCUS)
        self.list.setStyleSheet(self.STYLES)

        self.menu_layout.addWidget(self.list)

        if self.settings and self.settings.keys():
            for k in self.settings.keys():
                item = ListItemWidget(self, k)
                item.enter_signal.connect(self.button_func)
                self.add_list_item(item)

    # override for custom list
    def connect_buttons(self):
        self.list.itemSelectionChanged.connect(self.changed_item)
        self.list.itemClicked.connect(self.button_func)

    @qasync.asyncSlot()
    async def button_func(self):
        await self.button_func_extra()
        self.back()

    async def button_func_extra(self):
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
        self.preprocess_extra()

    # override for custom list
    def preprocess_extra(self):
        # set default item in the list
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


class ListDetailLabel(QtWidgets.QLabel):
    @property
    def STYLES(self):
        return f"""
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

    def __init__(self, parent, title, detail=None):
        self.title = title
        self.detail = detail
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.setup_ui()

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


class UploadActivityMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, icon
            (
                "Ride with GPS",
                "cloud_upload",
                self.rwgps_upload,
                (
                    icons.RideWithGPSIcon(),
                    (icons.BASE_LOGO_SIZE * 4, icons.BASE_LOGO_SIZE),
                ),
            ),
        )
        self.add_buttons(button_conf)

    @qasync.asyncSlot()
    async def rwgps_upload(self):
        await self.buttons["Ride with GPS"].run(self.config.api.rwgps.upload)
