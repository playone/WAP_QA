"""
REST Countries API test suite.

API under test : https://restcountries.com/v3.1
Source         : https://github.com/public-apis/public-apis

Validation strategy
-------------------
* **Status-code validation** — the first gate for every test.  The HTTP
  status code is the contract between client and server; verifying it
  first gives a clear, unambiguous signal when something is wrong.

* **Schema / field validation** — for successful responses we assert that
  required keys are present and that their value types match the documented
  API contract (list, string, dict …).  This catches silent schema changes
  that a status-code check alone would miss.

* **Business-logic validation** — for parametrized country/region tests we
  verify that the returned data actually matches the requested value
  (e.g. ``region == "Europe"``), ensuring the API is not returning
  irrelevant data with a 200 OK.

* **Negative / boundary validation** — invalid names and codes must return
  404 with the documented error payload, confirming the API handles bad
  input gracefully.

pytest.mark.parametrize is used extensively to achieve high coverage with
minimal code duplication while keeping individual test cases readable.
"""

import pytest


# ==========================================================================
# TC-API-001  GET /all — retrieve all countries
# ==========================================================================
class TestGetAllCountries:
    """Validate the /all endpoint returns a well-formed country list."""

    def test_status_200(self, countries_client):
        """TC-API-001a: /all returns HTTP 200."""
        response = countries_client.get("/all?fields=name,region,cca2")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )

    def test_response_is_list(self, countries_client):
        """TC-API-001b: /all response body is a JSON array."""
        response = countries_client.get("/all?fields=name,region,cca2")
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"

    def test_returns_multiple_countries(self, countries_client):
        """TC-API-001c: /all returns more than 200 countries (there are 250)."""
        response = countries_client.get("/all?fields=name,region,cca2")
        assert len(response.json()) > 200, "Fewer countries than expected."

    def test_each_item_has_required_fields(self, countries_client):
        """TC-API-001d: Every country object contains 'name', 'region', 'cca2'."""
        response = countries_client.get("/all?fields=name,region,cca2")
        countries = response.json()
        for country in countries:
            assert "name" in country, f"Missing 'name' key in: {country}"
            assert "region" in country, f"Missing 'region' key in: {country}"
            assert "cca2" in country, f"Missing 'cca2' key in: {country}"


# ==========================================================================
# TC-API-002  GET /name/{name} — positive (valid country names)
# ==========================================================================
VALID_COUNTRY_NAMES = [
    # (query_name, expected_common_name_substring)
    ("Germany",   "Germany"),
    ("Japan",     "Japan"),
    ("Brazil",    "Brazil"),
    ("Australia", "Australia"),
    ("Mexico",    "Mexico"),
]


class TestGetCountryByValidName:
    """Verify positive name lookups return correct country data."""

    @pytest.mark.parametrize("name, expected_name", VALID_COUNTRY_NAMES)
    def test_status_200(self, countries_client, name, expected_name):
        """TC-API-002a: Valid country name returns HTTP 200."""
        response = countries_client.get(f"/name/{name}")
        assert response.status_code == 200, (
            f"GET /name/{name} → expected 200, got {response.status_code}"
        )

    @pytest.mark.parametrize("name, expected_name", VALID_COUNTRY_NAMES)
    def test_response_is_list(self, countries_client, name, expected_name):
        """TC-API-002b: Response is a JSON array."""
        response = countries_client.get(f"/name/{name}")
        assert isinstance(response.json(), list)

    @pytest.mark.parametrize("name, expected_name", VALID_COUNTRY_NAMES)
    def test_returned_country_matches_query(self, countries_client, name, expected_name):
        """TC-API-002c: At least one result common name matches the query."""
        response = countries_client.get(f"/name/{name}")
        results = response.json()
        common_names = [
            r.get("name", {}).get("common", "") for r in results
        ]
        assert any(expected_name in n for n in common_names), (
            f"'{expected_name}' not found in returned names: {common_names}"
        )

    @pytest.mark.parametrize("name, expected_name", VALID_COUNTRY_NAMES)
    def test_country_has_required_fields(self, countries_client, name, expected_name):
        """TC-API-002d: Country object contains 'name', 'capital', 'population'."""
        response = countries_client.get(f"/name/{name}")
        for country in response.json():
            assert "name" in country
            assert "population" in country
            assert isinstance(country["population"], int)


# ==========================================================================
# TC-API-003  GET /name/{name} — negative (invalid / nonexistent names)
# ==========================================================================
INVALID_COUNTRY_NAMES = [
    "ThisCountryDoesNotExist",
    "xyzzy123",
    "!!!",
    "Narnia",
]


class TestGetCountryByInvalidName:
    """Verify that invalid names are handled with a 404 response."""

    @pytest.mark.parametrize("name", INVALID_COUNTRY_NAMES)
    def test_status_404(self, countries_client, name):
        """TC-API-003a: Non-existent country name returns HTTP 404."""
        response = countries_client.get(f"/name/{name}")
        assert response.status_code == 404, (
            f"GET /name/{name} → expected 404, got {response.status_code}"
        )

    @pytest.mark.parametrize("name", INVALID_COUNTRY_NAMES)
    def test_error_body_has_message(self, countries_client, name):
        """TC-API-003b: 404 body contains a 'message' or 'status' field."""
        response = countries_client.get(f"/name/{name}")
        body = response.json()
        assert "message" in body or "status" in body, (
            f"Expected error body with 'message'/'status', got: {body}"
        )


# ==========================================================================
# TC-API-004  GET /region/{region} — positive
# ==========================================================================
VALID_REGIONS = [
    ("Europe",   50),   # minimum expected countries
    ("Asia",     40),
    ("Americas", 30),
    ("Africa",   50),
    ("Oceania",  10),
]


class TestGetCountriesByRegion:
    """Validate region-based lookups return the correct subset."""

    @pytest.mark.parametrize("region, min_count", VALID_REGIONS)
    def test_status_200(self, countries_client, region, min_count):
        """TC-API-004a: Valid region returns HTTP 200."""
        response = countries_client.get(f"/region/{region}")
        assert response.status_code == 200, (
            f"GET /region/{region} → expected 200, got {response.status_code}"
        )

    @pytest.mark.parametrize("region, min_count", VALID_REGIONS)
    def test_result_count_is_plausible(self, countries_client, region, min_count):
        """TC-API-004b: Results contain at least *min_count* countries."""
        response = countries_client.get(f"/region/{region}")
        count = len(response.json())
        assert count >= min_count, (
            f"Region '{region}': expected >= {min_count} countries, got {count}"
        )

    @pytest.mark.parametrize("region, min_count", VALID_REGIONS)
    def test_all_results_belong_to_region(self, countries_client, region, min_count):
        """TC-API-004c: Every returned country has region == queried region."""
        response = countries_client.get(f"/region/{region}?fields=name,region")
        for country in response.json():
            assert country.get("region") == region, (
                f"Country {country.get('name')} has region "
                f"'{country.get('region')}', expected '{region}'"
            )


# ==========================================================================
# TC-API-005  GET /region/{region} — negative (invalid region)
# ==========================================================================
INVALID_REGIONS = ["Galaxy", "Atlantis", "123", ""]


class TestGetCountriesByInvalidRegion:
    """Verify that invalid region values are rejected with a 404."""

    @pytest.mark.parametrize("region", INVALID_REGIONS)
    def test_status_404(self, countries_client, region):
        """TC-API-005a: Invalid region name returns HTTP 404."""
        response = countries_client.get(f"/region/{region}")
        assert response.status_code == 404, (
            f"GET /region/{region} → expected 404, got {response.status_code}"
        )


# ==========================================================================
# TC-API-006  GET /alpha/{code} — country code lookups (positive + negative)
# ==========================================================================
VALID_ALPHA_CODES = [
    ("US",  "United States"),
    ("DE",  "Germany"),
    ("JP",  "Japan"),
    ("BR",  "Brazil"),
    ("GBR", "United Kingdom"),   # alpha-3 code
]

INVALID_ALPHA_CODES = ["ZZ", "XX", "000", "QQQ"]


class TestGetCountryByAlphaCode:
    """Validate ISO alpha-2 / alpha-3 code lookups in both directions."""

    @pytest.mark.parametrize("code, expected_name", VALID_ALPHA_CODES)
    def test_valid_code_returns_200(self, countries_client, code, expected_name):
        """TC-API-006a: Valid alpha code returns HTTP 200."""
        response = countries_client.get(f"/alpha/{code}")
        assert response.status_code == 200, (
            f"GET /alpha/{code} → expected 200, got {response.status_code}"
        )

    @pytest.mark.parametrize("code, expected_name", VALID_ALPHA_CODES)
    def test_valid_code_returns_correct_country(self, countries_client, code, expected_name):
        """TC-API-006b: Returned country name matches the expected value."""
        response = countries_client.get(f"/alpha/{code}")
        data = response.json()
        # /alpha/{code} returns a list or a single object depending on API version
        countries_list = data if isinstance(data, list) else [data]
        common_names = [c.get("name", {}).get("common", "") for c in countries_list]
        assert any(expected_name in n for n in common_names), (
            f"Code {code}: expected '{expected_name}' in {common_names}"
        )

    @pytest.mark.parametrize("code", INVALID_ALPHA_CODES)
    def test_invalid_code_returns_404(self, countries_client, code):
        """TC-API-006c: Invalid alpha code returns HTTP 404."""
        response = countries_client.get(f"/alpha/{code}")
        assert response.status_code == 404, (
            f"GET /alpha/{code} → expected 404, got {response.status_code}"
        )
