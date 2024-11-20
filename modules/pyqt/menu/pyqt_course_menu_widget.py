import shutil
from collections import namedtuple

from PIL import Image, ImageEnhance, ImageQt

from modules._pyqt import (
    QT_ALIGN_CENTER,
    QtCore,
    QtWidgets,
    QtGui,
    qasync,
)
from modules.constants import MenuLabel
from modules.pyqt.components import icons, topbar
from modules.pyqt.pyqt_item import Item
from modules.settings import settings
from modules.utils.formatter import Altitude, Distance
from modules.utils.network import detect_network
from .pyqt_menu_widget import (
    MenuWidget,
    ListWidget,
    ListItemWidget,
)

SimpleItemConfig = namedtuple("SimpleItemConfig", ("label", "formatter"))


class CoursesMenuWidget(MenuWidget):
    def setup_menu(self):
        button_conf = (
            # Name(page_name), button_attribute, connected functions, icon
            (MenuLabel.LOCAL_STORAGE, "submenu", self.load_local_courses),
            (
                MenuLabel.RIDE_WITH_GPS,
                "submenu",
                self.load_rwgps_courses,
                (
                    icons.RideWithGPSIcon(),
                    (icons.BASE_LOGO_SIZE * 4, icons.BASE_LOGO_SIZE),
                ),
            ),
            (
                MenuLabel.CANCEL_COURSE,
                "dialog",
                lambda: self.config.gui.show_dialog(
                    self.cancel_course, MenuLabel.CANCEL_COURSE
                ),
            ),
        )
        self.add_buttons(button_conf)

    def preprocess(self):
        self.onoff_course_cancel_button()

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

    def onoff_course_cancel_button(self):
        status = self.config.logger.course.is_set
        self.buttons[MenuLabel.CANCEL_COURSE].onoff_button(status)

    def cancel_course(self):
        self.config.logger.reset_course(delete_course_file=True)
        self.onoff_course_cancel_button()

    def set_new_course(self, course_file):
        self.config.logger.set_new_course(course_file)
        self.config.gui.init_course()
        self.onoff_course_cancel_button()

    async def load_tcx_route(self, filename):
        self.cancel_course()
        course_file = (
            settings.COURSE_DIR / filename[: filename.lower().find(".tcx") + 4]
        )
        shutil.move(settings.COURSE_DIR / filename, course_file)
        self.set_new_course(course_file)
        self.config.gui.show_forced_message("Loading succeeded!")


class CourseListWidget(ListWidget):
    def setup_menu(self):
        super().setup_menu()
        self.vertical_scrollbar = self.list.verticalScrollBar()
        self.vertical_scrollbar.valueChanged.connect(self.detect_bottom)

    @qasync.asyncSlot(int)
    async def detect_bottom(self, value):
        if (
            self.list_type == MenuLabel.RIDE_WITH_GPS
            and value == self.vertical_scrollbar.maximum()
        ):
            await self.list_ride_with_gps()

    @qasync.asyncSlot()
    async def button_func(self):
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

    def preprocess_extra(self):
        self.page_name_label.setText(self.list_type)

    async def list_local_courses(self):
        courses = self.config.get_courses()
        for c in courses:
            course_item = CourseListItemWidget(self, self.list_type, c)
            self.add_list_item(course_item)

    async def list_ride_with_gps(self, reset=False):
        courses = await self.config.rwgps.list_routes(reset)

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


class CourseDetailWidget(MenuWidget):
    route_id = None
    course = None

    next_button = None
    font_size = 20

    def setup_menu(self):
        self.make_menu_layout(QtWidgets.QVBoxLayout)

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
            self.menu_layout.addWidget(self.map_image)
            outer_layout.addLayout(self.distance_item)
            outer_layout.addLayout(self.ascent_item)

        self.menu_layout.addLayout(outer_layout)
        self.menu_layout.addWidget(self.profile_image)

        # also set extra button for topbar
        self.next_button = topbar.TopBarNextButton()
        self.next_button.setEnabled(False)

        self.top_bar_layout.addWidget(self.next_button)

    def connect_buttons(self):
        self.next_button.clicked.connect(self.set_course)

    def preprocess(self, course_info):
        # reset
        self.course = None

        self.map_image.clear()
        self.profile_image.clear()
        self.next_button.setEnabled(False)

        self.page_name_label.setText(course_info["name"])
        self.distance_item.update_value(course_info["distance"])
        self.ascent_item.update_value(course_info["elevation_gain"])

        self.route_id = course_info["id"]

    async def load_images(self):
        if not self.check_all_image_and_draw():
            course_info, map_preview = await self.config.rwgps.get_route_files(
                self.route_id
            )

            if course_info and map_preview:
                self.draw_images(map_image=map_preview)
                profile, course = await self.config.rwgps.get_private_route_files(
                    self.route_id
                )

                if profile and course:
                    self.draw_images(profile_image=profile)
                    self.course = course
                    self.next_button.setEnabled(True)

    def check_all_image_and_draw(self):
        # if all files exists, load images and buttons,
        downloaded = self.config.rwgps.check_files(self.route_id)

        if downloaded:
            self.draw_images(downloaded[1], downloaded[2])
            self.course = downloaded[3]
            self.next_button.setEnabled(True)
            return True

        # if no internet connection exit
        elif not detect_network():
            return True
        return False

    def set_course(self):
        widget = self.parentWidget().findChild(
            QtWidgets.QWidget, MenuLabel.COURSES_LIST
        )
        widget.set_course(self.course)

    def draw_images(self, map_image=None, profile_image=None):
        if self.route_id is None:
            return

        if map_image and map_image.exists():
            im = Image.open(map_image).convert("RGBA")
            im = ImageEnhance.Contrast(im).enhance(2.0)

            map_image_size = im.size  # tuple (w, h)

            if map_image_size[0] == 0 or map_image_size[1] == 0:
                return

            ratio = 1 if self.is_vertical else 0.5

            scale = (self.size().width() * ratio) / map_image_size[0]
            im = im.resize(
                (
                    int(map_image_size[0] * scale),
                    int(map_image_size[1] * scale),
                )
            )
            self.map_image.setPixmap(QtGui.QPixmap.fromImage(ImageQt.ImageQt(im)))

        if profile_image and profile_image.exists():
            im = Image.open(profile_image).convert("RGBA")
            profile_image_size = im.size  # tuple (w, h)

            if profile_image_size[0] == 0 or profile_image_size[1] == 0:
                return

            scale = self.size().width() / profile_image_size[0]
            im = im.resize(
                (
                    int(profile_image_size[0] * scale),
                    int(profile_image_size[1] * scale),
                )
            )
            self.profile_image.setPixmap(QtGui.QPixmap.fromImage(ImageQt.ImageQt(im)))

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
