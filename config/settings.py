"""
Global configuration settings for the WAP_QA test framework.
All environment-specific values should be defined here and
referenced throughout the test suite via this module.
"""

# ---------------------------------------------------------------------------
# WAP / Twitch settings
# ---------------------------------------------------------------------------
TWITCH_BASE_URL = "https://www.twitch.tv"
TWITCH_SEARCH_QUERY = "StarCraft II"

# Number of times to scroll down on the search results page
SCROLL_DOWN_COUNT = 2

# Maximum time (seconds) to wait for an element to appear
DEFAULT_TIMEOUT = 15

# Screenshot directory (relative to project root)
SCREENSHOT_DIR = "screenshots"

# ---------------------------------------------------------------------------
# REST API settings
# ---------------------------------------------------------------------------
REST_COUNTRIES_BASE_URL = "https://restcountries.com/v3.1"

# Default request timeout in seconds
API_TIMEOUT = 10

# ---------------------------------------------------------------------------
# Report settings
# ---------------------------------------------------------------------------
REPORT_DIR = "reports"
