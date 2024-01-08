"""
Tests for the QR code handler
"""

from dataclasses import asdict
import datetime as dt
import unittest

from finance_tracker.qr_handler import (
    QRData,
)


class QRDataTestCase(unittest.TestCase):
    def setUp(self):
        self.raw_data = {
            "business_code": "business_code",
            "transaction_code": "transaction_code",
            "date": "2022-01-01",
            "time": "00:01:23",
            "amount": "12.51",
        }
        self.string_data = "*".join(self.raw_data.values())
        self.data = {
            "business_code": "business_code",
            "transaction_code": "transaction_code",
            "date": dt.date(2022, 1, 1),
            "time": dt.time(0, 1, 23),
            "amount": 12.51,
            "datetime": dt.datetime(2022, 1, 1, 0, 1, 23),
        }

    def test_init(self):
        result = QRData(**self.raw_data)
        self.assertIsInstance(result, QRData)
        self.assertAlmostEqual(asdict(result), self.data)

    def test_from_string_good(self):
        result = QRData.from_string(self.string_data)
        self.assertIsInstance(result, QRData)
        self.assertAlmostEqual(asdict(result), self.data)

    def test_from_string_bad(self):
        with self.assertRaises(ValueError):
            _ = QRData.from_string("some random string bla bla")
