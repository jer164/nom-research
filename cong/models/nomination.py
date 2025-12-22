from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import ClassVar

from cong.models.congress_base import CongressResponseBase, JsonSerializable
from cong.models.member import Chamber, LatestAction
from cong.statics import EST_TZ


class ActionType(Enum):
    COMMITTEE = "Committee"
    REFERRAL = "IntroReferral"
    FLOOR = "Floor"
    CALENDARS = "Calendars"
    DISCHARGE = "Discharge"


class NominationType(Enum):
    MILITARY = "Military"
    CIVILIAN = "Civilian"
    UNKNOWN = "Unknown"

    @classmethod
    def from_dict_key(cls, data: dict) -> "NominationType":
        key_mapping = {"is_civilian": cls.CIVILIAN, "is_military": cls.MILITARY}
        return key_mapping.get(next(iter(data), None), cls.UNKNOWN)


@dataclass
class ActionSummary(JsonSerializable):
    count: int
    url: str


@dataclass
class CommitteeSummary(ActionSummary):
    pass


@dataclass
class HearingSummary(ActionSummary):
    pass


@dataclass
class Committee(JsonSerializable):
    name: str
    system_code: str
    url: str


@dataclass
class Activity(JsonSerializable):
    date: datetime
    name: str

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%dT%H:%M:%SZ").astimezone(EST_TZ)


@dataclass
class DetailedCommittee(CongressResponseBase):
    chamber: Chamber
    name: str
    system_code: str
    type: str
    url: str
    activities: list[Activity] = field(default_factory=list)

    json_key: ClassVar[str] = field(default="committees", init=False, repr=False)

    def __post_init__(self):
        self.chamber = Chamber(self.chamber)
        if isinstance(self.activities, list):
            self.activities = [Activity.from_json(activity) for activity in self.activities]


@dataclass
class Nominee(CongressResponseBase):
    first_name: str
    last_name: str
    middle_name: str
    ordinal: int
    state: str

    json_key: ClassVar[str] = field(default="nominees", init=False, repr=False)


@dataclass
class NomineeAction(CongressResponseBase):
    action_code: str
    action_date: datetime
    text: str
    type: ActionType
    committees: list[Committee] = field(default_factory=list)

    json_key: ClassVar[str] = field(default="actions", init=False, repr=False)

    def __post_init__(self):
        self.type = ActionType(self.type)
        self.action_date = datetime.strptime(self.action_date, "%Y-%m-%d").astimezone(EST_TZ)
        if isinstance(self.committees, list):
            self.committees = [Committee.from_json(committee) for committee in self.committees]


@dataclass
class NomineeSummary(JsonSerializable):
    nominee_count: int
    ordinal: int
    organization: str
    url: str
    position_title: str = field(default=None)
    intro_text: str = field(default="no intro text")


@dataclass
class Nomination(CongressResponseBase):
    citation: str
    congress: int
    nomination_type: NominationType
    number: int
    part_number: str
    url: str
    update_date: datetime
    received_date: datetime | None = field(default_factory=str)
    latest_action: dict = field(default_factory=dict)
    organization: str = field(default="no organization")
    description: str = field(default="no description")

    json_key: ClassVar[str] = field(default="nominations", init=False, repr=False)

    def __post_init__(self):
        self.update_date = datetime.strptime(self.update_date, "%Y-%m-%dT%H:%M:%SZ").astimezone(EST_TZ)
        self.received_date = (
            datetime.strptime(self.received_date, "%Y-%m-%d").astimezone(EST_TZ)
            if self.received_date
            else self.update_date
        )
        if isinstance(self.nomination_type, dict):
            self.nomination_type = NominationType.from_dict_key(self.nomination_type)
        if isinstance(self.latest_action, dict):
            self.latest_action = LatestAction.from_json(self.latest_action)

    @property
    def is_civilian(self) -> bool:
        return self.nomination_type == NominationType.CIVILIAN

    @property
    def is_military(self) -> bool:
        return self.nomination_type == NominationType.MILITARY


@dataclass
class DetailedNomination(CongressResponseBase):
    actions: ActionSummary = field(default=None)
    authority_date: str = field(default=None)
    citation: str = field(default=None)
    committees: CommitteeSummary = field(default=None)
    congress: int = field(default=None)
    hearings: HearingSummary = field(default=None)
    nomination_type: NominationType = field(default=None)
    nominees: NomineeSummary = field(default=None)
    number: int = field(default=None)
    part_number: str = field(default=None)
    update_date: datetime = field(default=None)
    latest_action: LatestAction = field(default=None)
    is_list: bool = field(default=False)
    is_privileged: bool = field(default=False)
    received_date: datetime | None = field(default_factory=str)
    description: str = field(default="no description")
    executive_calendar_number: str = field(default=None)

    json_key: ClassVar[str] = field(default="nomination", init=False, repr=False)

    def __post_init__(self):
        self.update_date = datetime.strptime(self.update_date, "%Y-%m-%dT%H:%M:%SZ").astimezone(EST_TZ)
        self.received_date = datetime.strptime(self.received_date, "%Y-%m-%d").astimezone(EST_TZ)
        self.authority_date = (
            datetime.strptime(self.authority_date, "%Y-%m-%d").astimezone(EST_TZ) if self.authority_date else None
        )
        if isinstance(self.actions, dict):
            self.actions = ActionSummary.from_json(self.actions)
        if isinstance(self.latest_action, dict):
            self.latest_action = LatestAction.from_json(self.latest_action)
        if isinstance(self.nominees, list):
            self.nominees = [NomineeSummary.from_json(nominee) for nominee in self.nominees]
        if isinstance(self.nomination_type, dict):
            self.nomination_type = NominationType.from_dict_key(self.nomination_type)
        if isinstance(self.committees, dict):
            self.committees = CommitteeSummary.from_json(self.committees)
        if isinstance(self.hearings, dict):
            self.hearings = HearingSummary.from_json(self.hearings)

    @property
    def is_civilian(self) -> bool:
        return self.nomination_type == NominationType.CIVILIAN

    @property
    def is_military(self) -> bool:
        return self.nomination_type == NominationType.MILITARY
