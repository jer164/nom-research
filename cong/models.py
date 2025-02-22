from __future__ import annotations

from dataclasses import asdict as dc_to_dict
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

import humps
from pyspark.sql import Row

from cong.statics import EST_TZ


@dataclass
class CongressResponseBase:
    json_key: ClassVar[str | None] = field(default=None, init=False, repr=False)

    @classmethod
    def from_json(cls, data: dict) -> CongressResponseBase:
        snake_case = humps.decamelize(data)
        return cls(**snake_case)

    def to_json(self) -> dict:
        to_dict = dc_to_dict(self)
        return humps.camelize(to_dict)

    def to_row(self) -> Row:
        return Row(**self.to_json())

    def format_ts(self, str_ts: str) -> datetime:
        valid_ts = ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]
        for ts in valid_ts:
            try:
                return datetime.strptime(str_ts, ts).astimezone(EST_TZ)
            except ValueError:
                continue
        msg = f"passed {str_ts} does not conform to expected ts formats."
        raise ValueError(msg)


@dataclass
class Nomination(CongressResponseBase):
    citation: str
    congress: int
    latest_action: dict
    nomination_type: dict
    number: int
    organization: str
    part_number: str
    received_date: datetime
    update_date: datetime
    url: str
    description: str = field(default="no description")

    json_key: ClassVar[str] = field(default="nominations", init=False, repr=False)

    def __post_init__(self):
        self.received_date = datetime.strptime(self.received_date, "%Y-%m-%d").astimezone(EST_TZ)
        self.update_date = datetime.strptime(self.update_date, "%Y-%m-%dT%H:%M:%SZ").astimezone(EST_TZ)

    @property
    def is_military(self):
        return not "isMilitary" not in self.nomination_type


@dataclass
class Hearing(CongressResponseBase):
    chamber: str
    congress: str
    jacket_number: int
    update_date: datetime
    url: str

    json_key: ClassVar[str] = field(default="hearings", init=False, repr=False)


@dataclass
class _HearingFromNomination(CongressResponseBase):
    chamber: str
    citation: str
    date: datetime
    jacket_number: int
    number: int

    json_key: ClassVar[str] = field(default="hearings", init=False, repr=False)


@dataclass
class HearingTranscript:
    type: str
    url: str


@dataclass
class DetailedHearing(CongressResponseBase):
    number: int
    chamber: str
    citation: str
    committees: list
    congress: int
    dates: list[datetime]
    formats: list[HearingTranscript]
    jacket_number: int
    library_of_congress_identifier: str
    title: str
    update_date: datetime
    associated_meeting: dict = field(default_factory=dict)

    json_key: ClassVar[str] = field(default="hearing", init=False, repr=False)

    def __post_init__(self):
        self.formats = [HearingTranscript(**f) for f in self.formats]

    @property
    def hearing_text(self) -> str:
        import requests
        txt_url = next((t.url for t in self.formats if t.type == "Formatted Text"), None)
        if txt_url is not None:
            response = requests.get(txt_url, timeout=200)
            response.raise_for_status()
            return response.text
        msg = "No valid text data found."
        raise AttributeError(msg)
