import asyncio
import os
import shutil

from modules._pyqt import (
    QT_ALIGN_CENTER,
    QtCore,
    QtWidgets,
    QtGui,
    qasync,
)
from modules.pyqt.components import icons, topbar
from modules.settings import settings
from modules.utils.network import detect_network
from .pyqt_menu_widget import (
    MenuWidget,
    ListWidget,
    ListItemWidget,
)


class CoursesMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, icon
            ("Local Storage", "submenu", self.load_local_courses),
            (
                "Ride with GPS",
                "submenu",
                self.load_rwgps_courses,
                (
                    icons.RideWithGPSIcon(),
                    (icons.BASE_LOGO_SIZE * 4, icons.BASE_LOGO_SIZE),
                ),
            ),
            (
                "Cancel Course",
                "dialog",
                lambda: self.config.gui.show_dialog(
                    self.cancel_course, "Cancel Course"
                ),
            ),
        )
        self.add_buttons(button_conf)

    def preprocess(self):
        self.onoff_course_cancel_button()

    @qasync.asyncSlot()
    async def load_local_courses(self):
        widget = self.change_page(
            "Courses List", preprocess=True, reset=True, list_type="Local Storage"
        )
        await widget.list_local_courses()

    @qasync.asyncSlot()
    async def load_rwgps_courses(self):
        widget = self.change_page(
            "Courses List", preprocess=True, reset=True, list_type="Ride with GPS"
        )
        await widget.list_ride_with_gps(reset=True)

    def onoff_course_cancel_button(self):
        status = self.config.logger.course.is_set
        self.buttons["Cancel Course"].onoff_button(status)

    def cancel_course(self):
        self.config.logger.reset_course(delete_course_file=True)
        self.onoff_course_cancel_button()

    async def load_tcx_route(self, filename):
        self.cancel_course()
        course_file = os.path.join(
            settings.COURSE_DIR, filename[: filename.lower().find(".tcx") + 4]
        )
        shutil.move(os.path.join(settings.COURSE_DIR, filename), course_file)
        self.set_new_course(course_file)
        self.config.gui.show_forced_message("Loading succeeded!")

    def set_new_course(self, course_file):
        self.config.logger.set_new_course(course_file)
        self.config.gui.init_course()
        self.onoff_course_cancel_button()


class CourseListWidget(ListWidget):
    def setup_menu(self):
        super().setup_menu()
        self.vertical_scrollbar = self.list.verticalScrollBar()
        self.vertical_scrollbar.valueChanged.connect(self.detect_bottom)

    @qasync.asyncSlot(int)
    async def detect_bottom(self, value):
        if (
            self.list_type == "Ride with GPS"
            and value == self.vertical_scrollbar.maximum()
        ):
            await self.list_ride_with_gps(add=True)

    @qasync.asyncSlot()
    async def button_func(self):
        if self.list_type == "Local Storage":
            self.set_course()
        elif self.list_type == "Ride with GPS":
            await self.change_course_detail_page()

    @qasync.asyncSlot()
    async def change_course_detail_page(self):
        if self.selected_item is None:
            return

        widget = self.change_page(
            "Course Detail",
            preprocess=True,
            course_info=self.selected_item.list_info,
        )
        await widget.load_images()

    def preprocess_extra(self):
        self.page_name_label.setText(self.list_type)

    async def list_local_courses(self):
        courses = self.config.get_courses()
        for c in courses:
            course_item = CourseListItemWidget(self, self.list_type, c)
            self.add_list_item(course_item)

    async def list_ride_with_gps(self, add=False, reset=False):
        courses = await self.config.api.get_ridewithgps_route(add, reset)

        for c in reversed(courses or []):
            course_item = CourseListItemWidget(self, self.list_type, c)
            self.add_list_item(course_item)

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
        self.parentWidget().widget(
            self.config.gui.gui_config.G_GUI_INDEX[self.back_index_key]
        ).cancel_course()
        self.set_new_course()

    def set_new_course(self):
        self.parentWidget().widget(
            self.config.gui.gui_config.G_GUI_INDEX[self.back_index_key]
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


class CourseDetailWidget(MenuWidget):
    list_id = None

    privacy_code = None
    all_downloaded = False
    map_image_size = None
    profile_image_size = None
    next_button = None

    address_format = "{locality}, {administrative_area}"

    def setup_menu(self):
        self.make_menu_layout(QtWidgets.QVBoxLayout)

        self.map_image = QtWidgets.QLabel()
        self.map_image.setAlignment(QT_ALIGN_CENTER)

        self.profile_image = QtWidgets.QLabel()
        self.profile_image.setAlignment(QT_ALIGN_CENTER)

        self.distance_label = QtWidgets.QLabel()
        self.distance_label.setMargin(0)
        self.distance_label.setContentsMargins(0, 0, 0, 0)

        self.elevation_label = QtWidgets.QLabel()
        self.elevation_label.setMargin(0)
        self.elevation_label.setContentsMargins(0, 0, 0, 0)

        self.locality_label = QtWidgets.QLabel()
        self.locality_label.setMargin(0)
        self.locality_label.setContentsMargins(0, 0, 0, 0)
        self.locality_label.setWordWrap(True)

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setContentsMargins(5, 0, 0, 0)
        info_layout.setSpacing(0)
        info_layout.addWidget(self.distance_label)
        info_layout.addWidget(self.elevation_label)
        info_layout.addWidget(self.locality_label)

        outer_layout = QtWidgets.QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(self.map_image)
        outer_layout.addLayout(info_layout)

        self.menu_layout.addLayout(outer_layout)
        self.menu_layout.addWidget(self.profile_image)

        # update panel for every 1 seconds
        self.timer = QtCore.QTimer(parent=self)
        self.timer.timeout.connect(self.update_display)

        # also set extra button for topbar
        self.next_button = topbar.TopBarNextButton((self.icon_x, self.icon_y))
        self.next_button.setEnabled(False)

        self.top_bar_layout.addWidget(self.next_button)

    def enable_next_button(self):
        self.next_button.setVisible(True)
        self.next_button.setEnabled(True)

    def connect_buttons(self):
        self.next_button.clicked.connect(self.set_course)

    def preprocess(self, course_info):
        # reset
        self.list_id = None
        self.privacy_code = None
        self.all_downloaded = False

        self.map_image.clear()
        self.profile_image.clear()
        self.next_button.setVisible(False)
        self.next_button.setEnabled(False)

        self.page_name_label.setText(course_info["name"])
        self.distance_label.setText("{:.1f}km".format(course_info["distance"] / 1000))
        self.elevation_label.setText("{:.0f}m up".format(course_info["elevation_gain"]))
        self.locality_label.setText(self.address_format.format(**course_info))

        self.list_id = course_info["id"]

        self.timer.start(settings.DRAW_INTERVAL)

    async def load_images(self):
        if self.check_all_image_and_draw():
            self.timer.stop()
            return
        else:
            # 1st download
            await self.config.api.get_ridewithgps_files(self.list_id)

    def on_back_menu(self):
        self.timer.stop()

    @qasync.asyncSlot()
    async def update_display(self):
        if self.check_all_image_and_draw():
            self.timer.stop()
            return

        # sequentially draw with download
        # 1st download check
        if self.privacy_code is None and self.config.api.check_ridewithgps_files(
            self.list_id, "1st"
        ):
            self.draw_images(draw_map_image=True, draw_profile_image=False)
            self.privacy_code = self.config.logger.course.get_ridewithgps_privacycode(
                self.list_id
            )
            if self.privacy_code is not None:
                # download files with privacy code (2nd download)
                await self.config.api.get_ridewithgps_files_with_privacy_code(
                    self.list_id, self.privacy_code
                )
        # 2nd download with privacy_code check
        elif self.privacy_code is not None and self.config.api.check_ridewithgps_files(
            self.list_id, "2nd"
        ):
            self.draw_images(draw_map_image=False, draw_profile_image=True)
            self.enable_next_button()
            self.timer.stop()

    def check_all_image_and_draw(self):
        # if all files exists, reload images and buttons, stop timer and exit
        if not self.all_downloaded and self.config.api is not None:
            self.all_downloaded = self.config.api.check_ridewithgps_files(
                self.list_id, "ALL"
            )
        if self.all_downloaded:
            res = self.draw_images()
            self.enable_next_button()
            return res
        # if no internet connection, stop timer and exit
        elif not detect_network():
            return True
        return False

    def set_course(self):
        index = self.config.gui.gui_config.G_GUI_INDEX["Courses List"]
        self.parentWidget().widget(index).set_course(
            (
                self.config.G_RIDEWITHGPS_API["URL_ROUTE_DOWNLOAD_DIR"]
                + "course-{route_id}.tcx"
            ).format(route_id=self.list_id)
        )

    def draw_images(self, draw_map_image=True, draw_profile_image=True):
        if self.list_id is None:
            return False

        if draw_map_image:
            filename = (
                self.config.G_RIDEWITHGPS_API["URL_ROUTE_DOWNLOAD_DIR"]
                + "preview-{route_id}.png"
            ).format(route_id=self.list_id)
            if self.map_image_size is None:
                self.map_image_size = QtGui.QImage(filename).size()
            if self.map_image_size.width() == 0:
                return False
            scale = (self.menu.width() / 2) / self.map_image_size.width()
            map_image_qsize = QtCore.QSize(
                int(self.map_image_size.width() * scale),
                int(self.map_image_size.height() * scale),
            )
            self.map_image.setPixmap(QtGui.QIcon(filename).pixmap(map_image_qsize))

        if draw_profile_image:
            filename = (
                self.config.G_RIDEWITHGPS_API["URL_ROUTE_DOWNLOAD_DIR"]
                + "elevation_profile-{route_id}.jpg"
            ).format(route_id=self.list_id)
            if self.profile_image_size is None:
                # self.profile_image_size = Image.open(filename).size
                self.profile_image_size = QtGui.QImage(filename).size()
            if self.profile_image_size.width() == 0:
                return False
            scale = self.menu.width() / self.profile_image_size.width()
            profile_image_qsize = QtCore.QSize(
                int(self.profile_image_size.width() * scale),
                int(self.profile_image_size.height() * scale),
            )
            self.profile_image.setPixmap(
                QtGui.QIcon(filename).pixmap(profile_image_qsize)
            )
        return True

    def resizeEvent(self, event):
        self.check_all_image_and_draw()

        h = self.size().height()
        q = self.distance_label.font()
        q.setPixelSize(int(h / 12))
        for label in [self.distance_label, self.elevation_label, self.locality_label]:
            label.setFont(q)

        return super().resizeEvent(event)
