import pytest
from unittest.mock import patch
from cong.api.member import MemberAPI
from cong.models.member import MemberDetail
from tests.fixtures_mocks import member_fixture, member_detail_fixture


@pytest.fixture
def api_key():
    return "test_api_key"


@pytest.fixture
def member_api(api_key):
    return MemberAPI(api_key=api_key)


class TestMemberAPI:
    def test_init(self, api_key):
        api = MemberAPI(api_key=api_key)
        assert api is not None

    @patch.object(MemberAPI, "_fetch")
    def test_get_members(self, mock_fetch, member_api):
        mock_fetch.return_value = [member_fixture]
        result = member_api.get_members(offset=0, limit=100)

        mock_fetch.assert_called_once()
        assert len(result) == 1

    @patch.object(MemberAPI, "_get_all_members")
    def test_get_members_retrieve_all(self, mock_get_all, member_api):
        mock_get_all.return_value = [member_fixture]
        result = member_api.get_members(retrieve_all=True)

        mock_get_all.assert_called_once()
        assert len(result) == 1

    @patch.object(MemberAPI, "_fetch")
    def test_get_members_by_congress(self, mock_fetch, member_api):
        mock_fetch.return_value = [member_fixture]
        result = member_api.get_members_by_congress(congress=117)

        mock_fetch.assert_called_once()
        assert len(result) == 1

    @patch.object(MemberAPI, "_fetch_async")
    @patch.object(MemberAPI, "_build_async_requests")
    @patch.object(MemberAPI, "_get_endpoint_max")
    def test_get_members_by_congress_retrieve_all(self, mock_max, mock_build, mock_fetch_async, member_api):
        mock_max.return_value = 250
        mock_build.return_value = ["url1", "url2"]
        mock_fetch_async.return_value = [member_fixture]

        result = member_api.get_members_by_congress(congress=117, retrieve_all=True)

        mock_fetch_async.assert_called_once()
        assert len(result) == 1

    @patch.object(MemberAPI, "_fetch")
    def test_get_bioguide_from_member(self, mock_fetch, member_api, member_detail_fixture):
        mock_fetch.return_value = member_detail_fixture
        result = member_api.get_bioguide_from_member(member_detail_fixture)

        mock_fetch.assert_called_once()
        assert isinstance(result, MemberDetail)

    @patch.object(MemberAPI, "_fetch")
    def test_get_sponsored_legislation_from_member(self, mock_fetch, member_api, member_fixture):
        mock_fetch.return_value = {}
        result = member_api.get_sponsored_legislation_from_member(member_fixture)

        mock_fetch.assert_called_once()
        assert isinstance(result, dict)

    @patch.object(MemberAPI, "_fetch")
    def test_get_cosponsored_legislation_from_member(self, mock_fetch, member_api, member_fixture):
        mock_fetch.return_value = {}
        result = member_api.get_cosponsored_legislation_from_member(member_fixture)

        mock_fetch.assert_called_once()
        assert isinstance(result, dict)

    @patch.object(MemberAPI, "_fetch")
    def test_get_members_by_state(self, mock_fetch, member_api):
        mock_fetch.return_value = [member_fixture]
        result = member_api.get_members_by_state(state="CA")

        mock_fetch.assert_called_once()
        assert len(result) == 1

    @patch.object(MemberAPI, "_fetch")
    def test_get_members_by_state_and_district(self, mock_fetch, member_api):
        mock_fetch.return_value = [member_fixture]
        result = member_api.get_members_by_state_and_district(state="CA", district=1)

        mock_fetch.assert_called_once()
        assert len(result) == 1

    def test_get_members_by_state_and_district_invalid(self, member_api):
        with pytest.raises(ValueError, match="Invalid district number"):
            member_api.get_members_by_state_and_district(state="CA", district=53)

        with pytest.raises(ValueError, match="Invalid district number"):
            member_api.get_members_by_state_and_district(state="CA", district=-1)

    @patch.object(MemberAPI, "_fetch")
    def test_get_members_by_congress_state_and_district(self, mock_fetch, member_api):
        mock_fetch.return_value = [member_fixture]
        result = member_api.get_members_by_congress_state_and_district(congress=117, state="CA", district=1)

        mock_fetch.assert_called_once()
        assert len(result) == 1

    def test_get_members_by_congress_state_and_district_invalid(self, member_api):
        with pytest.raises(ValueError, match="Invalid district number"):
            member_api.get_members_by_congress_state_and_district(congress=117, state="CA", district=100)

    @patch.object(MemberAPI, "_fetch_async")
    @patch.object(MemberAPI, "_build_async_requests")
    @patch.object(MemberAPI, "_get_endpoint_max")
    def test_get_all_members(self, mock_max, mock_build, mock_fetch_async, member_api):
        mock_max.return_value = 500
        mock_build.return_value = ["url1", "url2"]
        mock_fetch_async.return_value = [member_fixture]

        result = member_api._get_all_members()

        mock_max.assert_called_once()
        mock_build.assert_called_once()
        mock_fetch_async.assert_called_once()
        assert len(result) == 1
