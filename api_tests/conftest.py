"""
API test fixtures.

Provides a pre-configured ``APIClient`` instance as a pytest fixture,
keeping HTTP session management out of individual test files.
"""

import pytest
from api_tests.utils.api_client import APIClient
from config.settings import REST_COUNTRIES_BASE_URL


@pytest.fixture(scope="session")
def countries_client() -> APIClient:
    """
    Shared REST Countries API client for the entire test session.

    ``scope="session"`` reuses the same requests.Session across all
    API tests, which is safe for read-only endpoints and avoids
    redundant TCP connection overhead.
    """
    return APIClient(base_url=REST_COUNTRIES_BASE_URL)
