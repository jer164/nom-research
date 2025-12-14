from dataclasses import dataclass, field
from typing import ClassVar
from datetime import datetime

import humps

from cong.models.congress_base import CongressResponseBase


@dataclass
class Depiction:
    attribution: str | None = None
    image_url: str | None = None


@dataclass
class Term:
    chamber: str
    start_year: int | None = None
    end_year: int | None = None
    start: int | None = None
    end: int | None = None


@dataclass
class Terms:
    item: list[Term] = field(default_factory=list)

    def __post_init__(self):
        if self.item and isinstance(self.item, list) and isinstance(self.item[0], dict):
            self.item = [Term(**t) for t in self.item]


@dataclass
class Member(CongressResponseBase):
    bioguide_id: str
    name: str
    party_name: str
    state: str
    terms: Terms
    update_date: datetime
    url: str
    depiction: Depiction | None = None
    district: int | None = None


    json_key: ClassVar[str] = field(default="members", init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.update_date, str):
            self.update_date = self.format_ts(self.update_date)
        if self.depiction is not None and isinstance(self.depiction, dict):
            self.depiction = Depiction(**humps.decamelize(self.depiction))
        if isinstance(self.terms, dict):
            self.terms = Terms(**humps.decamelize(self.terms))
