import os
from enum import Enum

import pytz
from dotenv import load_dotenv

load_dotenv()

EST_TZ = pytz.timezone("US/Eastern")

URL_BASE = os.getenv("CONGRESS_V3_API_BASE")


class BaseEndpoints(Enum):
    BILL: str = f"{URL_BASE}/bill"
    AMENDMENTS: str = f"{URL_BASE}/amendment"
    SUMMARIES: str = f"{URL_BASE}/summaries"
    COMGRESS: str = f"{URL_BASE}/congress"
    MEMBER: str = f"{URL_BASE}/member"
    COMMITTEE: str = f"{URL_BASE}/committee"
    COMMITTEE_REPORT: str = f"{URL_BASE}/committee-report"
    COMMITTEE_PRINT: str = f"{URL_BASE}/committee-print"
    COMMITTEE_MEETING: str = f"{URL_BASE}/committee-meeting"
    HEARING: str = f"{URL_BASE}/hearing"
    CONGRESSIONAL_RECORD: str = f"{URL_BASE}/congressional-record"
    DAILY_CONGRESSIONAL_RECORD: str = f"{URL_BASE}/daily-congressional-record"
    BOUND_CONGRESSIONAL_RECORD: str = f"{URL_BASE}/bound-congressional-record"
    HOUSE_COMMUNICATION: str = f"{URL_BASE}/house-communication"
    HOUSE_REQUIREMENT: str = f"{URL_BASE}/house-requirement"
    SENATE_COMMUNICATION: str = f"{URL_BASE}/senate-communication"
    NOMINATION: str = f"{URL_BASE}/nomination"
    TREATY: str = f"{URL_BASE}/treaty"
