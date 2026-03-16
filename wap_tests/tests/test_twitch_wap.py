"""
WAP test suite — Twitch mobile (Google Chrome emulation).

Test flow
---------
1. Open https://www.twitch.tv in a Chrome mobile emulated browser.
2. Click the search icon.
3. Type "StarCraft II" and submit.
4. Scroll down 2 times.
5. Select the first available streamer.
6. Wait for the stream page to fully load (handle pop-ups).
7. Take a screenshot as evidence.
"""

import os
import pytest

from wap_tests.pages.home_page import HomePage
from wap_tests.pages.search_page import SearchPage
from wap_tests.pages.streamer_page import StreamerPage
from config.settings import TWITCH_BASE_URL, TWITCH_SEARCH_QUERY, SCROLL_DOWN_COUNT


class TestTwitchWAP:
    """End-to-end WAP test cases for Twitch search → stream flow."""

    # ------------------------------------------------------------------
    # TC-WAP-001: Full happy path
    # ------------------------------------------------------------------
    def test_search_starcraft_and_open_streamer(self, mobile_driver):
        """
        TC-WAP-001: Search for StarCraft II and open a live stream.

        Steps
        -----
        1. Navigate to https://www.twitch.tv
        2. Click the search icon
        3. Search for "StarCraft II"
        4. Scroll down 2 times
        5. Click the first streamer card
        6. Handle any pop-ups / mature-content gate
        7. Wait for the video player to load
        8. Take a screenshot

        Expected result
        ---------------
        * The browser URL contains the channel name (not twitch.tv/search).
        * The video player element is present in the DOM.
        * A screenshot file is saved to the screenshots/ directory.
        """
        # Step 1: Load Twitch homepage and dismiss banners
        home = HomePage(mobile_driver)
        home.load()

        # Step 2: Open search
        home.click_search()

        # Steps 3-4: Type query and scroll through results
        search = SearchPage(mobile_driver)
        search.search(TWITCH_SEARCH_QUERY)
        search.scroll_results(times=SCROLL_DOWN_COUNT)

        # Step 5: Select first streamer
        channel_href = search.select_first_streamer()

        # Steps 6-7: Handle pop-ups and wait for player
        streamer = StreamerPage(mobile_driver)
        streamer.handle_popups()
        streamer.wait_for_player()

        # Step 8: Screenshot
        screenshot_path = streamer.capture_screenshot("tc_wap_001_starcraft")

        # --- Assertions ---
        current_url = mobile_driver.current_url
        assert TWITCH_BASE_URL in current_url, (
            f"Expected to be on Twitch, got: {current_url}"
        )
        assert "/search" not in current_url, (
            f"Browser is still on search page, expected a channel page. URL: {current_url}"
        )
        assert os.path.isfile(screenshot_path), (
            f"Screenshot was not saved at: {screenshot_path}"
        )
        assert os.path.getsize(screenshot_path) > 0, "Screenshot file is empty."

    # ------------------------------------------------------------------
    # TC-WAP-002: Search results contain StarCraft II content
    # ------------------------------------------------------------------
    def test_search_results_not_empty(self, mobile_driver):
        """
        TC-WAP-002: Verify that searching for StarCraft II returns results.

        Steps
        -----
        1. Navigate to Twitch
        2. Open search
        3. Type "StarCraft II"
        4. Scroll down 2 times

        Expected result
        ---------------
        * At least one stream/channel card is visible on the page.
        """
        home = HomePage(mobile_driver)
        home.load()
        home.click_search()

        search = SearchPage(mobile_driver)
        search.search(TWITCH_SEARCH_QUERY)
        search.scroll_results(times=SCROLL_DOWN_COUNT)

        from selenium.webdriver.common.by import By
        cards = mobile_driver.find_elements(
            By.CSS_SELECTOR, 'a[data-a-target="preview-card-image-link"]'
        )
        assert len(cards) > 0, (
            "No stream cards found after searching for StarCraft II."
        )

    # ------------------------------------------------------------------
    # TC-WAP-003: Pop-up handling robustness
    # ------------------------------------------------------------------
    def test_popup_handled_gracefully(self, mobile_driver):
        """
        TC-WAP-003: Verify that the mature-content / modal pop-up handler
        does not raise an exception even on pages without a pop-up.

        Steps
        -----
        1-6: Same as TC-WAP-001

        Expected result
        ---------------
        * handle_popups() completes without raising an exception regardless
          of whether a pop-up is present.
        * The test does not crash and a screenshot is saved successfully.
        """
        home = HomePage(mobile_driver)
        home.load()
        home.click_search()

        search = SearchPage(mobile_driver)
        search.search(TWITCH_SEARCH_QUERY)
        search.scroll_results(times=SCROLL_DOWN_COUNT)
        search.select_first_streamer()

        streamer = StreamerPage(mobile_driver)

        # This must never raise even when no pop-up is shown
        try:
            streamer.handle_popups()
            streamer.wait_for_player()
            popup_handled = True
        except Exception as exc:  # pragma: no cover
            popup_handled = False
            pytest.fail(f"handle_popups raised an unexpected exception: {exc}")

        screenshot_path = streamer.capture_screenshot("tc_wap_003_popup_check")
        assert popup_handled
        assert os.path.isfile(screenshot_path)
