"""
Reporting front-end
"""

from flask import (
    Flask,
    render_template,
)

from finance_tracker.report.summary import SummaryMetrics


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/summary/")
def summary():
    metrics = SummaryMetrics.from_engine(app.config.engine)
    return render_template("summary.html", metrics=metrics)
