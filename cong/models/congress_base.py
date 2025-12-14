from __future__ import annotations

from dataclasses import asdict as dc_to_dict
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

import humps
from pyspark.sql import Row

from cong.statics import EST_TZ


@dataclass
class Pagination:
    count: int
    next: str | None = None

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
    

