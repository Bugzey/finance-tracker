"""
Unit tests for application logic
"""

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
)


class SomeModel(BaseModel):
    __tablename__ = "some_table"
    value: Mapped[str]


class SomeManager(BaseManager):
    model = SomeModel


class BaseManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        BaseModel.metadata.create_all(self.engine)
        self.sess = Session(self.engine)
        self.sess.add(SomeModel(value="bla"))
        self.sess.flush()
        self.manager = SomeManager(sess=self.sess)

    def tearDown(self):
        self.sess.rollback()

    def test_get(self):
        result = self.manager.get(1)
        self.assertIsInstance(result, SomeModel)
        self.assertEqual(result.value, "bla")
        self.assertEqual(result.id, 1)
