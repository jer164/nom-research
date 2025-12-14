from typing import ClassVar

from cong.models.hearing import DetailedHearing, Hearing
from cong.statics import BaseEndpoints
from cong.api.api import CongressAPI, HasSubDirectories

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