from datetime import datetime
from typing import ClassVar

from dataclasses import dataclass, field

from cong.models.congress_base import CongressResponseBase
from cong.statics import EST_TZ


@dataclass
class Nomination(CongressResponseBase):
    citation: str
    congress: int
    nomination_type: dict
    number: int
    part_number: str
    update_date: datetime
    url: str
    received_date: datetime | None = field(default_factory=str)
    latest_action: dict = field(default_factory=dict)
    organization: str = field(default="no organization")
    description: str = field(default="no description")

    json_key: ClassVar[str] = field(default="nominations", init=False, repr=False)

    def __post_init__(self):
        self.update_date = datetime.strptime(
            self.update_date, "%Y-%m-%dT%H:%M:%SZ"
        ).astimezone(EST_TZ)
        self.received_date = (
            datetime.strptime(self.received_date, "%Y-%m-%d").astimezone(EST_TZ)
            if self.received_date
            else self.update_date
        )

    @property
    def is_military(self):
        return not "isMilitary" not in self.nomination_type
