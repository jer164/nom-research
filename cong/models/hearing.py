from dataclasses import dataclass, field
from typing import ClassVar
from datetime import datetime

from cong.models.congress_base import CongressResponseBase

@dataclass
class Hearing(CongressResponseBase):
    chamber: str
    congress: str
    jacket_number: int
    update_date: datetime
    url: str
    number: int | None = None

    json_key: ClassVar[str] = field(default="hearings", init=False, repr=False)


@dataclass
class HearingFromNomination(CongressResponseBase):
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
