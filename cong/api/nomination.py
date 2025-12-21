from datetime import datetime
from typing import ClassVar

from cong.api.api import CongressAPI, HasSubDirectories
from cong.models.hearing import HearingFromNomination
from cong.models.nomination import Nomination, Nominee, DetailedNomination, NomineeAction, DetailedCommittee
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
        retrieve_all: bool = False,
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
        if retrieve_all:
            base_endpoint = self.build_url_from_values(congress)
            max_rows = self._get_endpoint_max(base_endpoint)
            async_urls = self._build_async_requests(
                base_endpoint,
                max_rows,
            )
            return self._fetch_async(
                async_urls,
                return_type=Nomination,
                sort_key="number",
            )

        return self._fetch(
            self.build_url_from_values(congress),
            return_type=Nomination,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )

    def get_detail_from_nomination(self, nomination: Nomination, offset: int = 0, limit: int = 100) -> Nomination:
        """
        Fetches detailed nomination information for a given nomination from the API.
        Args:
            nomination (Nomination): The Nomination object.
            offset (int): The offset for pagination.
            limit (int): The maximum number of results to return.
        Returns:
            DetailedNomination: The detailed nomination information.

        """
        return self._fetch(
            self.build_url_from_values(nomination.congress, nomination.number),
            return_type=DetailedNomination,
            offset=offset,
            limit=limit,
        )

    def get_hearings_from_nomination_number(
        self,
        congress: int,
        nomination_no: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[HearingFromNomination]:
        """
        Fetches hearings for a given nomination number and congress from the API.

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
            return_type=HearingFromNomination,
            offset=offset,
            limit=limit,
        )

    def get_nominee_from_nomination(
        self,
        nomination: Nomination,
        ordinal: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Nominee]:
        """
        Fetches nominees for a given nomination from the API.

        This endpoint requires the parameter ordinal to specify which nominee to retrieve.

        Args:
            nomination (Nomination): The Nomination object.
            offset (int): The offset for pagination.
            limit (int): The maximum number of results to return.
        Returns:
            list[Nomination]: The list of nominations.

        """
        resp = self._fetch(
            self.build_url_from_values(nomination.congress, nomination.number, ordinal),
            return_type=Nominee,
            offset=offset,
            limit=limit,
        )
        if len(resp) > 1:
            self.logger.info("Detected multiple nominees returned, returning the first nominee.")
        return resp

    def get_actions_from_nomination(
        self,
        nomination: Nomination,
        offset: int = 0,
        limit: int = 100,
    ) -> list[NomineeAction]:
        """
        Fetches actions for a given nomination from the API.

        Args:
            nomination (Nomination): The Nomination object.
            offset (int): The offset for pagination.
            limit (int): The maximum number of results to return.
        Returns:
            list[NomineeAction]: The list of nominee actions.

        """
        return self._fetch(
            self.build_url_from_values(nomination.congress, nomination.number, "actions"),
            return_type=NomineeAction,
            offset=offset,
            limit=limit,
        )

    def get_committees_from_nomination(
        self,
        nomination: Nomination,
        offset: int = 0,
        limit: int = 100,
    ) -> list[DetailedCommittee]:
        """
        Fetches committees for a given nomination from the API.

        Args:
            nomination (Nomination): The Nomination object.
            offset (int): The offset for pagination.
            limit (int): The maximum number of results to return.
        Returns:
            list[DetailedCommittee]: The list of committees.

        """
        return self._fetch(
            self.build_url_from_values(nomination.congress, nomination.number, "committees"),
            return_type=DetailedCommittee,
            offset=offset,
            limit=limit,
        )

    def get_hearings_from_nomination(
        self,
        nomination: Nomination,
        offset: int = 0,
        limit: int = 100,
    ) -> list[HearingFromNomination]:
        """
        Fetches hearings for a given nomination from the API.

        Args:
            nomination (Nomination): The Nomination object.
            offset (int): The offset for pagination.
            limit (int): The maximum number of results to return.

        Returns:
            list[Nomination]: The list of nominations.

        """
        return self._fetch(
            self.build_url_from_values(nomination.congress, nomination.number, "hearings"),
            return_type=HearingFromNomination,
            offset=offset,
            limit=limit,
        )

    ### TODO: needs to use better async params
    def get_hearings_from_list_of_nominations(
        self,
        nominations: list[Nomination],
    ) -> list[HearingFromNomination]:
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
        base_urls = [self.build_url_from_values(nom.congress, nom.number, "hearings") for nom in nominations]
        request_list = [
            {
                "url": base_url,
                "params": self.build_params(),
            }
            for base_url in base_urls
        ]
        return self._fetch_async(
            request_list,
            return_type=HearingFromNomination,
        )
