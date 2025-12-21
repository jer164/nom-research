from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

import requests

from cong.models.congress_base import CongressResponseBase, JsonSerializable
from cong.models.nomination import Committee
from cong.models.member import Chamber
from cong.statics import EST_TZ


@dataclass
class AssociatedMeeting(JsonSerializable):
    event_id: str
    url: str


@dataclass
class Hearing(CongressResponseBase):
    chamber: Chamber
    congress: str
    jacket_number: int
    update_date: datetime
    url: str
    number: int | None = None
    part: str | None = None

    json_key: ClassVar[str] = field(default="hearings", init=False, repr=False)

    def __post_init__(self):
        self.chamber = Chamber(self.chamber)
        if isinstance(self.update_date, str):
            self.update_date = datetime.strptime(
                self.update_date, "%Y-%m-%dT%H:%M:%SZ"
            ).astimezone(EST_TZ)


@dataclass
class HearingFromNomination(CongressResponseBase):
    chamber: Chamber
    citation: str
    date: datetime
    jacket_number: int
    number: int

    json_key: ClassVar[str] = field(default="hearings", init=False, repr=False)

    def __post_init__(self):
        self.chamber = Chamber(self.chamber)
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").astimezone(EST_TZ)


@dataclass
class HearingTranscript:
    type: str
    url: str


@dataclass
class DetailedHearing(CongressResponseBase):
    chamber: Chamber
    citation: str
    congress: int
    formats: list[HearingTranscript]
    jacket_number: int
    library_of_congress_identifier: str
    update_date: datetime
    part: str | None = None
    title: str | None = None
    committees: list[Committee] = field(default_factory=list)
    number: int | None = None  ### this may not exist
    dates: list[dict[str, datetime]] = field(default_factory=list)
    associated_meeting: AssociatedMeeting = field(
        default_factory=lambda: AssociatedMeeting(event_id=None, url=None)
    )

    json_key: ClassVar[str] = field(default="hearing", init=False, repr=False)

    def __post_init__(self):
        self.chamber = Chamber(self.chamber)
        self.formats = [HearingTranscript(**f) for f in self.formats]
        if isinstance(self.dates, list):
            self.dates = [
                {"date": datetime.strptime(d["date"], "%Y-%m-%d").astimezone(EST_TZ)}
                for d in self.dates
            ]
        if isinstance(self.update_date, str):
            self.update_date = datetime.strptime(
                self.update_date, "%Y-%m-%dT%H:%M:%SZ"
            ).astimezone(EST_TZ)
        if isinstance(self.associated_meeting, dict):
            self.associated_meeting = AssociatedMeeting.from_json(
                self.associated_meeting
            )
        if isinstance(self.committees, list):
            self.committees = [Committee.from_json(c) for c in self.committees]

    @property
    def hearing_text(self) -> str:
        txt_url = next(
            (t.url for t in self.formats if t.type == "Formatted Text"), None
        )
        if txt_url is not None:
            response = requests.get(txt_url, timeout=200)
            response.raise_for_status()
            return response.text
        msg = "No valid text data found."
        raise AttributeError(msg)
