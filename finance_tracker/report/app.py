"""
Reporting front-end
"""

import base64
from dataclasses import dataclass
from typing import Any

from flask import (
    Flask,
    render_template,
    request,
)
from sqlalchemy import text

from finance_tracker.report.summary import (
    SummaryMetrics,
    SummaryPlot,
)


app = Flask(__name__)


@dataclass
class Filter:
    name: str
    data: tuple[Any, Any]
    type: str = "single"
    default: Any | None = None

    def __post_init__(self):
        assert self.type in ("single", "multi")
        if self.default:
            assert self.default in (item for item, _ in self.data)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/summary/")
def summary():
    with app.config.engine.begin() as con:
        accounts = con.execute(text("select id, name from account")).all()
        periods = con.execute(text("select id, code from period order by code")).all()

    account_id = request.args.get("account")
    account_id = int(account_id) if account_id else accounts[0][0]
    period_id = request.args.get("period")
    period_id = int(period_id) if period_id else periods[-1][0]

    filters = [
        Filter(
            name="account",
            data=[(id, name) for id, name in accounts],
            default=account_id,
        ),
        Filter(
            name="period",
            data=[(id, name) for id, name, in periods],
            default=period_id,
        ),
    ]

    metrics = SummaryMetrics.from_engine(
        app.config.engine,
        account_id=account_id,
        period_id=period_id,
    )
    plot_bytes = SummaryPlot.from_engine(
        app.config.engine,
        account_id=account_id,
        period_id=period_id,
    )
    plot = base64.b64encode(plot_bytes.plot_svg).decode("utf-8")
    return render_template("summary.html", metrics=metrics, plot=plot, filters=filters)
