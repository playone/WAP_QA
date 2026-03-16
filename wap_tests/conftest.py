"""
WAP test fixtures.

The ``mobile_driver`` fixture spins up a Chrome instance with a mobile
device emulation profile and tears it down after each test automatically.

The profile used is resolved at run-time via the ``--mobile-profile``
CLI option (defaults to Pixel_5).  This makes it trivial to add new
device targets through CI matrix builds without touching any test code.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from config.mobile_profiles import MOBILE_PROFILES, DEFAULT_MOBILE_PROFILE


def pytest_addoption(parser):
    """Expose --mobile-profile CLI flag for pytest."""
    parser.addoption(
        "--mobile-profile",
        action="store",
        default=DEFAULT_MOBILE_PROFILE,
        help=(
            f"Mobile emulation profile name defined in "
            f"config/mobile_profiles.py. Default: {DEFAULT_MOBILE_PROFILE}"
        ),
    )


@pytest.fixture(scope="function")
def mobile_driver(request):
    """
    Yield a Selenium WebDriver configured with Chrome mobile emulation.

    Scope is ``function`` so each test gets a fresh, isolated browser
    session – avoiding state bleed between tests.
    """
    profile_name = request.config.getoption("--mobile-profile")
    profile = MOBILE_PROFILES.get(profile_name)
    if profile is None:
        raise ValueError(
            f"Unknown mobile profile '{profile_name}'. "
            f"Available: {list(MOBILE_PROFILES.keys())}"
        )

    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", profile)

    # Headless mode can be enabled for CI by setting HEADLESS=1 env var
    import os
    if os.getenv("HEADLESS", "0") == "1":
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=390,844")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(0)  # rely on explicit waits only in BasePage

    yield driver

    driver.quit()
