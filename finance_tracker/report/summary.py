"""
Generate summary reports

What do we want in terms of data?

- metric: current month total
- metric: previous month total
- metric: month over month difference, absolute and in percent
- metric: same month of previous year total
- metric: year of year difference - absolute and in percent
- graph: Totals of last 12 months - absolute values
- filter: account_id + name
- (future): multi-select - add child accounts
"""

from dataclasses import dataclass, field
import datetime as dt
import io
from typing import Self

import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import Engine, select, func, column, text
from sqlalchemy.orm import Session

from finance_tracker.models import (
    BusinessModel,
    CategoryModel,
    PeriodModel,
    TransactionModel,
)


matplotlib.use("svg")


TOTAL_HISTORY_QUERY = """-- # noqa
select
    per.period_start
    , sum(tran.amount) as amount
from
    "transaction" tran

    left join period per
    on tran.period_id = per.id

where
    1 = 1
    and tran.account_id = :account_id
    and (
        per.period_start <= (
            select
                per.period_start
            from
                period per
            where
                per.id = :period_id
        )
    )

group by
    per.period_start
"""


@dataclass
class SummaryMetrics:
    sess: Session
    period_id: int | None = None
    account_id: int | None = None
    top_n: int = 10

    period: dt.date = field(init=False)

    def __post_init__(self):
        if self.period_id:
            period = self.sess.scalars(
                select(PeriodModel)
                .where(PeriodModel.id == self.period_id)
            ).first()
            self.period = period.period_start
        else:
            period = self.sess.scalars(
                select(PeriodModel)
                .where(
                    PeriodModel.id.in_(
                        select(TransactionModel.period_id)
                        .distinct()
                        .scalar_subquery()
                    )
                )
                .order_by(PeriodModel.period_start.desc())
            ).first()
            self.period_id = period.id
            self.period = period.period_start

        self.account_id = self.account_id or 1

    def _get_total_query(self, period: dt.date) -> float:
        query = (
            select(func.sum(TransactionModel.amount).label("amount"))
            .where(
                TransactionModel.period_id == (
                    select(PeriodModel.id)
                    .where(
                        PeriodModel.period_start == period,
                        TransactionModel.account_id == self.account_id,
                    )
                    .scalar_subquery()
                )
            )
            .group_by(TransactionModel.period_id)
        )
        return query

    def current_month_total(self) -> float:
        query = self._get_total_query(self.period)
        return self.sess.scalar(query) or 0.0

    def previous_month_total(self) -> float:
        period = dt.date(self.period.year, self.period.month, 1) - dt.timedelta(days=1)
        period = dt.date(period.year, period.month, 1)
        query = self._get_total_query(period)
        return self.sess.scalar(query) or 0.0

    def previous_year_total(self) -> float:
        period = dt.date(self.period.year - 1, self.period.month, self.period.day)
        query = self._get_total_query(period)
        return self.sess.scalar(query) or 0.0

    def top_businesses(self) -> list[dict]:
        query = (
            select(
                TransactionModel.business_id,
                BusinessModel.name,
                func.count(TransactionModel.id).label("count"),
                func.sum(TransactionModel.amount).label("amount"),
            )
            .join_from(
                TransactionModel,
                BusinessModel,
                onclause=TransactionModel.business_id == BusinessModel.id,
                isouter=True,
            )
            .where(
                TransactionModel.account_id == self.account_id,
                TransactionModel.period_id == self.period_id,
            )
            .group_by(TransactionModel.business_id)
            .order_by(column("amount").desc())
            .limit(self.top_n)
        )
        return self.sess.execute(query).all()

    def top_categories(self) -> list[dict]:
        query = (
            select(
                TransactionModel.category_id,
                CategoryModel.name,
                func.count(TransactionModel.id).label("count"),
                func.sum(TransactionModel.amount).label("amount"),
            )
            .join_from(
                TransactionModel,
                CategoryModel,
                onclause=TransactionModel.category_id == CategoryModel.id,
                isouter=True,
            )
            .where(
                TransactionModel.account_id == self.account_id,
                TransactionModel.period_id == self.period_id,
            )
            .group_by(TransactionModel.category_id)
            .order_by(column("amount").desc())
            .limit(self.top_n)
        )
        return self.sess.execute(query).all()


@dataclass
class SummaryPlot:
    data: dict
    plot_svg: str

    @classmethod
    def from_engine(
        cls,
        engine: Engine,
        account_id: int = 1,
        period_id: int | None = None,
        period: dt.date | None = None,
    ) -> Self:
        if not period:
            period = dt.date.today().replace(day=1)

        with engine.begin() as con:
            result = con.execute(
                text(TOTAL_HISTORY_QUERY),
                parameters=dict(
                    account_id=account_id,
                    period=period,
                    period_id=period_id,
                ),
            ).all()

        data = cls.reshape_data(result)
        plot_svg = cls.make_graph(data)
        return cls(data=data, plot_svg=plot_svg)

    @staticmethod
    def reshape_data(data: list[tuple]) -> dict:
        """
        Reshape the list of named tuples output by sqlalchemy into a dictionary for use in plotting
        """
        result = {
            "period_start": [item._mapping["period_start"] for item in data],
            "amount": [item._mapping["amount"] for item in data],
        }
        return result

    @staticmethod
    def make_graph(data: dict) -> bytes:
        """
        Create the graph and output it PNG format as a bytes object
        """
        fig, ax = plt.subplots()
        ax.plot(data["period_start"], data["amount"])
        ax.set_xlabel("Period")
        ax.set_ylabel("Amount")
        ax.set_ylim(ymin=0)
        ax.set_title("Total Amount")

        with io.BytesIO() as cur_file:
            _ = fig.savefig(cur_file, format="png")
            cur_file.seek(0)
            result = cur_file.read()

        return result
