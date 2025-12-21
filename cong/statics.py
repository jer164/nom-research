import logging
from enum import Enum

import pytz

EST_TZ = pytz.timezone("US/Eastern")

URL_BASE = "https://api.congress.gov/v3"


def log_template(name: str):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="[%(asctime)s | %(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class BaseEndpoints(Enum):
    BILL = f"{URL_BASE}/bill"
    AMENDMENTS = f"{URL_BASE}/amendment"
    SUMMARIES = f"{URL_BASE}/summaries"
    CONGRESS = f"{URL_BASE}/congress"
    MEMBER = f"{URL_BASE}/member"
    COMMITTEE = f"{URL_BASE}/committee"
    COMMITTEE_REPORT = f"{URL_BASE}/committee-report"
    COMMITTEE_PRINT = f"{URL_BASE}/committee-print"
    COMMITTEE_MEETING = f"{URL_BASE}/committee-meeting"
    HEARING = f"{URL_BASE}/hearing"
    CONGRESSIONAL_RECORD = f"{URL_BASE}/congressional-record"
    DAILY_CONGRESSIONAL_RECORD = f"{URL_BASE}/daily-congressional-record"
    BOUND_CONGRESSIONAL_RECORD = f"{URL_BASE}/bound-congressional-record"
    HOUSE_COMMUNICATION = f"{URL_BASE}/house-communication"
    HOUSE_REQUIREMENT = f"{URL_BASE}/house-requirement"
    SENATE_COMMUNICATION = f"{URL_BASE}/senate-communication"
    NOMINATION = f"{URL_BASE}/nomination"
    TREATY = f"{URL_BASE}/treaty"
