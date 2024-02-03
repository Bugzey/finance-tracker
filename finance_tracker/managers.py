"""
Application logic - managers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime as dt
import logging

from sqlalchemy import select
from sqlalchemy.engine import Engine
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
from finance_tracker.qr_handler import (
    QRData,
)

logger = logging.getLogger(__name__)


@dataclass
class BaseManager(ABC):
    """
    Base object manager that should be inherited by other objects

    Args:
        sess: current SQLAlchemy session
    """
    engine: Engine

    @property
    @abstractmethod
    def model(self) -> BaseModel:
        pass

    def get(self, id: int) -> BaseModel:
        with Session(self.engine) as sess:
            result = sess.get(self.model, id)
        return result

    def create(self, **data) -> BaseModel:
        new = self.model(**data)
        with Session(self.engine) as sess:
            sess.add(new)
            sess.commit()
            # Silently select?
            _ = new.id
        return new

    def delete(self, id: int) -> BaseModel:
        """
        Delete an observation and return its previous values
        """
        with Session(self.engine) as sess:
            result = self.get(id)
            sess.delete(result)
            sess.commit()
        return result

    def update(self, id: int, **data) -> BaseModel:
        immutable_columns = BaseModel.__annotations__.keys()
        with Session(self.engine) as sess:
            item = self.get(id)
            for key, value in data.items():
                if key in immutable_columns:
                    logger.warning(f"Key is immutable: {key}")
                    continue
                item.__setattr__(key, value)

            sess.add(item)
            sess.commit()

        result = self.get(id)
        return result

    def query(
        self,
        limit: int = 100,
        offset: int = 0,
        **kwargs,
    ) -> list[BaseModel]:
        with Session(self.engine) as sess:
            query = select(self.model)

            for key, value in kwargs.items():
                query = query.where(self.model.__dict__[key] == value)

            query = query.offset(offset)

            result = sess.execute(query).fetchmany(limit)
            #   Unpack from single-length tuples
            result = [item[0] for item in result]

        return result


class AccountManager(BaseManager):
    model = AccountModel


class BusinessManager(BaseManager):
    model = BusinessModel

    def from_qr_code(self, qrdata: QRData, **data):
        data = {
            "code": qrdata.business_code,
            **data,
        }
        return self.create(**data)


class CategoryManager(BaseManager):
    model = CategoryModel


class SubcategoryManager(BaseManager):
    model = SubcategoryModel


class PeriodManager(BaseManager):
    model = PeriodModel

    def create(self, **data):
        period_start: dt.date = data.get("period_start") or dt.date.today().replace(day=1)

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
    #   2. Cancelling a transaction creates a new transaction for the negative sum

    def create(self, **data):
        """
        Handle dates if they are not given
        """
        #   Handle periods
        if not data.get("period_id"):

            #   Get or create the period corresponding to the transaction date or today
            period_manager = PeriodManager(self.engine)

            if data.get("transaction_date"):
                logger.info(f"Using period for date: {data['transaction_date']}")
                transaction_date = dt.date.fromisoformat(data["transaction_date"])
                data["transaction_date"] = transaction_date
                period_start = dt.date(
                   transaction_date.year,
                   transaction_date.month,
                   1,
                )
            else:
                logger.info("Using period for today")
                period_start = None

            period = period_manager.query(
                period_start=period_start,
            )
            period = period[0] if period else None
            if not period:
                period = period_manager.create(period_start=period_start)  # Today

            data["period_id"] = period.id

        #   Use business categories if not given
        if (
            data.get("business_id")
            and (
                not data.get("category_id")
                or not data.get("subcategory_id")
            )
        ):
            business_manager = BusinessManager(self.engine)
            business = business_manager.get(data.get("business_id"))
            data["category_id"] = data.get("category_id", business.default_category_id)
            data["subcategory_id"] = data.get("subcategory_id", business.default_subcategory_id)

        return super().create(**data)

    def from_qr_code(self, qrdata: QRData, **data):
        business = BusinessManager(engine=self.engine).query(code=qrdata.business_code)
        business = business[0] if business else business
        if not business:
            raise ValueError(f"Business with code: {qrdata.business_code} not found")

        period_manager = PeriodManager(engine=self.engine)
        period_start = dt.date(qrdata.date.year, qrdata.date.month, 1)
        period = period_manager.query(period_start=period_start)
        if not period:
            period = period_manager.create(period_start=period_start)
        else:
            period = period[0]

        #   Data given last so that it can override QR Code values
        data = {
            "amount": qrdata.amount,
            "code": f"{qrdata.business_code}-{qrdata.transaction_code}",
            "transaction_date": qrdata.date,
            "business_id": business.id,
            "period_id": period.id,
            "category_id": business.default_category_id,
            "subcategory_id": business.default_subcategory_id,
            **data,
        }
        return self.create(**data)
