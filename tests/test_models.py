"""
Unit tests for models
"""

import unittest

import sqlalchemy

from finance_tracker.models import (
    AccountModel,
    Base,
    BusinessModel,
    CategoryModel,
    SubcategoryModel,
    TransactionModel,
    UserModel,
)


class TestBase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite+pysqlite:///:memory:")
        self.session = sqlalchemy.orm.Session(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.session.begin()

    def tearDown(self):
        self.session.rollback()


class AccountModelTestCase(TestBase):
    def test_account(self):
        result = AccountModel(name="some_name")
        self.session.add(result)
        self.assertTrue(result, AccountModel)
        self.assertEqual(result.name, "some_name")


class TransactionTestCase(TestBase):
    def setUp(self):
        super().setUp()
        self.user = UserModel(name="user")
        self.account = AccountModel(name="account", user=self.user)
        self.category = CategoryModel(name="category")
        self.subcategory = SubcategoryModel(name="subcategory")
        self.business = BusinessModel(
            name="business",
            code="blabla123",
            default_category=self.category,
            default_subcategory=self.subcategory,
        )
        self.session.add_all([
            self.user,
            self.account,
            self.category,
            self.subcategory,
            self.business,
        ])
        self.session.commit()

    def test_transaction(self):
        transaction = TransactionModel(
            amount=12,
            category=self.category,
            subcategory=self.subcategory,
            account=self.account,
            business=self.business,
        )
        self.assertEqual(transaction.category.name, "category")
        self.assertEqual(transaction.subcategory.name, "subcategory")
        self.assertEqual(transaction.account.name, "account")
        self.assertEqual(transaction.business.name, "business")
