
from __future__ import annotations

import itertools
from datetime import datetime
from typing import ClassVar

import grequests
import pytz
import requests

from cong.models.congress_base import CongressResponseBase
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

    def _fetch_all(self, url: str, return_type: CongressResponseBase, stop_after: int | None = None, **kwargs) -> list[CongressResponseBase]:
        """
        Fetches all data from the specified URL, handling pagination.

        Args:
            url (str): The URL to fetch data from.
            return_type (CongressResponseBase): The type of response expected from the query.
            stop_after (int | None): Maximum number of pages to fetch.
            **kwargs: Additional parameters for the request.
        
        Returns:
            list: The processed response data.

        """
        all_data = []
        page_count = 0
        next_url = url
        
        while next_url and (stop_after is None or page_count < stop_after):
            page_count += 1
            
            if page_count == 1:
                self.logger.info("Sending initial request...")
            else:
                limit = kwargs.get("limit", 100)
                count = data.get("pagination", {}).get("count", 0)
                total_pages = (count + limit - 1) // limit
                self.logger.info(f"Fetching page {page_count}/{total_pages}...")
            
            data = self._get(next_url, **kwargs)
            all_data.extend(self._parse_response(data, return_type))
            next_url = data.get("pagination", {}).get("next")
        
        return all_data

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
