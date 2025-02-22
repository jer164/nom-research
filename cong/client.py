"""
Module to provide a client for interacting with the Congress API.

Classes:
    CongressV3Client: A client for accessing the Nomination and Hearing APIs.
"""

from functools import cached_property

from cong.api import HearingAPI, NominationAPI


class CongressV3Client:
    """
    A client for accessing the Nomination and Hearing APIs.

    Attributes:
        _api_key (str): The API key for authenticating requests.

    """

    def __init__(self, api_key: str):
        """
        Initializes the CongressV3Client with the provided API key.

        Args:
            api_key (str): The API key for authenticating requests.

        """
        self._api_key = api_key

    @cached_property
    def nomination(self) -> NominationAPI:
        """
        Provides access to the NominationAPI.

        Returns:
            NominationAPI: An instance of the NominationAPI.

        """
        return NominationAPI(api_key=self._api_key)

    @cached_property
    def hearing(self) -> HearingAPI:
        """
        Provides access to the HearingAPI.

        Returns:
            HearingAPI: An instance of the HearingAPI.

        """
        return HearingAPI(api_key=self._api_key)
