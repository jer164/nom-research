from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

import requests
from pyspark.sql import Row

from cong.statics import EST_TZ


@dataclass
class CongressBaseResponse(ABC):
    json_key: ClassVar[str | None] = field(default=None, init=False, repr=False)

    @abstractmethod
    def to_json(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_json(cls, data: dict) -> CongressBaseResponse:
        pass

    def to_row(self) -> Row:
        return Row(**self.to_json())


@dataclass
class Nomination(CongressBaseResponse):
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

    json_key: ClassVar[str] = field(default="nominations", init=False, repr=False)

    @property
    def is_military(self):
        return not "isMilitary" not in self.nomination_type

    @classmethod
    def from_json(cls, data: dict) -> Nomination:
        return cls(
            citation=data["citation"],
            congress=data["congress"],
            latest_action=data["latestAction"],
            nomination_type=data["nominationType"],
            number=data["number"],
            organization=data["organization"],
            part_number=data["partNumber"],
            received_date=datetime.strptime(data["receivedDate"], "%Y-%m-%d").astimezone(EST_TZ),
            update_date=datetime.strptime(data["updateDate"], "%Y-%m-%dT%H:%M:%SZ").astimezone(EST_TZ),
            url=data["url"],
        )

    def to_json(self) -> dict:
        return {
            "citation": self.citation,
            "congress": self.congress,
            "latestAction": self.latest_action,
            "nominationType": self.nomination_type,
            "number": self.number,
            "organization": self.organization,
            "partNumber": self.part_number,
            "receivedDate": self.received_date.strftime("%Y-%m-%d"),
            "updateDate": self.update_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "url": self.url,
        }


@dataclass
class Hearing(CongressBaseResponse):
    chamber: str
    congress: str
    jacket_number: int
    update_date: datetime
    url: str

    json_key: ClassVar[str] = field(default="hearings", init=False, repr=False)

    @classmethod
    def from_json(cls, data: dict) -> Hearing:
        return cls(
            chamber=data["chamber"],
            congress=data["congress"],
            jacket_number=data["jacketNumber"],
            update_date=datetime.strptime(data["updateDate"], "%Y-%m-%dT%H:%M:%SZ").astimezone(EST_TZ),
            url=data["url"],
        )

    def to_json(self) -> dict:
        return {
            "chamber": self.chamber,
            "congress": self.congress,
            "updateDate": self.update_date.strftime("%Y-%m-%d"),
            "jacketNumber": self.jacket_number,
            "url": self.url,
        }


@dataclass
class _HearingFromNomination(CongressBaseResponse):
    chamber: str
    citation: str
    date: datetime
    jacket_number: int
    number: int

    json_key: ClassVar[str] = field(default="hearings", init=False, repr=False)

    @classmethod
    def from_json(cls, data: dict) -> Hearing:
        return cls(
            chamber=data["chamber"],
            citation=data["citation"],
            date=datetime.strptime(data["date"], "%Y-%m-%d").astimezone(EST_TZ),
            jacket_number=data["jacketNumber"],
            number=data["number"],
        )

    def to_json(self) -> dict:
        ### create a method to handle this for all cases cuz it can be done
        return {
            "chamber": self.chamber,
            "citation": self.citation,
            "date": self.date.strftime("%Y-%m-%d"),
            "jacketNumber": self.jacket_number,
            "number": self.number,
        }


@dataclass
class HearingTranscript:
    type: str
    url: str


@dataclass
class DetailedHearing(CongressBaseResponse):
    associated_meeting: dict
    chamber: str
    citation: str
    committees: list[HearingTranscript]
    congress: int
    dates: list[datetime]
    formats: list[HearingTranscript]
    jacket_number: int
    library_of_congress_identifier: str
    title: str
    update_date: datetime

    json_key: ClassVar[str] = field(default="hearing", init=False, repr=False)

    @classmethod
    def from_json(cls, data: dict) -> DetailedHearing:
        return cls(
            associated_meeting=data["associatedMeeting"],
            chamber=data["chamber"],
            citation=data["citation"],
            committees=data["committees"],
            congress=data["congress"],
            dates=[datetime.strptime(date["date"], "%Y-%m-%d").astimezone(EST_TZ) for date in data["dates"]],
            formats=[HearingTranscript(**f) for f in data["formats"]],
            jacket_number=data["jacketNumber"],
            library_of_congress_identifier=data["libraryOfCongressIdentifier"],
            title=data["title"],
            update_date=datetime.strptime(data["updateDate"], "%Y-%m-%dT%H:%M:%SZ").astimezone(EST_TZ),
        )

    def to_json(self) -> dict:
        return {
            "associatedMeeting": self.associated_meeting,
            "chamber": self.chamber,
            "citation": self.citation,
            "committees": self.committees,
            "congress": self.congress,
            "dates": [date.strftime("%Y-%m-%d") for date in self.dates],
            "formats": self.formats,
            "jacketNumber": self.jacket_number,
            "libraryOfCongressIdentifier": self.library_of_congress_identifier,
            "title": self.title,
            "updateDate": self.update_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    @property
    def hearing_text(self) -> str:
        txt_url = next((t.url for t in self.formats if t.type == "Formatted Text"), None)
        if txt_url is not None:
            response = requests.get(txt_url, timeout=200)
            response.raise_for_status()
            return response.text
        msg = "No valid text data found."
        raise AttributeError(msg)
