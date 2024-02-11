"""
Reporting front-end
"""

import base64

from flask import (
    Flask,
    render_template,
)

from finance_tracker.report.summary import (
    SummaryMetrics,
    SummaryPlot,
)


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/summary/")
def summary():
    metrics = SummaryMetrics.from_engine(app.config.engine)
    plot_bytes = SummaryPlot.from_engine(app.config.engine)
    plot = base64.b64encode(plot_bytes.plot_svg).decode("utf-8")
    return render_template("summary.html", metrics=metrics, plot=plot)
