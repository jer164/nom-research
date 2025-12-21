from __future__ import annotations

from dataclasses import asdict as dc_to_dict
from dataclasses import dataclass, field, is_dataclass
from datetime import datetime
from typing import ClassVar
import humps
from pyspark.sql import Row

from cong.statics import EST_TZ


class CanParseAttributes:
    """Mixin to provide casing conversion utilities for dataclasses."""

    @staticmethod
    def case_from_json(data: dict) -> dict:
        """Convert camelCase keys from JSON to snake_case for Python."""
        return humps.decamelize(data)

    @staticmethod
    def case_for_json(data: dict) -> dict:
        """Convert snake_case keys from Python to camelCase for JSON."""
        if is_dataclass(data):
            return humps.camelize(dc_to_dict(data))
        return humps.camelize(data)


class JsonSerializable(CanParseAttributes):
    """Mixin to provide JSON serialization/deserialization for dataclasses."""

    @classmethod
    def from_json(cls, data: dict) -> JsonSerializable:
        """Create instance from JSON data with automatic case conversion."""
        return cls(**cls.case_from_json(data))

    def to_json(self) -> dict:
        """Convert instance to JSON-compatible dict with automatic case conversion."""
        return self.case_for_json(self)


@dataclass
class Pagination:
    count: int
    next: str | None = None

@dataclass
class CongressResponseBase(JsonSerializable):

    json_key: ClassVar[str | None] = field(default=None, init=False, repr=False)

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
    

