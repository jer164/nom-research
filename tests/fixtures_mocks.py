from datetime import datetime

import pytest

from cong.models.member import (
    AddressInformation,
    Depiction,
    DetailedTerm,
    LegislationInfo,
    Member,
    MemberDetail,
    Term,
    Depiction,
    AddressInformation,
    PartyHistory,
    PreviousName,
    Term,
)


@pytest.fixture
def member_fixture():
    return Member(
        bioguide_id="B001301",
        name="Bergman, Jack",
        party_name="Republican",
        state="Michigan",
        terms=[
            Term(
                chamber="House of Representatives",
                start_year=2017,
                end_year=None,
            )
        ],
        update_date=datetime(2025, 9, 24, 7, 40, 15),
        url="https://api.congress.gov/v3/member/B001301?format=json",
        depiction=Depiction(
            attribution="Image courtesy of the Member",
            image_url="https://www.congress.gov/img/member/b001301_200.jpg",
        ),
        district=1,
    )


@pytest.fixture
def member_detail_fixture():
    return MemberDetail(
        address_information=AddressInformation(
            city="Washington",
            district="DC",
            office_address="466 Cannon House Office Building",
            phone_number="(202) 225-5235",
            zip_code=20515,
        ),
        bioguide_id="D000628",
        birth_year="1953",
        current_member=True,
        depiction=Depiction(
            attribution="Congressional Pictorial Directory",
            image_url="https://www.congress.gov/img/member/115_rp_fl_2_dunn_neal_200.jpg",
        ),
        direct_order_name="Neal P. Dunn",
        first_name="Neal",
        honorific_name="Mr.",
        inverted_order_name="Dunn, Neal P.",
        last_name="Dunn",
        middle_name="P.",
        official_website_url="https://dunn.house.gov",
        party_history=[
            PartyHistory(
                party_abbreviation="R", party_name="Republican", start_year=2017
            )
        ],
        previous_names=[
            PreviousName(
                direct_order_name="Neal P. Dunn",
                first_name="Neal",
                honorific_name="Mr.",
                inverted_order_name="Dunn, Neal P.",
                last_name="Dunn",
                middle_name="P.",
                start_date="2017-01-03T05:00:00Z",
                end_date="2023-06-01T03:59:59Z",
            ),
            PreviousName(
                direct_order_name="Neal P. Dunn",
                first_name="Neal",
                honorific_name="Mr.",
                inverted_order_name="Dunn, Neal P.",
                last_name="Dunn",
                middle_name="P.",
                start_date="2023-06-01T04:00:00Z",
                end_date="2024-06-03T03:59:59Z",
            ),
            PreviousName(
                direct_order_name="Neal P. Dunn",
                first_name="Neal",
                honorific_name="Mr.",
                inverted_order_name="Dunn, Neal P.",
                last_name="Dunn",
                middle_name="P.",
                start_date="2024-06-03T04:00:00Z",
                end_date=None,
            ),
        ],
        state="Florida",
        terms=[
            DetailedTerm(
                chamber="House of Representatives",
                congress=115,
                member_type="Representative",
                start_year=2017,
                state_code="FL",
                state_name="Florida",
                district=2,
                end_year=2019,
            ),
            DetailedTerm(
                chamber="House of Representatives",
                congress=116,
                member_type="Representative",
                start_year=2019,
                state_code="FL",
                state_name="Florida",
                district=2,
                end_year=2021,
            ),
            DetailedTerm(
                chamber="House of Representatives",
                congress=117,
                member_type="Representative",
                start_year=2021,
                state_code="FL",
                state_name="Florida",
                district=2,
                end_year=2023,
            ),
            DetailedTerm(
                chamber="House of Representatives",
                congress=118,
                member_type="Representative",
                start_year=2023,
                state_code="FL",
                state_name="Florida",
                district=2,
                end_year=2025,
            ),
            DetailedTerm(
                chamber="House of Representatives",
                congress=119,
                member_type="Representative",
                start_year=2025,
                state_code="FL",
                state_name="Florida",
                district=2,
                end_year=None,
            ),
        ],
        update_date=datetime(2025, 12, 9, 8, 40, 20),
        cosponsored_legislation=LegislationInfo(
            count=1109,
            url="https://api.congress.gov/v3/member/D000628/cosponsored-legislation",
        ),
        sponsored_legislation=LegislationInfo(
            count=85,
            url="https://api.congress.gov/v3/member/D000628/sponsored-legislation",
        ),
        district=2,
    )
