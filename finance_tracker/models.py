"""
Database models
"""

import datetime as dt
from decimal import Decimal

import sqlalchemy as db
from sqlalchemy import (
    ForeignKey,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_time: Mapped[dt.datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_time: Mapped[dt.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )


class CategoryModel(Base):
    __tablename__ = "category"
    name: Mapped[str]


class SubcategoryModel(Base):
    __tablename__ = "subcategory"
    name: Mapped[str]


class UserModel(Base):
    __tablename__ = "user"
    name: Mapped[str]
    accounts: Mapped[list["AccountModel"]] = relationship(back_populates="user")


class AccountModel(Base):
    __tablename__ = "account"
    name: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["UserModel"] = relationship(back_populates="accounts")


class BusinessModel(Base):
    __tablename__ = "business"
    name: Mapped[str]
    code: Mapped[str]
    default_category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    default_category: Mapped["CategoryModel"] = relationship()
    default_subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategory.id"))
    default_subcategory: Mapped["SubcategoryModel"] = relationship()


class TransactionModel(Base):
    __tablename__ = "transaction"
    amount: Mapped[Decimal]
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    account: Mapped["AccountModel"] = relationship()
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["CategoryModel"] = relationship()
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategory.id"))
    subcategory: Mapped["SubcategoryModel"] = relationship()
    business_id: Mapped[int] = mapped_column(ForeignKey("business.id"))
    business: Mapped["BusinessModel"] = relationship()
