from datetime import datetime
from typing import ClassVar

from us import states

from cong.api.api import HasSubDirectories, CongressAPI
from cong.models.member import Member, MemberDetail, SponsoredLegislation, CosponsoredLegislation
from cong.statics import BaseEndpoints

MAX_DISTRICT_NUMBER = 52


class MemberAPI(CongressAPI, HasSubDirectories):
    """
    A class for interacting with the Member API.

    Attributes:
        _url (str): The base URL for the Member API.
        _return_type (CongressResponseBase): The type of response expected from the API.

    """

    _url: ClassVar[str] = BaseEndpoints.MEMBER.value

    def __init__(self, api_key: str):
        """
        Initializes the MemberAPI with the provided API key.
        Args:
            api_key (str): The API key for authenticating requests.

        """
        super().__init__(api_key=api_key)

    def get_members(
        self,
        offset: int = 0,
        from_date: datetime | str | None = None,
        to_date: datetime | str | None = None,
        limit: int = 100,
        current_member: bool = True,
        retrieve_all: bool = False,
    ) -> list[Member]:
        """
        Fetches Members from the API.

        Args:
            offset (int): The offset for pagination.
            from_date (datetime | str | None): The start date for filtering results.
            to_date (datetime | str | None): The end date for filtering results.
            limit (int): The maximum number of results to return.
            current_member (bool): Whether to filter for current members only.

        Returns:
            list[Member]: The list of Members.

        """
        if retrieve_all:
            return self._get_all_members(
                from_date=from_date,
                to_date=to_date,
                current_member=current_member,
            )
        return self._fetch(
            self._url,
            return_type=Member,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            currentMember=current_member,
        )

    def get_members_by_congress(
        self,
        congress: int,
        offset: int = 0,
        limit: int = 100,
        current_member: bool = True,
        retrieve_all: bool = False,
    ) -> list[Member]:
        """
        Fetches Members by Congress from the API.

        Args:
            congress (int): The Congress number.
            offset (int): The offset for pagination.
            from_date (datetime | str | None): The start date for filtering results.
            to_date (datetime | str | None): The end date for filtering results.
            limit (int): The maximum number of results to return.
            current_member (bool): Whether to filter for current members only.
        Returns:
            list[Member]: The list of Members.
        """
        if retrieve_all:
            max_rows = self._get_endpoint_max(self.build_url_from_values("congress", congress))
            async_urls = self._build_async_requests(
                self.build_url_from_values("congress", congress),
                max_rows,
                currentMember=current_member,
            )
            return self._fetch_async(
                async_urls,
                return_type=Member,
            )
        # else just get with pagination optional
        return self._fetch(
            self.build_url_from_values("congress", congress),
            return_type=Member,
            offset=offset,
            limit=limit,
            currentMember=current_member,
        )

    def get_bioguide_from_member(self, member: Member) -> MemberDetail:
        """
        Fetches MemberDetail for a given Member from the API.

        Args:
            member (Member): The Member object.
        Returns:
            MemberDetail: The detailed information of the Member.
        """
        return self._fetch(
            self.build_url_from_values(member.bioguide_id),
            return_type=MemberDetail,
        )

    def get_sponsored_legislation_from_member(self, member: Member, limit: int = 100, offset: int = 0) -> dict:
        """
        Fetches sponsored legislation for a given Member from the API.

        Args:
            member (Member): The Member object.
        Returns:
            SponsoredLegislation: The sponsored legislation information.
        """
        return self._fetch(
            self.build_url_from_values(member.bioguide_id, "sponsored-legislation"),
            return_type=SponsoredLegislation,
            limit=limit,
            offset=offset,
        )

    def get_cosponsored_legislation_from_member(self, member: Member, limit: int = 100, offset: int = 0) -> dict:
        """
        Fetches cosponsored legislation for a given Member from the API.

        Args:
            member (Member): The Member object.
        Returns:
            CosponsoredLegislation: The cosponsored legislation information.
        """
        return self._fetch(
            self.build_url_from_values(member.bioguide_id, "cosponsored-legislation"),
            return_type=CosponsoredLegislation,
            limit=limit,
            offset=offset,
        )

    def get_members_by_state(
        self, state: str, limit: int = 100, current_member: bool = True, offset: int = 0
    ) -> list[Member]:
        """
        Fetches Members by state from the API.

        Args:
            state (str): The state abbreviation or state name.
        Returns:
            list[Member]: The list of Members from the specified state.
        """

        state_code = states.lookup(state).abbr
        return self._fetch(
            self.build_url_from_values(state_code),
            return_type=Member,
            offset=offset,
            limit=limit,
            currentMember=current_member,
        )

    def get_members_by_state_and_district(
        self, state: str, district: int, limit: int = 100, current_member: bool = True, offset: int = 0
    ) -> list[Member]:
        """
        Fetches Members by state and district from the API.

        Args:
            state (str): The state abbreviation or state name.
            district (int): The district number.
        Returns:
            list[Member]: The list of Members from the specified state and district.
        """
        if district > 52 or district < 0:
            raise ValueError("Invalid district number. Must be between 0 and 52.")
        state_code = states.lookup(state).abbr
        return self._fetch(
            self.build_url_from_values(state_code, district),
            return_type=Member,
            offset=offset,
            limit=limit,
            currentMember=current_member,
        )

    def get_members_by_congress_state_and_district(
        self, congress: int, state: str, district: int, limit: int = 100, current_member: bool = True, offset: int = 0
    ) -> list[Member]:
        """
        Fetches Members by congress, state and district from the API.

        Args:
            congress (int): The Congress number.
            state (str): The state abbreviation or state name.
            district (int): The district number.
        Returns:
            list[Member]: The list of Members from the specified congress, state and district.
        """
        if district > MAX_DISTRICT_NUMBER or district < 0:
            raise ValueError(f"Invalid district number. Must be between 0 and {MAX_DISTRICT_NUMBER}.")
        state_code = states.lookup(state).abbr
        return self._fetch(
            self.build_url_from_values("congress", congress, state_code, district),
            return_type=Member,
            offset=offset,
            limit=limit,
            currentMember=current_member,
        )

    def _get_all_members(
        self,
        from_date: datetime | str | None = None,
        to_date: datetime | str | None = None,
        current_member: bool = True,
    ) -> list[Member]:
        """
            Fetches all Members from the API.

            Args:
                from_date (datetime | str | None): The start date for filtering results.
                to_date (datetime | str | None): The end date for filtering results.
                current_member (bool): Whether to filter for current members only.
        )
            Returns:
                list[Member]: The list of Members.

        """
        max_rows = self._get_endpoint_max(self._url)
        async_urls = self._build_async_requests(
            self._url,
            max_rows,
            currentMember=current_member,
            from_date=from_date,
            to_date=to_date,
        )
        return self._fetch_async(
            async_urls,
            return_type=Member,
        )
