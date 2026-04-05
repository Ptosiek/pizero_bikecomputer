from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from pizero_bikecomputer.modules.course import Course


class Config:
    pass


# TODO find/create a file where time is not set so distance is kept empty with no_indexing
# @patch(
#     "pizero_bikecomputer.modules.settings.settings.COURSE_INDEXING",
#     False,
# )
# def test_load_no_indexing():
#     config = Config()
#     course = Course(config)
#     course.load(file="tests/data/tcx/Heart_of_St._Johns_Peninsula_Ride.tcx")
#
#     # downsampled from 184 to 31 points
#     assert len(course.latitude) == 31
#     assert len(course.course_points.latitude) == 18
#
#     # distance was not set since there's no indexing
#     assert len(course.course_points.distance) == 0
#
#     assert len(course.colored_altitude) == 31


@patch(
    "pizero_bikecomputer.modules.settings.settings.COURSE_FILE_PATH",
    Path(NamedTemporaryFile().name),
)
def test_load_with_tcx_indexing():
    config = Config()
    course = Course(config)
    course.load(file="tests/data/tcx/Heart_of_St._Johns_Peninsula_Ride.tcx")

    # downsampled from 184 to 31 points
    assert len(course.latitude) == 31
    assert len(course.course_points.latitude) == 18
    assert len(course.course_points.distance) == 18


@patch(
    "pizero_bikecomputer.modules.settings.settings.COURSE_FILE_PATH",
    Path(NamedTemporaryFile().name),
)
def test_load_insert_course_point():
    config = Config()
    course = Course(config)
    course.load(file="tests/data/tcx/Heart_of_St._Johns_Peninsula_Ride-CP-Removed.tcx")

    assert len(course.course_points.latitude) == 18
    assert len(course.course_points.distance) == 18

    assert course.course_points.name[0] == "Start"
    assert course.course_points.latitude[0] == 45.57873
    assert course.course_points.longitude[0] == -122.71318
    assert course.course_points.distance[0] == 0.0

    assert course.course_points.name[-1] == "End"
    assert course.course_points.latitude[-1] == 45.5788
    assert course.course_points.longitude[-1] == -122.7135
    assert course.course_points.distance[-1] == 12.286501
