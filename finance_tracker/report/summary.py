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

from dataclasses import dataclass
import datetime as dt
from typing import Self

from sqlalchemy.engine import Engine
from sqlalchemy import text


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


@dataclass
class SummaryMetrics:
    current_month_total: float
    previous_month_total: float
    previous_year_total: float

    month_over_month_difference: float
    month_over_month_percent: float
    year_over_year_difference: float
    year_over_year_percent: float

    @classmethod
    def from_engine(
        cls,
        engine: Engine,
        account_id: int = 1,
        period: dt.date | None = None,
    ) -> Self:
        #   Test - pass a query
        if not period:
            period = dt.date.today().replace(day=1)

        previous_month = (period - dt.timedelta(days=1)).replace(day=1)
        previous_year = period.replace(year=period.year - 1)

        with engine.begin() as con:
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
