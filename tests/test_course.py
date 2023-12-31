import unittest
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from modules.course import Course


class Config:
    pass


class TestCourse(unittest.TestCase):
    # TODO find/create a file where time is not set so distance is kept empty with no_indexing
    # @patch(
    #     "modules.settings.settings.COURSE_INDEXING",
    #     False,
    # )
    # def test_load_no_indexing(self):
    #     config = Config()
    #     course = Course(config)
    #     course.load(file="tests/data/tcx/Heart_of_St._Johns_Peninsula_Ride.tcx")
    #
    #     # downsampled from 184 to 31 points
    #     self.assertEqual(len(course.latitude), 31)
    #     self.assertEqual(len(course.course_points.latitude), 18)
    #
    #     # distance was not set since there's no indexing
    #     self.assertEqual(len(course.course_points.distance), 0)
    #
    #     self.assertEqual(len(course.colored_altitude), 31)

    @patch(
        "modules.settings.settings.COURSE_FILE_PATH",
        NamedTemporaryFile().name,
    )
    def test_load_with_tcx_indexing(self):
        config = Config()
        course = Course(config)
        course.load(file="tests/data/tcx/Heart_of_St._Johns_Peninsula_Ride.tcx")

        # downsampled from 184 to 31 points
        self.assertEqual(len(course.latitude), 31)
        self.assertEqual(len(course.course_points.latitude), 18)
        self.assertEqual(len(course.course_points.distance), 18)

    @patch(
        "modules.settings.settings.COURSE_FILE_PATH",
        NamedTemporaryFile().name,
    )
    def test_load_insert_course_point(self):
        config = Config()
        course = Course(config)
        course.load(
            file="tests/data/tcx/Heart_of_St._Johns_Peninsula_Ride-CP-Removed.tcx"
        )

        self.assertEqual(len(course.course_points.latitude), 18)
        self.assertEqual(len(course.course_points.distance), 18)

        self.assertEqual(course.course_points.name[0], "Start")
        self.assertEqual(course.course_points.latitude[0], 45.57873)
        self.assertEqual(course.course_points.longitude[0], -122.71318)
        self.assertEqual(course.course_points.distance[0], 0.0)

        self.assertEqual(course.course_points.name[-1], "End")
        self.assertEqual(course.course_points.latitude[-1], 45.5788)
        self.assertEqual(course.course_points.longitude[-1], -122.7135)
        self.assertEqual(course.course_points.distance[-1], 12.286501)
