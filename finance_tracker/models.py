"""
Database models
"""

import datetime as dt
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    ForeignKey,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class BaseModel(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_time: Mapped[dt.datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_time: Mapped[dt.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self):
        name = self.__class__.__name__
        fields = [
            f"{item.name}='{self.__dict__[item.name]}'"
            for item
            in self.__table__.c
        ]
        result = f"{name}({', '.join(fields)})"
        return result


class CategoryModel(BaseModel):
    __tablename__ = "category"
    name: Mapped[str] = mapped_column(unique=True)


class SubcategoryModel(BaseModel):
    __tablename__ = "subcategory"
    name: Mapped[str] = mapped_column()
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["CategoryModel"] = relationship()


class AccountModel(BaseModel):
    __tablename__ = "account"
    name: Mapped[str]


class BusinessModel(BaseModel):
    __tablename__ = "business"
    name: Mapped[str]
    code: Mapped[str] = mapped_column(unique=True, insert_default=lambda x: str(uuid4()))
    default_category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    default_category: Mapped["CategoryModel"] = relationship()
    default_subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategory.id"))
    default_subcategory: Mapped["SubcategoryModel"] = relationship()


class PeriodModel(BaseModel):
    __tablename__ = "period"
    code: Mapped[str] = mapped_column(unique=True)
    period_start: Mapped[dt.date]
    period_end: Mapped[dt.date]


class TransactionModel(BaseModel):
    __tablename__ = "transaction"
    code: Mapped[str] = mapped_column(unique=True, insert_default=lambda x: str(uuid4()))
    amount: Mapped[Decimal]
    transaction_date: Mapped[dt.date | None]
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    account: Mapped["AccountModel"] = relationship(foreign_keys=[account_id])
    account_for_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    account_for: Mapped["AccountModel"] = relationship(foreign_keys=[account_for_id])
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["CategoryModel"] = relationship()
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategory.id"))
    subcategory: Mapped["SubcategoryModel"] = relationship()
    business_id: Mapped[int | None] = mapped_column(ForeignKey("business.id"))
    business: Mapped["BusinessModel"] = relationship()
    period_id: Mapped[int] = mapped_column(ForeignKey("period.id"))
    period: Mapped["PeriodModel"] = relationship()
