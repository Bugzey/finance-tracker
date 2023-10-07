"""
Application logic - managers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime as dt
import logging

from sqlalchemy.orm import (
    Session,
)

from finance_tracker.models import (
    BaseModel,
    AccountModel,
    BusinessModel,
    CategoryModel,
    SubcategoryModel,
    PeriodModel,
    TransactionModel,
)

logger = logging.getLogger(__name__)


@dataclass
class BaseManager(ABC):
    """
    Base object manager that should be inherited by other objects

    Args:
        sess: current SQLAlchemy session
    """
    sess: Session

    @property
    @abstractmethod
    def model(self) -> BaseModel:
        pass

    def get(self, id: int) -> BaseModel:
        return self.sess.get(self.model, id)

    def create(self, **data) -> BaseModel:
        new = self.model(**data)
        _ = self.sess.add(new)
        return new

    def delete(self, id: int) -> BaseModel:
        """
        Delete an observation and return its previous values
        """
        result = self.get(id)
        self.sess.delete(result)
        return result

    def update(self, id: int, **data) -> BaseModel:
        immutable_columns = BaseModel.__annotations__.keys()
        item = self.get(id)
        for key, value in data.items():
            if key in immutable_columns:
                logger.warning(f"Key is immutable: {key}")
                continue
            item.__dict__[key] = value

        self.sess.add(item)
        return item


class AccountManager(BaseManager):
    model = AccountModel


class BusinessManager(BaseManager):
    model = BusinessModel


class CategoryManager(BaseManager):
    model = CategoryModel


class SubcategoryManager(BaseManager):
    model = SubcategoryModel


class PeriodManager(BaseManager):
    model = PeriodModel

    def create(self, **data):
        period_start: dt.date = data.get("period_start", dt.date.today().replace(day=1))

        if period_start.month == 12:
            period_end = (
                period_start.replace(year=period_start.year + 1, month=1, day=1)
            )
        else:
            period_end = period_start.replace(month=period_start.month + 1)

        period_end -= dt.timedelta(days=1)
        data["period_start"] = period_start
        data["period_end"] = period_end
        data["code"] = period_start.strftime("%Y%m")
        return super().create(**data)


class TransactionManager(BaseManager):
    model = TransactionModel
    #   TODO: this needs to be cancellable:
    #   1. Disable delete
    #   2. Cnacelling a transaction creates a new transaction for the negative sum
