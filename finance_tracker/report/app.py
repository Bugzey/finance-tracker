"""
Reporting front-end
"""

import base64

from flask import (
    Flask,
    render_template,
    request,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from finance_tracker.models import (
    AccountModel,
    PeriodModel,
)
from finance_tracker.report.summary import (
    SummaryMetrics,
    SummaryPlot,
)


app = Flask(__name__)


def get_accounts(sess: Session) -> dict[int, str]:
    query = (
        select(AccountModel.id, AccountModel.name)
        .order_by(AccountModel.id)
    )
    data = sess.execute(query).all()
    result = {item.id: item.name for item in data}
    return result


def get_periods(sess: Session) -> dict[int, str]:
    query = (
        select(PeriodModel.id, PeriodModel.period_start)
        .order_by(PeriodModel.period_start)
    )
    data = sess.execute(query).all()
    result = {item.id: item.period_start.isoformat() for item in data}
    return result


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/summary/", methods=["GET", "POST"])
def summary():
    with Session(app.config.engine) as sess:
        periods = get_periods(sess)
        accounts = get_accounts(sess)
        period_id = int(request.form.get("period") or list(periods.keys())[-1])
        account_id = int(request.form.get("account") or list(accounts.keys())[0])

        metrics = SummaryMetrics(sess, period_id=period_id, account_id=account_id)
        current_month_spend = metrics.current_month_total()
        last_month_spend = metrics.previous_month_total()
        previous_year_spend = metrics.previous_year_total()
        top_businesses = metrics.top_businesses() or []
        top_categories = metrics.top_categories() or []

    #   Format items
    top_businesses_header = [
        item.replace("_", " ").title()
        for item
        in top_businesses[0]._fields
    ] if top_businesses else []
    top_categories_header = [
        item.replace("_", " ").title()
        for item
        in top_categories[0]._fields
    ] if top_categories else []

    return render_template(
        "summary.html",
        #   Filters
        period_values=periods,
        period_selected=period_id,
        account_values=accounts,
        account_selected=account_id,

        #   Metrics
        current_month_spend=current_month_spend,
        last_month_spend=last_month_spend,
        previous_year_spend=previous_year_spend,

        #   Tables
        top_businesses_headers=top_businesses_header,
        top_businesses_data=top_businesses,
        top_categories_headers=top_categories_header,
        top_categories_data=top_categories,
    )

    plot_bytes = SummaryPlot.from_engine(
        app.config.engine,
        account_id=account_id,
        period_id=period_id,
    )
    _ = base64.b64encode(plot_bytes.plot_svg).decode("utf-8")
