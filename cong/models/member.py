from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from cong.models.congress_base import CongressResponseBase, JsonSerializable


@dataclass
class Depiction(JsonSerializable):
    attribution: str | None = None
    image_url: str | None = None


@dataclass
class Term(JsonSerializable):
    chamber: str
    start_year: int | None = None
    end_year: int | None = None


@dataclass
class DetailedTerm(JsonSerializable):
    chamber: str
    congress: int
    member_type: str
    start_year: int
    state_code: str
    state_name: str
    district: int | None = None
    end_year: int | None = None


@dataclass
class AddressInformation(JsonSerializable):
    city: str
    district: str
    office_address: str
    phone_number: str
    zip_code: int


@dataclass
class PartyHistory(JsonSerializable):
    party_abbreviation: str
    party_name: str
    start_year: int


@dataclass
class PreviousName(JsonSerializable):
    direct_order_name: str
    first_name: str
    honorific_name: str
    inverted_order_name: str
    last_name: str
    middle_name: str
    start_date: str
    end_date: str | None = None


@dataclass
class LegislationInfo(JsonSerializable):
    count: int
    url: str


@dataclass
class Member(CongressResponseBase):
    bioguide_id: str
    name: str
    party_name: str
    state: str
    terms: list[Term]
    update_date: datetime
    url: str
    depiction: Depiction | None = None
    district: int | None = None

    json_key: ClassVar[str] = field(default="members", init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.update_date, str):
            self.update_date = self.format_ts(self.update_date)
        if self.depiction is not None and isinstance(self.depiction, dict):
            self.depiction = Depiction.from_json(self.depiction)
        if isinstance(self.terms, dict):
            self.terms = [Term.from_json(t) for t in self.terms["item"]]


@dataclass
class MemberDetail(CongressResponseBase):
    address_information: AddressInformation
    bioguide_id: str
    birth_year: str
    current_member: bool
    depiction: Depiction
    direct_order_name: str
    first_name: str
    honorific_name: str
    inverted_order_name: str
    last_name: str
    middle_name: str
    official_website_url: str
    party_history: list[PartyHistory]
    previous_names: list[PreviousName]
    state: str
    terms: list[DetailedTerm]
    update_date: str
    cosponsored_legislation: LegislationInfo
    sponsored_legislation: LegislationInfo
    district: int | None = None

    json_key: ClassVar[str] = field(default="member", init=False, repr=False)

    ## TODO: Refactor __post_init__ to reduce repetition across the codebase
    ## Likely need to make a utility function in congress_base.py to handle this pattern
    def __post_init__(self):
        if isinstance(self.update_date, str):
            self.update_date = self.format_ts(self.update_date)

        if isinstance(self.address_information, dict):
            self.address_information = AddressInformation.from_json(self.address_information)

        if isinstance(self.depiction, dict):
            self.depiction = Depiction.from_json(self.depiction)

        if isinstance(self.cosponsored_legislation, dict):
            self.cosponsored_legislation = LegislationInfo.from_json(self.cosponsored_legislation)

        if isinstance(self.sponsored_legislation, dict):
            self.sponsored_legislation = LegislationInfo.from_json(self.sponsored_legislation)

        if self.party_history and isinstance(self.party_history[0], dict):
            self.party_history = [PartyHistory.from_json(p) for p in self.party_history]

        if self.previous_names and isinstance(self.previous_names[0], dict):
            self.previous_names = [PreviousName.from_json(p) for p in self.previous_names]

        if self.terms and isinstance(self.terms[0], dict):
            self.terms = [DetailedTerm.from_json(t) for t in self.terms]


@dataclass
class LatestAction(JsonSerializable):
    action_date: str
    text: str
    action_time: str | None = None


##TODO: Create enum for policy areas
@dataclass
class PolicyArea(JsonSerializable):
    name: str


@dataclass
class SponsoredLegislation(CongressResponseBase):
    congress: int
    introduced_date: str
    latest_action: LatestAction
    type: str
    url: str
    policy_area: PolicyArea | None = None
    title: str | None = None
    number: str | None = None
    amendment_number: str | None = None

    json_key: ClassVar[str] = field(default="sponsoredLegislation", init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.latest_action, dict):
            self.latest_action = LatestAction.from_json(self.latest_action)
        if self.policy_area is not None and isinstance(self.policy_area, dict):
            self.policy_area = PolicyArea.from_json(self.policy_area)


@dataclass
class CosponsoredLegislation(SponsoredLegislation):
    json_key: ClassVar[str] = field(default="cosponsoredLegislation", init=False, repr=False)
