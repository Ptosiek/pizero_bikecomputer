import os
import tempfile
from datetime import UTC, datetime
from unittest.mock import patch

from pizero_bikecomputer.modules.logger.logger_csv import LoggerCsv
from pizero_bikecomputer.modules.logger.logger_fit import LoggerFit


@patch(
    "pizero_bikecomputer.modules.settings.settings.LOG_DB",
    "tests/data/log.db-Heart_of_St._Johns_Peninsula_Ride",
)
def test_write_log():
    logger = LoggerCsv()
    _, path = tempfile.mkstemp()

    try:
        result = logger.write_log(path)
    finally:
        os.remove(path)

    assert result is True


@patch(
    "pizero_bikecomputer.modules.settings.settings.LOG_DB",
    "tests/data/log.db-Heart_of_St._Johns_Peninsula_Ride",
)
def test_write_logs():
    logger = LoggerFit()

    start = datetime(2023, 9, 28, 20, 39, 13, tzinfo=UTC)
    end = datetime(2023, 9, 28, 21, 10, 53, tzinfo=UTC)

    _, path = tempfile.mkstemp()

    try:
        result = logger.write_log_cython(path, start, end)

        assert result is True

        with open(path, "rb") as f:
            cython_data = f.read()
    finally:
        os.remove(path)

    _, path = tempfile.mkstemp()

    try:
        result = logger.write_log_python(path, start, end)

        assert result is True

        with open(path, "rb") as f:
            python_data = f.read()

    finally:
        os.remove(path)

    assert cython_data == python_data
