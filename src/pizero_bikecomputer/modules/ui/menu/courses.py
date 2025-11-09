import shutil
from collections import namedtuple

from PIL import Image, ImageEnhance, ImageQt

from pizero_bikecomputer.modules._pyqt import (
    QT_ALIGN_CENTER,
    QtCore,
    QtGui,
    QtWidgets,
    qasync,
)
from pizero_bikecomputer.modules.constants import MenuLabel
from pizero_bikecomputer.modules.settings import settings
from pizero_bikecomputer.modules.utils.formatter import Altitude, Distance
from pizero_bikecomputer.modules.utils.network import detect_network

from ..components import icons, topbar
from ..widgets.item import Item
from .base import (
    BaseWidget,
    ListItemWidget,
    ListWidget,
    MenuItem,
    MenuType,
    MenuWidget,
)

SimpleItemConfig = namedtuple("SimpleItemConfig", ("label", "formatter"))


class CourseMenuWidget(MenuWidget):
    def get_menu_items(self):
        return [
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.LOCAL_STORAGE,
                action=self.load_local_courses,
                icon="📍",
            ),
            MenuItem(
                type=MenuType.MENU,
                name=MenuLabel.RIDE_WITH_GPS,
                action=self.load_rwgps_courses,
                icon=icons.RideWithGPSIcon(),
            ),
            MenuItem(
                type=MenuType.DIALOG,
                name=MenuLabel.CANCEL_COURSE,
                action=lambda: self.show_dialog(
                    self.cancel_course, MenuLabel.CANCEL_COURSE
                ),
                icon="❌",
            ),
        ]

    def preprocess(self):
        self.set_cancel_button_state()

    @qasync.asyncSlot()
    async def load_local_courses(self):
        widget = self.change_page(
            MenuLabel.COURSES_LIST,
            reset=True,
            list_type=MenuLabel.LOCAL_STORAGE,
        )
        await widget.list_local_courses()

    @qasync.asyncSlot()
    async def load_rwgps_courses(self):
        widget = self.change_page(
            MenuLabel.COURSES_LIST,
            reset=True,
            list_type=MenuLabel.RIDE_WITH_GPS,
        )
        await widget.list_ride_with_gps(reset=True)

    def set_cancel_button_state(self):
        self.menu_items[MenuLabel.CANCEL_COURSE].set_state(
            self.config.logger.course.is_set
        )

    def cancel_course(self):
        self.config.logger.reset_course(delete_course_file=True)
        self.set_cancel_button_state()

    def set_new_course(self, course_file):
        self.config.logger.set_new_course(course_file)
        self.config.gui.init_course()
        self.set_cancel_button_state()

    async def load_tcx_route(self, filename):
        self.cancel_course()
        course_file = (
            settings.COURSE_DIR / filename[: filename.lower().find(".tcx") + 4]
        )
        shutil.move(settings.COURSE_DIR / filename, course_file)
        self.set_new_course(course_file)
        self.config.gui.show_forced_message("Loading succeeded!")


class CourseListWidget(ListWidget):
    def setup_ui(self):
        super().setup_ui()
        self.vertical_scrollbar = self.list.verticalScrollBar()
        self.vertical_scrollbar.valueChanged.connect(self.detect_bottom)

        self.loading_indicator = topbar.TopBarLoadingIndicator()
        self.loading_indicator.setVisible(False)
        self.top_bar_layout.addWidget(self.loading_indicator)

    @qasync.asyncSlot(int)
    async def detect_bottom(self, value):
        if (
            self.list_type == MenuLabel.RIDE_WITH_GPS
            and value == self.vertical_scrollbar.maximum()
        ):
            self.loading_indicator.start_loading()
            await self.list_ride_with_gps()
            self.loading_indicator.stop_loading()

    @qasync.asyncSlot()
    async def _on_click(self):
        if self.list_type == MenuLabel.LOCAL_STORAGE:
            self.set_course()
        elif self.list_type == MenuLabel.RIDE_WITH_GPS:
            await self.change_course_detail_page()

    @qasync.asyncSlot()
    async def change_course_detail_page(self):
        if self.selected_item is None:
            return

        widget = self.change_page(
            MenuLabel.COURSE_DETAIL,
            course_info=self.selected_item.list_info,
        )
        await widget.load_images()

    async def list_local_courses(self):
        courses = self.config.get_courses()
        for c in courses:
            course_item = CourseListItemWidget(self, self.list_type, c)
            self.add_list_item(course_item)

    async def list_ride_with_gps(self, reset=False):
        self.loading_indicator.start_loading()
        courses = await self.config.api.rwgps.list_routes(reset)

        for c in reversed(courses or []):
            course_item = CourseListItemWidget(self, self.list_type, c)
            self.add_list_item(course_item)

        self.loading_indicator.stop_loading()

    def set_course(self, course_file=None):
        if self.selected_item is None:
            return

        # from Local Storage (self.list)
        if course_file is None:
            self.course_file = self.selected_item.list_info["path"]
        # from Ride with GPS (CourseDetailWidget)
        else:
            self.course_file = course_file

        # exist course: cancel and set new course
        if self.config.logger.course.is_set:
            self.config.gui.show_dialog(
                self.cancel_and_set_new_course, "Replace this course?"
            )
        else:
            self.config.gui.show_dialog(self.set_new_course, "Set this course?")

    def cancel_and_set_new_course(self):
        self.parentWidget().findChild(
            QtWidgets.QWidget, MenuLabel.COURSES
        ).cancel_course()
        self.set_new_course()

    def set_new_course(self):
        self.parentWidget().findChild(
            QtWidgets.QWidget, MenuLabel.COURSES
        ).set_new_course(self.course_file)
        self.back()


class CourseListItemWidget(ListItemWidget):
    list_info = None
    list_type = None
    locality_text = ", {elevation_gain:.0f}m up, {locality}, {administrative_area}"

    def __init__(self, parent, list_type, list_info):
        self.list_type = list_type
        self.list_info = list_info.copy()

        if self.list_type == "Ride with GPS":
            detail = ("{:.1f}km" + self.locality_text).format(
                self.list_info["distance"] / 1000,
                **self.list_info,
            )
        else:
            detail = None

        super().__init__(parent=parent, title=list_info["name"], detail=detail)

        if self.list_type == "Local Storage":
            self.enter_signal.connect(parent.set_course)
        elif self.list_type == "Ride with GPS":
            self.enter_signal.connect(parent.change_course_detail_page)

    def setup_ui(self):
        super().setup_ui()
        right_icon = icons.CourseRightIcon()
        self.outer_layout.setContentsMargins(0, 0, right_icon.margin, 0)
        self.outer_layout.addStretch()
        self.outer_layout.addWidget(right_icon)


class CourseDetailWidget(BaseWidget):
    list_id = None

    map_image_size = None
    profile_image_size = None
    next_button = None
    font_size = 20

    def __init__(self, parent, page_name, config):
        super().__init__(parent, page_name, config)
        self.setup_ui()

    def setup_ui(self):
        super().setup_ui()
        widget = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(widget)

        self.map_image = QtWidgets.QLabel()
        self.map_image.setAlignment(QT_ALIGN_CENTER)

        self.profile_image = QtWidgets.QLabel()
        self.profile_image.setAlignment(QT_ALIGN_CENTER)

        self.set_font_size()

        self.distance_item = Item(
            config=SimpleItemConfig("Distance", Distance),
            font_size=20,
            right_flag=True,
            bottom_flag=False,
        )
        self.ascent_item = Item(
            config=SimpleItemConfig("Ascent", Altitude),
            font_size=20,
            right_flag=True,
            bottom_flag=False,
        )

        outer_layout = QtWidgets.QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        if not self.is_vertical:
            info_layout = QtWidgets.QVBoxLayout()
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(0)

            info_layout.addLayout(self.distance_item)
            info_layout.addLayout(self.ascent_item)

            outer_layout.addWidget(self.map_image)
            outer_layout.addLayout(info_layout)

        else:
            layout.addWidget(self.map_image)
            outer_layout.addLayout(self.distance_item)
            outer_layout.addLayout(self.ascent_item)

        layout.addLayout(outer_layout)
        layout.addWidget(self.profile_image)

        # update panel for every 1 seconds
        self.timer = QtCore.QTimer(parent=self)
        self.timer.timeout.connect(self.update_display)

        # also set extra button for topbar
        self.next_button = topbar.TopBarNextButton()
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.set_course)

        self.top_bar_layout.addWidget(self.next_button)

        self.layout.addWidget(widget)

    def enable_next_button(self):
        self.next_button.setVisible(True)
        self.next_button.setEnabled(True)

    def preprocess(self, course_info):
        # reset
        self.list_id = None

        self.map_image.clear()
        self.profile_image.clear()
        self.next_button.setVisible(False)
        self.next_button.setEnabled(False)

        self.distance_item.update_value(course_info["distance"])
        self.ascent_item.update_value(course_info["elevation_gain"])

        self.list_id = course_info["id"]

        self.timer.start(settings.DRAW_INTERVAL)

    async def load_images(self):
        if self.check_all_image_and_draw():
            self.timer.stop()
        else:
            # 1st download
            await self.config.api.rwgps.get_route_files(self.list_id)

    def back(self):
        self.timer.stop()
        super().back()

    @qasync.asyncSlot()
    async def update_display(self):
        if self.check_all_image_and_draw():
            self.timer.stop()
            return

        # 1st download check
        if self.config.api.rwgps.check_files(self.list_id, True):
            self.draw_images(draw_map_image=True, draw_profile_image=False)
            # download files with privacy code (2nd download)
            await self.config.api.rwgps.get_route_files(
                self.list_id, with_privacy_code=True
            )

    def check_all_image_and_draw(self):
        # if all files exists, reload images and buttons, stop timer and exit
        all_downloaded = self.config.api.rwgps.check_files(self.list_id)

        if all_downloaded:
            res = self.draw_images()
            self.enable_next_button()
            return res

        # if no internet connection, stop timer and exit
        elif not detect_network():
            return True
        return False

    def set_course(self):
        widget = self.parentWidget().findChild(
            QtWidgets.QWidget, MenuLabel.COURSES_LIST
        )
        widget.set_course(
            settings.RWGS_ROUTE_DOWNLOAD_DIR / f"course-{self.list_id}.tcx"
        )

    def draw_images(self, draw_map_image=True, draw_profile_image=True):
        if self.list_id is None:
            return False

        if draw_map_image:
            filename = settings.RWGS_ROUTE_DOWNLOAD_DIR / f"preview-{self.list_id}.png"

            if not filename.exists():
                return

            im = Image.open(filename).convert("RGBA")
            im = ImageEnhance.Contrast(im).enhance(2.0)

            if self.map_image_size is None:
                self.map_image_size = Image.open(filename).size  # tuple (w, h)
            if self.map_image_size[0] == 0 or self.map_image_size[1] == 0:
                return False

            ratio = 1 if self.is_vertical else 0.5

            scale = (self.size().width() * ratio) / self.map_image_size[0]
            im = im.resize(
                (
                    int(self.map_image_size[0] * scale),
                    int(self.map_image_size[1] * scale),
                )
            )
            self.map_image.setPixmap(QtGui.QPixmap.fromImage(ImageQt.ImageQt(im)))

        if draw_profile_image:
            filename = (
                settings.RWGS_ROUTE_DOWNLOAD_DIR
                / f"elevation_profile-{self.list_id}.jpg"
            )

            im = Image.open(filename).convert("RGBA")
            if self.profile_image_size is None:
                self.profile_image_size = Image.open(filename).size  # tuple (w, h)
            if self.profile_image_size[0] == 0 or self.profile_image_size[1] == 0:
                return False

            scale = self.size().width() / self.profile_image_size[0]
            im = im.resize(
                (
                    int(self.profile_image_size[0] * scale),
                    int(self.profile_image_size[1] * scale),
                )
            )
            self.profile_image.setPixmap(QtGui.QPixmap.fromImage(ImageQt.ImageQt(im)))

        return True

    def set_font_size(self, init=False):
        if init:
            self.font_size = int(min(self.config.display.resolution) / 10)
        else:
            self.font_size = int(min(self.size().width(), self.size().height()) / 10)

    def resizeEvent(self, event):
        self.set_font_size(event.oldSize() == QtCore.QSize(-1, -1))
        for i in [self.distance_item, self.ascent_item]:
            i.update_font_size(self.font_size)

        return super().resizeEvent(event)
