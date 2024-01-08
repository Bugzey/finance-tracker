"""
Handle Bulgarian receipt-style QR codes

Format:
    <business_code>*<transaction_code>*<date>*<time>*<sum bgn>
"""

from dataclasses import dataclass
import datetime as dt
from typing import Self


QR_FORMAT = "<business_code>*<transaction_code>*<date>*<time>*<sum>"


@dataclass
class QRData:
    """
    Class that contains parsed QR Code data - correct fields in the correct type
    """
    business_code: str
    transaction_code: str
    date: dt.date
    time: dt.time
    amount: float
    datetime: dt.datetime | None = None

    def __post_init__(self):
        """
        Apply type handling
        """
        self.date = dt.date.fromisoformat(self.date)
        self.time = dt.time.fromisoformat(self.time)
        self.amount = float(self.amount)
        self.datetime = dt.datetime(
            self.date.year,
            self.date.month,
            self.date.day,
            self.time.hour,
            self.time.minute,
            self.time.second,
        )

    @classmethod
    def from_string(cls, data: str) -> Self:
        items = data.split("*")
        if len(items) != 5:
            raise ValueError(f"Unknown QR format: {data}. Expected: {QR_FORMAT}")
        return cls(*items)
