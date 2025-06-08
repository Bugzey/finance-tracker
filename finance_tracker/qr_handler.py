"""
Handle Bulgarian receipt-style QR codes

Format:
    <business_code>*<transaction_code>*<date>*<time>*<sum bgn>
"""

from dataclasses import dataclass
import datetime as dt
import logging
from typing import Self
import sys

import cv2 as cv


QR_FORMAT = "<business_code>*<transaction_code>*<date>*<time>*<sum>"
logger = logging.getLogger(__name__)


def create_capture(source: int | str = 0) -> cv.VideoCapture:
    if isinstance(source, str):
        capture = cv.VideoCapture(source)
    elif sys.platform == "windows":
        capture = cv.VideoCapture(source, cv.CAP_DSHOW)
    elif sys.platform == "linux":
        capture = cv.VideoCapture(source, cv.CAP_V4L2)
    else:
        #   Set default device and hope for the best
        capture = cv.VideoCapture(source)

    #   Try setting codec and resolution
    #   Query available codecs:
    #   Set codec in OpenCV: https://forum.opencv.org/t/cv-videocapture-api-backend-issue/9522/3
    capture.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc("M", "J", "P", "G"))
    capture.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    return capture


def get_qr_from_video(capture: cv.VideoCapture) -> str:
    """
    Start the default video capture device and detect a single QR code using OpenCV
    """
    detector = cv.QRCodeDetector()
    data = None

    while True:
        try:
            has_frame, img = capture.read()
            if has_frame:
                data, _, has_detection = detector.detectAndDecode(img)
                if has_detection is not None:
                    break
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            break
        except Exception as e:
            logger.error(e)
            capture.release()
            raise

    return data


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
        self.datetime = self.datetime or dt.datetime(
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

        items = {
            key: value
            for key, value
            in zip(("business_code", "transaction_code", "date", "time", "amount"), items)
        }
        items["date"] = dt.date.fromisoformat(items["date"])
        items["time"] = dt.time.fromisoformat(items["time"])
        items["amount"] = float(items["amount"])
        return cls(**items)
