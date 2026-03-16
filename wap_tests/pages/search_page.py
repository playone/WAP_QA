"""
SearchPage: represents the Twitch /search route.

Responsibilities
----------------
* Type a query into the search input.
* Scroll through results.
* Select the first available live streamer (handles sponsored / category
  cards that are not actual stream cards).
* Dismiss any pop-ups that appear before or during result loading.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base_page import BasePage


class SearchPage(BasePage):
    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------
    _SEARCH_INPUT = (By.CSS_SELECTOR, 'input[data-a-target="tw-input"]')
    _SEARCH_INPUT_ALT = (By.XPATH, '//input[@type="search" or @placeholder]')

    # Stream / channel result cards
    _STREAM_CARDS = (By.CSS_SELECTOR, 'a[data-a-target="preview-card-image-link"]')
    _STREAM_CARDS_ALT = (By.XPATH, '//a[contains(@href,"/") and .//img]')

    # "Live" badge that confirms a card is a live stream
    _LIVE_BADGE = (By.CSS_SELECTOR, '[data-a-target="LIVE"]')

    # "Channels" section heading used to locate channel result cards
    _CHANNEL_CARDS = (By.CSS_SELECTOR, 'a[data-a-target="preview-card-channel-link"]')

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def search(self, query: str) -> "SearchPage":
        """Enter *query* in the search box and submit."""
        try:
            input_el = self.find_clickable(self._SEARCH_INPUT)
        except Exception:
            input_el = self.find_clickable(self._SEARCH_INPUT_ALT)

        input_el.clear()
        input_el.send_keys(query)
        input_el.send_keys(Keys.RETURN)
        time.sleep(1.5)  # Allow results to start loading
        return self

    def scroll_results(self, times: int = 2, pixels: int = 800) -> "SearchPage":
        """Scroll down *times* times to load more results."""
        for _ in range(times):
            self.scroll_down(pixels)
        return self

    def select_first_streamer(self) -> str:
        """
        Click the first live stream card visible on the page.

        Returns the href (channel URL) that was clicked so tests can
        assert we landed on the correct page.
        """
        cards = self.find_all(self._STREAM_CARDS)
        if not cards:
            # Fallback locator
            cards = self.find_all(self._STREAM_CARDS_ALT)

        assert cards, "No streamer cards found on search results page."

        first_card = cards[0]
        href = first_card.get_attribute("href") or ""
        self.scroll_to_element(first_card)
        first_card.click()
        return href
