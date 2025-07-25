"""
Tests of the summary report
"""

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from finance_tracker.report.summary import (
    SummaryMetrics,
)
from finance_tracker.models import BaseModel
from finance_tracker.managers import (
    PeriodManager,
    TransactionManager,
)


class SummaryMetricsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.sess = Session(self.engine)
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

    def test_init(self):
        metrics = SummaryMetrics(self.sess)
        self.assertIsInstance(metrics, SummaryMetrics)
        self.assertIsNotNone(metrics.account_id)
        self.assertIsNotNone(metrics.period_id)
        self.assertIsNotNone(metrics.period)

    def test_totals(self):
        metrics = SummaryMetrics(self.sess)
        self.assertEqual(metrics.current_month_total(), 50)
        self.assertEqual(metrics.previous_month_total(), 25)
        self.assertEqual(metrics.previous_year_total(), 12.5)
