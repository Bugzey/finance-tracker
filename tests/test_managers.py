"""
Unit tests for application logic
"""

import datetime as dt
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Mapped,
    Session,
)

from finance_tracker.models import (
    BaseModel,
    BusinessModel,
    TransactionModel,
)
from finance_tracker.managers import (
    BaseManager,
    AccountManager,
    BusinessManager,
    CategoryManager,
    SubcategoryManager,
    PeriodManager,
    TransactionManager,
)
from finance_tracker.qr_handler import QRData


class SomeModel(BaseModel):
    __tablename__ = "some_table"
    value: Mapped[str]


class SomeManager(BaseManager):
    model = SomeModel


class BaseManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        BaseModel.metadata.create_all(self.engine)
        with Session(self.engine) as sess:
            sess.add(SomeModel(value="bla"))
            sess.commit()
        self.manager = SomeManager(engine=self.engine)

    def test_get(self):
        result = self.manager.get(1)
        self.assertIsInstance(result, SomeModel)
        self.assertEqual(result.value, "bla")
        self.assertEqual(result.id, 1)

    def test_create(self):
        _ = self.manager.create(value="bla2")
        result = self.manager.get(2)
        self.assertIsInstance(result, SomeModel)
        self.assertEqual(result.value, "bla2")

    def test_delete(self):
        result = self.manager.delete(id=1)
        self.assertEqual(result.value, "bla")
        new = self.manager.get(id=1)
        self.assertIsNone(new)

    def test_update(self):
        bad_date = dt.datetime(2000, 1, 1)
        result = self.manager.update(id=1, value="changed", updated_time=bad_date)
        self.assertEqual(result.value, "changed")
        result = self.manager.get(id=1)
        self.assertEqual(result.value, "changed")
        self.assertNotEqual(result.updated_time, bad_date)


class BusinessManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        BaseModel.metadata.create_all(self.engine)
        self.manager = BusinessManager(engine=self.engine)

    def test_from_qr_code_good(self):
        qr_data = QRData(
            business_code="some_code",
            transaction_code="bla",
            date=dt.date(2020, 1, 1),
            time=dt.time(0, 1, 23),
            amount=12.3,
        )
        result = self.manager.from_qr_code(
            qr_data,
            name="some_business",
            default_category_id=1,
            default_subcategory_id=1,
        )
        self.assertIsInstance(result, BusinessModel)
        self.assertEqual(result.code, "some_code")


class PeriodTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        BaseModel.metadata.create_all(self.engine)
        self.manager = PeriodManager(engine=self.engine)

    def test_create_blank(self):
        _ = self.manager.create()
        result = self.manager.get(1)
        self.assertEqual(result.period_start, dt.date.today().replace(day=1))
        self.assertEqual(result.code, dt.date.today().strftime("%Y%m"))


class TransactionManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        BaseModel.metadata.create_all(self.engine)
        self.account = AccountManager(self.engine).create(name="Account")
        self.period = PeriodManager(self.engine).create(period_start=dt.date(2022, 1, 1))
        self.category = CategoryManager(self.engine).create(name="Daily life")
        self.subcategory = SubcategoryManager(self.engine).create(
            name="Food",
            category_id=self.category.id,
        )
        self.business = BusinessManager(self.engine).create(
            name="Some business",
            code="bla1",
            default_category_id=self.category.id,
            default_subcategory_id=self.subcategory.id,
        )
        self.qrdata = QRData(
            business_code=self.business.code,
            transaction_code="123",
            date=dt.date(2022, 1, 12),
            time=dt.time(0, 1, 12),
            amount=59.99,
        )

    def test_from_qr_full(self):
        tran = TransactionManager(self.engine).from_qr_code(
            qrdata=self.qrdata,
            account_id=self.account.id,
        )
        self.assertIsInstance(tran, TransactionModel)
        self.assertEqual(tran.account_id, self.account.id)
        self.assertEqual(tran.business_id, self.business.id)
        self.assertEqual(tran.category_id, self.category.id)
        self.assertEqual(tran.subcategory_id, self.subcategory.id)
        self.assertEqual(tran.period_id, self.period.id)

    def test_from_qr_override(self):
        new_cat = CategoryManager(self.engine).create(name="second")
        new_sub = SubcategoryManager(self.engine).create(name="second", category_id=2)
        new_per = PeriodManager(self.engine).create(period_start=dt.date(2022, 12, 1))

        tran = TransactionManager(self.engine).from_qr_code(
            qrdata=self.qrdata,
            account_id=self.account.id,
            category_id=2,
            subcategory_id=2,
            period_id=2,
            amount=12.91,
        )
        self.assertIsInstance(tran, TransactionModel)
        self.assertEqual(tran.account_id, self.account.id)
        self.assertEqual(tran.business_id, self.business.id)
        self.assertEqual(tran.category_id, new_cat.id)
        self.assertEqual(tran.subcategory_id, new_sub.id)
        self.assertEqual(tran.period_id, new_per.id)
        self.assertAlmostEqual(float(tran.amount), 12.91)
