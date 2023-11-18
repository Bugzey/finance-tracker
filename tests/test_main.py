"""
Main unit tests
"""

import tempfile
from types import SimpleNamespace
import unittest

from finance_tracker.main import (
    DBHandler,
    main,
)
from finance_tracker.models import (
    TransactionModel,
)


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.db = tempfile.NamedTemporaryFile()

    def test_main_manual(self):
        #   Create a category
        main(
            SimpleNamespace(
                database=self.db.name,
                action="create",
                object="category",
                data={"name": "test_cat"},
            )
        )

        #   Create a subcategory
        main(
            SimpleNamespace(
                database=self.db.name,
                action="create",
                object="subcategory",
                data={"name": "test_sub"},
            )
        )

        #   Create an account
        main(
            SimpleNamespace(
                database=self.db.name,
                action="create",
                object="account",
                data={"name": "test_acc"},
            )
        )

        #   Create a transaction
        main(
            SimpleNamespace(
                database=self.db.name,
                action="create",
                object="transaction",
                data={
                    "amount": 12.54,
                    "account_id": 1,
                    "category_id": 1,
                    "subcategory_id": 1,
                },
            )
        )

        #   Check result
        result = main(
            SimpleNamespace(
                database=self.db.name,
                action="query",
                object="transaction",
                limit=10,
                offset=0,
                data={},
            )
        )
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], TransactionModel)
        self.assertAlmostEqual(float(result[0].amount), 12.54)

    def test_main_qr_code_flow(self):
        #   TODO
        pass
