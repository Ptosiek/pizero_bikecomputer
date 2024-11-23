import os
import tempfile
import unittest
from datetime import UTC, datetime

from modules.logger.logger_csv import LoggerCsv
from modules.logger.logger_fit import LoggerFit


class TestLoggerCsv(unittest.TestCase):
    def test_write_log(self):
        logger = LoggerCsv("tests/data/log.db-Heart_of_St._Johns_Peninsula_Ride")
        _, path = tempfile.mkstemp()

        try:
            result = logger.write_log(path)
        finally:
            os.remove(path)

        self.assertTrue(result)


class TestLoggerFit(unittest.TestCase):
    def test_write_logs(self):
        logger = LoggerFit("tests/data/log.db-Heart_of_St._Johns_Peninsula_Ride")

        start = datetime(2023, 9, 28, 20, 39, 13, tzinfo=UTC)
        end = datetime(2023, 9, 28, 21, 10, 53, tzinfo=UTC)

        _, path = tempfile.mkstemp()

        try:
            result = logger.write_log_python(path, start, end)

            self.assertTrue(result)

            with open(path, "rb") as f:
                python_data = f.read()

        finally:
            os.remove(path)

        _, path = tempfile.mkstemp()

        try:
            result = logger.write_log_cython(path, start, end)

            self.assertTrue(result)

            with open(path, "rb") as f:
                cython_data = f.read()
        finally:
            os.remove(path)

        self.assertEqual(cython_data, python_data)
