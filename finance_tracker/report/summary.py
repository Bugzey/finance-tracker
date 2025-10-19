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

import base64
from dataclasses import dataclass, field
import datetime as dt
import io

import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import select, func, column
from sqlalchemy.orm import Session

from finance_tracker.models import (
    AccountModel,
    BusinessModel,
    CategoryModel,
    PeriodModel,
    TransactionModel,
)


matplotlib.use("svg")


@dataclass
class SummaryMetrics:
    sess: Session
    period_id: int | None = None
    account_id: int | None = None
    account_for_ids: list[int] | None = None
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

    def get_account_for_total(self) -> list[dict]:
        query = (
            select(
                TransactionModel.account_for_id,
                func.max(AccountModel.name).label("account_for_name"),
                func.sum(TransactionModel.amount).label("amount"),
            )
            .outerjoin(
                AccountModel,
                TransactionModel.account_for_id == AccountModel.id,
            )
            .where(
                TransactionModel.account_id == self.account_id,
                TransactionModel.period_id == self.period_id,
                (
                    TransactionModel.account_for_id.in_(self.account_for_ids)
                    if self.account_for_ids
                    else 1 == 1
                ),
            )
            .group_by(
                TransactionModel.account_for_id,
            )
        )
        return self.sess.execute(query).mappings().all()


@dataclass
class SummaryPlot:
    out_format: str = "png"

    def _make_plot(self, fig) -> str:
        """
        Create a binary image useable by the Web application
        """
        with io.BytesIO() as cur_file:
            _ = fig.savefig(cur_file, format="png")
            cur_file.seek(0)
            result = cur_file.read()

        result = base64.b64encode(result).decode("utf-8")
        return result

    def _reshape(self, data: list[dict]) -> dict[str, list]:
        """
        Reshape a list of row data into a list of column dictionaries for use by matplotlib
        """
        keys = list(data[0].keys())
        result = {
            key: [row[key] for row in data]
            for key
            in keys
        }
        return result

    def make_history_linechart(self, data: dict) -> bytes:
        """
        Create the graph and output it PNG format as a bytes object
        """
        data = self._reshape(data)
        fig, ax = plt.subplots(layout="constrained")
        ax.plot(data["period_start"], data["amount"])
        ax.set_xlabel("Period")
        ax.set_ylabel("Amount")
        ax.set_ylim(ymin=0)
        ax.set_title("Total Amount")

        return self._make_plot(fig)

    def make_barplot(
        self,
        data: list[dict],
        category: str,
        target: str,
        y_label: str | None = None,
        x_label: str | None = None,
        y_min: int = 0,
        y_max: int = None,
    ) -> bytes:
        data = self._reshape(data)
        y_max = y_max or float(max(data[target]))

        fig, ax = plt.subplots(layout="constrained")
        ax.bar(data[category], data[target], align="center")
        ax.set_xlabel(x_label or category)
        ax.set_ylabel(y_label or target)
        ax.set(
            ylim=(y_min, y_max * 1.1),
        )

        #   Add texts
        ax.bar_label(ax.containers[0], label_type='edge')

        return self._make_plot(fig)
