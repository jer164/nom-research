from __future__ import annotations

import itertools
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

import grequests
import pytz
import requests

from cong.statics import SUCCESS_STATUS, log_template

if TYPE_CHECKING:
    from cong.models.congress_base import CongressResponseBase


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

    def _get_endpoint_max(self, endpoint: str) -> int:
        response = self._get(endpoint, limit=1)
        return response["pagination"]["count"]

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

    ## TODO: Refactor this so it can processes cases where the base_url
    ## has different parameters. Currently assumes same paths.
    def _build_async_requests(self, base_url: str, max_row_count: int, **kwargs) -> list[str]:
        async_requests = []
        reqs_needed = (max_row_count // 250) + (1 if max_row_count % 250 > 0 else 0)
        for i in range(reqs_needed):
            offset = i * 250
            async_requests.append(
                {
                    "url": base_url,
                    "params": self.build_params(offset=offset, limit=250, **kwargs),
                }
            )
        return async_requests  ### need to make this its own object probably

    def _get_async(self, request_list: list[dict]) -> list[dict]:
        responses = []
        rs = (grequests.get(url=req["url"], params=req["params"], timeout=30) for req in request_list)
        reqs = grequests.map(rs, size=50)
        for r in reqs:
            if r.status_code != SUCCESS_STATUS:
                r.raise_for_status()
            else:
                responses.append(r.json())
        return responses

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
        response_size = len(data[return_type.json_key]) if isinstance(data[return_type.json_key], list) else 1
        self.logger.info(
            "Request successful; returned %d %s.", response_size, "record" if response_size == 1 else "records"
        )
        return self._parse_response(data, return_type)

    def _fetch_async(
        self, request_list: list[dict], return_type: CongressResponseBase, sort_key: str | None = None, **kwargs
    ) -> list[CongressResponseBase]:
        """
        Fetches data from the specified URL.

        Args:
            request_list (list[dict]): The list of requests to send.
            return_type (CongressResponseBase): The type of response expected from the query.
            sort_key (str | None): The key to sort the results by.
            **kwargs: Additional parameters for the request.

        Returns:
            list: The processed response data.

        """
        self.logger.info("Sending %d batches of 50 parallel requests", len(request_list) // 50 + 1)
        self.logger.info("Session may timeout if token encounters rate limits.")
        data = self._get_async(request_list=request_list, **kwargs)
        nested_resp = [self._parse_response(d, return_type) for d in data]
        self.logger.info("All requests successful; returned %d records.", sum(len(r) for r in nested_resp))
        return (
            list(itertools.chain(*nested_resp))
            if sort_key is None
            else sorted(itertools.chain(*nested_resp), key=lambda x: getattr(x, sort_key))
        )
