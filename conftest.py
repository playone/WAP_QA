"""
Root conftest.py — project-wide fixtures and hooks.

Anything registered here is available to BOTH wap_tests and api_tests
without any extra imports.
"""

import os
import pytest

from config.settings import SCREENSHOT_DIR, REPORT_DIR


def pytest_configure(config):
    """Create output directories at session start."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


def pytest_runtest_makereport(item, call):
    """
    Attach a screenshot to the report when a WAP test fails.

    The ``mobile_driver`` fixture must be present on the test for this
    hook to activate.
    """
    if call.when == "call" and call.excinfo is not None:
        driver = item.funcargs.get("mobile_driver")
        if driver is not None:
            screenshot_name = f"FAILED_{item.name}"
            path = os.path.join(
                SCREENSHOT_DIR,
                f"{screenshot_name}.png",
            )
            try:
                driver.save_screenshot(path)
            except Exception:
                pass  # Never let screenshot logic fail the suite
