"""
Classes and methods for interacting with the Congress API.

Classes:
    HasSubDirectories: A mixin class for building URLs with subdirectories.
    CongressAPI: A base class for interacting with the Congress API.
    NominationAPI: A class for interacting with the Nomination API.
    HearingAPI: A class for interacting with the Hearing API.

Each API class provides methods for fetching data from the respective endpoints.
There is currently no support for pagination.

Dependencies:
    - datetime
    - pytz
    - requests
    - cong.models
    - cong.statics

Example usage:
    api = NominationAPI(api_key="your_api_key")
    nominations = api.get_nominations()
"""

from __future__ import annotations

import itertools
from datetime import datetime
from typing import ClassVar

import grequests
import pytz
import requests

from cong.models import CongressResponseBase, DetailedHearing, Hearing, Nomination, _HearingFromNomination
from cong.statics import BaseEndpoints, log_template


class HasSubDirectories:
    _url: ClassVar[str | None] = None

    def build_url_from_values(self, *values) -> str:
        return f"{self._url}/{'/'.join(map(str, values))}"


class CongressAPI:
    """
    A base class for interacting with the Congress API.

    Attributes:
        _url (str | None): The base URL for the API.
        _return_type (CongressResponseBase): The type of response expected from the API.

    """

    _url: ClassVar[str | None] = None
    _json_key: ClassVar[str | None] = None

    def __init__(self, api_key: str):
        """
        Initializes the CongressAPI with the provided API key.

        Args:
            api_key (str): The API key for authenticating requests.

        """
        self._api_key = api_key
        self.logger = log_template(self.__class__.__qualname__)

    def build_params(
        self,
        offset: int = 0,
        resp_format: str = "json",
        limit: int = 100,
        from_date: datetime | str | None = None,
        to_date: datetime | str | None = None,
        **kwargs,
    ) -> dict:
        """
        Builds the parameters for the API request.

        Args:
            offset (int): The offset for pagination.
            resp_format (str): The format of the response.
            limit (int): The maximum number of results to return.
            from_date (datetime | str | None): The start date for filtering results.
            to_date (datetime | str | None): The end date for filtering results.
            **kwargs: Additional parameters for the request.

        Returns:
            dict: The parameters for the API request.

        """
        return {
            "api_key": self._api_key,
            "offset": offset,
            "format": resp_format,
            "limit": min(limit, 250),
            **self.parse_dates(from_date, to_date),
            **kwargs,
        }

    def parse_dates(self, from_date: datetime | str | None, to_date: datetime | str | None) -> dict[str, str]:
        """
        Parses the from_date and to_date into the required format.

        Args:
            from_date (datetime | str | None): The start date.
            to_date (datetime | str | None): The end date.

        Returns:
            dict[str, str]: The formatted dates.

        """

        def format_date(date):
            if isinstance(date, datetime):
                return date.strftime("%Y-%m-%dT%H:%M:%SZ")
            if isinstance(date, str):
                return (
                    datetime.strptime(date, "%Y-%m-%d")
                    .astimezone(pytz.timezone("US/Eastern"))
                    .strftime("%Y-%m-%dT%H:%M:%SZ")
                )
            return None

        return {
            "fromDateTime": format_date(from_date),
            "toDateTime": format_date(to_date),
        }

    def _get(self, api_url: str, **kwargs) -> list:
        """
        Sends a GET request to the specified API URL.

        Args:
            api_url (str): The URL to send the request to.
            **kwargs: Additional parameters for the request.

        Returns:
            list: The JSON response from the API.

        """
        response = requests.get(api_url, params=self.build_params(**kwargs), timeout=200)
        response.raise_for_status()
        return response.json()

    def _get_async(self, api_urls: list[str], **kwargs) -> str:
        rs = (grequests.get(url=url, params=self.build_params(**kwargs), timeout=200) for url in api_urls)
        reqs = grequests.map(rs, size=5)
        return [r.json() for r in reqs]

    def _parse_response(self, data: dict, return_type: CongressResponseBase) -> list:
        if isinstance(data[return_type.json_key], list):
            return [return_type.from_json(item) for item in data[return_type.json_key]]
        return [return_type.from_json(data[return_type.json_key])]

    def _fetch(self, url: str, return_type: CongressResponseBase, **kwargs) -> list[CongressResponseBase]:
        """
        Fetches data from the specified URL.

        Args:
            url (str): The URL to fetch data from.
            return_type (CongressResponseBase): The type of response expected from the query.
            **kwargs: Additional parameters for the request.

        Returns:
            list: The processed response data.

        """
        self.logger.info("Sending request...")
        data = self._get(url, **kwargs)
        return self._parse_response(data, return_type)

    def _fetch_async(self, urls: list[str], return_type: CongressResponseBase, **kwargs) -> list[CongressResponseBase]:
        """
        Fetches data from the specified URL.

        Args:
            urls (list[str]): The list of URLs to fetch data from.
            return_type (CongressResponseBase): The type of response expected from the query.
            **kwargs: Additional parameters for the request.

        Returns:
            list: The processed response data.

        """
        self.logger.info("Sending request...")
        data = self._get_async(api_urls=urls, **kwargs)
        nested_resp = [self._parse_response(d, return_type) for d in data]
        return list(itertools.chain(*nested_resp))


class NominationAPI(CongressAPI, HasSubDirectories):
    """
    A class for interacting with the Nomination API.

    Attributes:
        _url (str): The base URL for the Nomination API.
        _return_type (CongressResponseBase): The type of response expected from the API.

    """

    _url: ClassVar[str] = BaseEndpoints.NOMINATION.value

    def __init__(self, api_key: str):
        """
        Initializes the NominationAPI with the provided API key.

        Args:
            api_key (str): The API key for authenticating requests.

        """
        super().__init__(api_key=api_key)

    def get_nominations(
        self,
        offset: int = 0,
        from_date: datetime | str | None = None,
        to_date: datetime | str | None = None,
        limit: int = 100,
    ) -> list[Nomination]:
        """
        Fetches nominations from the API.

        Args:
            offset (int): The offset for pagination.
            from_date (datetime | str | None): The start date for filtering results.
            to_date (datetime | str | None): The end date for filtering results.
            limit (int): The maximum number of results to return.

        Returns:
            list[Nomination]: The list of nominations.

        """
        return self._fetch(
            self._url, return_type=Nomination, offset=offset, from_date=from_date, to_date=to_date, limit=limit
        )

    def get_nominations_by_congress(
        self,
        congress: int,
        offset: int = 0,
        from_date: datetime | str | None = None,
        to_date: datetime | str | None = None,
        limit: int = 100,
    ) -> list[Nomination]:
        """
        Fetches nominations by Congress from the API.

        Args:
            congress (int): The Congress number.
            offset (int): The offset for pagination.
            from_date (datetime | str | None): The start date for filtering results.
            to_date (datetime | str | None): The end date for filtering results.
            limit (int): The maximum number of results to return.

        Returns:
            list[Nomination]: The list of nominations.

        """
        return self._fetch(
            self.build_url_from_values(congress),
            return_type=Nomination,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )

    def get_hearings_for_nomination(
        self,
        congress: int,
        nomination_no: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[_HearingFromNomination]:
        """
        Fetches nominations by Congress from the API.

        Args:
            congress (int): The Congress number.
            nomination_no (int): Nomination number.
            offset (int): The offset for pagination.
            limit (int): The maximum number of results to return.

        Returns:
            list[Nomination]: The list of nominations.

        """
        return self._fetch(
            self.build_url_from_values(congress, nomination_no, "hearings"),
            return_type=_HearingFromNomination,
            offset=offset,
            limit=limit,
        )

    def get_hearings_from_nomination_list(
        self,
        congress: int,
        nominations: list[Nomination],
        offset: int = 0,
        limit: int = 100,
    ) -> list[_HearingFromNomination]:
        """
        Fetches nominations by Congress from the API.

        Args:
            congress (int): The Congress number.
            nominations (list[int]): List of nomination numbers.
            offset (int): The offset for pagination.
            limit (int): The maximum number of results to return.

        Returns:
            list[Nomination]: The list of nominations.

        """
        return self._fetch_async(
            [self.build_url_from_values(congress, nom.number, "hearings") for nom in nominations],
            return_type=_HearingFromNomination,
            offset=offset,
            limit=limit,
        )


class HearingAPI(CongressAPI, HasSubDirectories):
    _url: ClassVar[str] = BaseEndpoints.HEARING.value

    def __init__(self, api_key: str):
        """
        Initializes the HearingAPI with the provided API key.

        Args:
            api_key (str): The API key for authenticating requests.
        """  # noqa: D413
        super().__init__(api_key=api_key)

    def get_hearings(self, offset: int = 0, limit: int = 100) -> list[Hearing]:
        """
        Retrieve a list of hearings with pagination support.

        Args:
            offset (int, optional): The starting point for the list of hearings. Defaults to 0.
            limit (int, optional): The maximum number of hearings to return. Defaults to 100.

        Returns:
            list[Hearing]: A list of Hearing objects.

        """
        return self._fetch(self._url, offset=offset, limit=limit, return_type=Hearing)

    def get_hearings_by_congress(self, congress: int, offset: int = 0, limit: int = 100) -> list[Hearing]:
        """
        Retrieve a list of hearings by Congress with pagination support.

        Args:
            congress (int): The Congress number.
            offset (int, optional): The starting point for the list of hearings. Defaults to 0.
            limit (int, optional): The maximum number of hearings to return. Defaults to 100.

        Returns:
            list[Hearing]: A list of Hearing objects.

        """
        return self._fetch(
            self.build_url_from_values(congress),
            return_type=Hearing,
            offset=offset,
            limit=limit,
        )

    def get_detailed_hearing_by_jacket_number(
        self, congress: int, chamber: str, jacket_number: int, offset: int = 0, limit: int = 100
    ) -> list[DetailedHearing]:
        """
        Retrieve a list of hearings by Congress with pagination support.

        Args:
            congress (int): The Congress number.
            chamber (str): The chamber of Congress ('house' or 'senate').
            jacket_number (int): The jacket number of the hearing.
            offset (int, optional): The starting point for the list of hearings. Defaults to 0.
            limit (int, optional): The maximum number of hearings to return. Defaults to 100.

        Returns:
            list[DetailedHearing]: A list of DetailedHearing objects.

        """
        return self._fetch(
            self.build_url_from_values(congress, chamber.lower(), jacket_number),
            return_type=DetailedHearing,
            offset=offset,
            limit=limit,
        )

    def get_detailed_hearings_from_jacket_numbers(
        self, congress: int, chamber: str, jacket_numbers: list[int], offset: int = 0, limit: int = 100
    ) -> list[DetailedHearing]:
        """
        Retrieve a list of hearings by Congress with pagination support.

        Args:
            congress (int): The Congress number.
            chamber (str): The chamber of Congress ('house' or 'senate').
            jacket_numbers (list[int]): The jacket number of the hearing.
            offset (int, optional): The starting point for the list of hearings. Defaults to 0.
            limit (int, optional): The maximum number of hearings to return. Defaults to 100.

        Returns:
            list[DetailedHearing]: A list of DetailedHearing objects.

        """
        return self._fetch_async(
            [self.build_url_from_values(congress, chamber.lower(), jacket) for jacket in jacket_numbers],
            return_type=DetailedHearing,
            offset=offset,
            limit=limit,
        )
