"""
Miscellaneous WAP test helpers.

These utilities are intentionally thin — complex logic belongs in
Page Objects, not here.  This module exists as a convenience layer for
things like environment detection that don't naturally fit a page.
"""

import os
import sys


def is_ci() -> bool:
    """Return True when running inside a CI environment."""
    return any(
        os.getenv(var)
        for var in ("CI", "GITHUB_ACTIONS", "JENKINS_HOME", "CIRCLECI")
    )


def headless_mode() -> bool:
    """
    Return True if headless Chrome should be used.

    Priority order:
    1. HEADLESS env var explicitly set to '1' or '0'.
    2. Auto-enable in CI environments.
    """
    env_val = os.getenv("HEADLESS")
    if env_val is not None:
        return env_val.strip() == "1"
    return is_ci()
