from functools import cached_property

from cong.api import HearingAPI, NominationAPI


class CongressV3Client:
    def __init__(self, api_key: str):
        self._api_key = api_key

    @cached_property
    def nomination(self) -> NominationAPI:
        return NominationAPI(api_key=self._api_key)

    @cached_property
    def hearing(self) -> HearingAPI:
        return HearingAPI(api_key=self._api_key)
