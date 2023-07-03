"""
Unit tests for models
"""

import unittest

import sqlalchemy

from finance_tracker.models import (
    AccountModel,
    CategoryModel,
    SubcategoryModel,
    TransactionModel,
    UserModel,
)


class TestBase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite+pysqlite:///:memory:")
        self.session = sqlalchemy.orm.Session(bind=self.engine)

    def tearDown(self):
        self.session.rollback()


class AccountModelTestCase(TestBase):
    def test_account(self):
        result = AccountModel(name="some_name")
        self.session.add(result)
        self.assertTrue(result, AccountModel)
        self.assertEqual(result.name, "some_name")
