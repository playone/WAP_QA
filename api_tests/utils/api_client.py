"""
Generic HTTP client wrapper used by all API test suites.

Design goals
------------
* Single responsibility: make HTTP requests and expose the raw response.
* Tests own assertions; this class owns transport concerns only.
* The base URL is injected at construction time, making it trivial to
  point the same client at a staging or production endpoint without
  any code changes in the test files.
"""

import requests
from config.settings import API_TIMEOUT


class APIClient:
    """Thin wrapper around ``requests.Session``."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------
    def get(self, path: str, **kwargs) -> requests.Response:
        """
        Send a GET request to ``{base_url}/{path}``.

        All extra keyword arguments are forwarded to
        ``requests.Session.get`` (e.g. ``params``, ``headers``).
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", API_TIMEOUT)
        return self._session.get(url, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        """Send a POST request."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", API_TIMEOUT)
        return self._session.post(url, **kwargs)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Close the underlying session (call in fixture teardown)."""
        self._session.close()
