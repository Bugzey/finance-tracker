"""
Tests of the summary report
"""

import datetime as dt
import unittest

from sqlalchemy import create_engine

from finance_tracker.report.summary import (
    SummaryMetrics,
)
from finance_tracker.models import BaseModel
from finance_tracker.managers import (
    PeriodManager,
    TransactionManager,
)


class SummaryMetricsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        BaseModel.metadata.create_all(self.engine)
        self.transaction_manager = TransactionManager(self.engine)
        self.transaction_manager.create(
            transaction_date="2024-01-01",
            category_id=1,
            subcategory_id=1,
            account_id=1,
            amount=50,
        )
        self.transaction_manager.create(
            transaction_date="2023-12-01",
            category_id=1,
            subcategory_id=1,
            account_id=1,
            amount=25,
        )
        self.transaction_manager.create(
            transaction_date="2023-01-01",
            category_id=1,
            subcategory_id=1,
            account_id=1,
            amount=12.5,
        )
        self.period_manager = PeriodManager(self.engine)

    def test_from_engine(self):
        result = SummaryMetrics.from_engine(self.engine, period=dt.date(2024, 1, 1))
        self.assertIsInstance(result, SummaryMetrics)
        self.assertEqual(result.current_month_total, 50)
        self.assertEqual(result.previous_month_total, 25)
        self.assertEqual(result.previous_year_total, 12.5)
