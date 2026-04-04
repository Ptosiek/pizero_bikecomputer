from pizero_bikecomputer.modules.loaders.tcx import TcxLoader


def test_tcx():
    data_course, data_course_points = TcxLoader.load_file(
        "tests/data/tcx/Mt_Angel_Abbey.tcx"
    )
    assert len(data_course["latitude"]) == 946
    assert len(data_course_points["latitude"]) == 42

    # validate that course_point distance was set correctly
    assert len(data_course_points["distance"]) > 0
