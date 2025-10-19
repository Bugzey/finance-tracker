"""
Tests of the summary report
"""

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from finance_tracker.report.summary import (
    SummaryMetrics,
    SummaryPlot,
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

    @classmethod
    def tearDownClass(self):
        self.sess.rollback()

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


class SummaryPlotTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.box_data = [
            {"category": "bla", "target": 10},
            {"category": "alb", "target": 20},
        ]
        self.plot = SummaryPlot()

    def test_reshape(self):
        result = self.plot._reshape(self.box_data)
        self.assertEqual(
            result,
            {
                "category": ["bla", "alb"],
                "target": [10, 20],
            },
        )

    def test_make_boxplot(self):
        _ = self.plot.make_boxplot(self.box_data, category="category", target="target")
