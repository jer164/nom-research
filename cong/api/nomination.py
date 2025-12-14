from datetime import datetime
from typing import ClassVar


from cong.api.api import HasSubDirectories, CongressAPI
from cong.models.hearing import _HearingFromNomination, DetailedHearing, Hearing
from cong.models.nomination import Nomination
from cong.statics import BaseEndpoints


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
            self._url,
            return_type=Nomination,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
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
            [
                self.build_url_from_values(congress, nom.number, "hearings")
                for nom in nominations
            ],
            return_type=_HearingFromNomination,
            offset=offset,
            limit=limit,
        )
