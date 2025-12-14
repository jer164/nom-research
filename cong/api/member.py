from datetime import datetime
from typing import ClassVar


from cong.api.api import HasSubDirectories, CongressAPI
from cong.models.member import Member
from cong.statics import BaseEndpoints


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
        return self._fetch(
            self._url,
            return_type=Member,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            currentMember=current_member,
        )
    
    def get_all_members(
        self,
        limit: int = 100,
        from_date: datetime | str | None = None,
        to_date: datetime | str | None = None,
        current_member: bool = True,
        stop_after: int | None = None,
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
        return self._fetch_all(
            self._url,
            return_type=Member,
            limit=limit,
            from_date=from_date,
            to_date=to_date,
            currentMember=current_member,
            stop_after=stop_after,
        )
    
