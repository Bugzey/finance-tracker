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
)
from finance_tracker.managers import (
    BaseManager,
    PeriodManager,
)


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
