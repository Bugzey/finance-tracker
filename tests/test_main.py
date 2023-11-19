"""
Main unit tests
"""

from sqlalchemy import create_engine
import tempfile
from types import SimpleNamespace
import unittest

from finance_tracker.main import (
    DBHandler,
    main,
)
from finance_tracker.managers import (
    CategoryManager,
    AccountManager,
)
from finance_tracker.models import (
    BaseModel,
    TransactionModel,
)


class DBHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        BaseModel.metadata.create_all(self.engine)

    def test_initial_setup(self):
        DBHandler.initial_setup(self.engine)

        accounts = AccountManager(self.engine).query()
        self.assertEqual(len(accounts), 1)
        self.assertTrue(
            any(item.name.casefold() == "me" for item in accounts)
        )

        categories = CategoryManager(self.engine).query()
        self.assertTrue(
            any(item.name == "Entertainment" for item in categories)
        )


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.db = tempfile.NamedTemporaryFile()
        self.engine = create_engine(f"sqlite+pysqlite:///{self.db.name}")
        BaseModel.metadata.create_all(self.engine)

    def test_main_pre_existing(self):
        #   Create a category
        main(
            SimpleNamespace(
                database=self.db.name,
                action="create",
                object="category",
                data=[{"name": "test_cat"}],
            )
        )

        #   Create a subcategory
        main(
            SimpleNamespace(
                database=self.db.name,
                action="create",
                object="subcategory",
                data=[{"name": "test_sub", "category_id": 1}],
            )
        )

        #   Create an account
        main(
            SimpleNamespace(
                database=self.db.name,
                action="create",
                object="account",
                data=[{"name": "test_acc"}],
            )
        )

        #   Create a transaction
        main(
            SimpleNamespace(
                database=self.db.name,
                action="create",
                object="transaction",
                data=[
                    {"amount": 12.54},
                    {"account_id": 1},
                    {"category_id": 1},
                    {"subcategory_id": 1},
                ],
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
                data=[],
            )
        )
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], TransactionModel)
        self.assertAlmostEqual(float(result[0].amount), 12.54)

    def test_main_qr_code_flow(self):
        #   TODO
        pass
