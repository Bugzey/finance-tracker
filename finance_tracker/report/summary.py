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

from dataclasses import dataclass, fields
import datetime as dt
import io
from typing import Self

import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy.engine import Engine
from sqlalchemy import text


matplotlib.use("svg")

SUMMARY_QUERY = """-- # noqa
with base as
(
    select
        sum(case when per.period_start = :period then tran.amount end) as current_month_total
        , sum(case when per.period_start = :previous_month_period then tran.amount end) as previous_month_total
        , sum(case when per.period_start = :previous_year_period then tran.amount end) as previous_year_total
    from
        "transaction" tran

        left join period per
        on tran.period_id = per.id

    where
        1 = 1
        and tran.account_id = :account_id
)

select
    base.current_month_total
    , base.previous_month_total
    , base.current_month_total - base.previous_month_total as month_over_month_difference
    , (base.current_month_total - base.previous_month_total ) / base.previous_month_total as month_over_month_percent
    , base.previous_year_total
    , (base.current_month_total - base.previous_year_total) as year_over_year_difference
    , (base.current_month_total - base.previous_year_total) / base.previous_year_total as year_over_year_percent

from
    base;
"""


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
    current_month_total: float
    previous_month_total: float
    previous_year_total: float

    month_over_month_difference: float
    month_over_month_percent: float
    year_over_year_difference: float
    year_over_year_percent: float

    def __post_init__(self):
        for item in fields(self):
            if item.type in (int, float):
                self.__dict__[item.name] = self.__dict__[item.name] or 0.0

    @classmethod
    def from_engine(
        cls,
        engine: Engine,
        account_id: int = 1,
        period_id: int | None = None,
    ) -> Self:
        #   Test - pass a query
        with engine.begin() as con:
            if period_id:
                period = con.execute(
                    text("select period_start from period where id = :id"),
                    parameters={"id": period_id},
                ).scalar()
                period = dt.date.fromisoformat(period)
            else:
                period = dt.date.today().replace(day=1)

            previous_month = (period - dt.timedelta(days=1)).replace(day=1)
            previous_year = period.replace(year=period.year - 1)

            result = con.execute(
                text(SUMMARY_QUERY),
                parameters=dict(
                    account_id=account_id,
                    period=period,
                    previous_month_period=previous_month,
                    previous_year_period=previous_year,
                ),
            ).fetchone()

        return cls(**result._mapping)


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
        ax.set_title("Total Amount")

        with io.BytesIO() as cur_file:
            _ = fig.savefig(cur_file, format="png")
            cur_file.seek(0)
            result = cur_file.read()

        return result
