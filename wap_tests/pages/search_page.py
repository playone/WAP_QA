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


# Paths that are definitively not stream channels
_TWITCH_NON_CHANNEL_PATHS = {
    'directory', 'search', 'login', 'signup', 'subscribe', 'p', 'jobs',
    'downloads', 'turbo', 'wallet', 'bits', 'friends', 'inventory', 'store',
    'settings', 'messages', 'notifications', 'payments', 'prime', 'subs',
    'videos', 'clips', 'about', 'schedule',
}


class SearchPage(BasePage):
    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------
    _SEARCH_INPUT = (By.CSS_SELECTOR, 'input[data-a-target="tw-input"]')
    _SEARCH_INPUT_TYPE = (By.CSS_SELECTOR, 'input[type="search"]')
    _SEARCH_INPUT_ALT = (By.XPATH, '//input[@placeholder or @aria-label]')

    # Stream / channel result cards — specific selectors tried first
    _STREAM_CARDS = (By.CSS_SELECTOR, 'a[data-a-target="preview-card-image-link"]')
    _STREAM_CARDS_TITLE = (By.CSS_SELECTOR, 'a[data-a-target="preview-card-title-link"]')
    _STREAM_CARDS_ALT = (By.XPATH, '//a[contains(@href,"/") and .//img]')

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def search(self, query: str) -> "SearchPage":
        """Enter *query* in the search box and submit."""
        input_el = None
        for locator in (self._SEARCH_INPUT, self._SEARCH_INPUT_TYPE, self._SEARCH_INPUT_ALT):
            if self.is_element_present(locator, timeout=6):
                try:
                    input_el = self.find_clickable(locator)
                    break
                except Exception:
                    continue

        if input_el is None:
            raise RuntimeError("Could not locate the search input on the page.")

        input_el.clear()
        input_el.send_keys(query)
        input_el.send_keys(Keys.RETURN)
        time.sleep(3.0)  # Allow results to start loading
        return self

    def scroll_results(self, times: int = 2, pixels: int = 800) -> "SearchPage":
        """Scroll down *times* times to load more results."""
        for _ in range(times):
            self.scroll_down(pixels)
        return self

    def get_card_count(self) -> int:
        """
        Return the number of visible stream/channel cards on the page.
        Tries specific selectors first, then falls back to JS discovery.
        """
        for locator in (self._STREAM_CARDS, self._STREAM_CARDS_TITLE, self._STREAM_CARDS_ALT):
            els = self.driver.find_elements(*locator)
            filtered = [e for e in els if self._is_channel_href(e.get_attribute("href") or "")]
            if filtered:
                return len(filtered)
        return len(self._get_channel_links_js())

    def select_first_streamer(self) -> str:
        """
        Click the first stream/channel card visible on the page.

        Only channel-path links are considered (filters out /directory/,
        /search, /login, etc.).  Falls back to a JavaScript DOM scan if
        no matching <a> is found via CSS/XPath.

        Returns the href that was clicked so tests can assert the final URL.
        """
        time.sleep(2)  # extra render buffer after scroll

        # Try specific Twitch data-a-target selectors first, filtered to channel URLs
        for locator in (self._STREAM_CARDS, self._STREAM_CARDS_TITLE, self._STREAM_CARDS_ALT):
            try:
                candidates = self.driver.find_elements(*locator)
                valid = [c for c in candidates
                         if self._is_channel_href(c.get_attribute("href") or "")]
                if valid:
                    return self._click_card(valid[0])
            except Exception:
                continue

        # JS fallback: scan the entire DOM for single-segment Twitch channel links
        js_cards = self._get_channel_links_js()
        assert js_cards, "No streamer cards found on search results page."
        return self._click_card(js_cards[0])

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _is_channel_href(href: str) -> bool:
        """Return True only for clean single-segment Twitch channel URLs."""
        if not href or "twitch.tv" not in href:
            return False
        # Remove scheme + domain, split remaining path
        path = href.split("twitch.tv", 1)[-1].strip("/")
        parts = [p for p in path.split("/") if p]
        return (
            len(parts) == 1
            and parts[0].lower() not in _TWITCH_NON_CHANNEL_PATHS
            and len(parts[0]) >= 3
        )

    def _get_channel_links_js(self) -> list:
        """Use JavaScript to collect all channel-like <a> elements in the DOM."""
        skip = list(_TWITCH_NON_CHANNEL_PATHS)
        return self.driver.execute_script(
            """
            var skip = arguments[0];
            return Array.from(document.querySelectorAll('a[href]')).filter(function(a) {
                try {
                    var href = a.href || '';
                    if (href.indexOf('twitch.tv') === -1) return false;
                    var path = new URL(href).pathname;
                    var parts = path.split('/').filter(Boolean);
                    return parts.length === 1
                        && skip.indexOf(parts[0].toLowerCase()) === -1
                        && parts[0].length >= 3;
                } catch(e) { return false; }
            });
            """,
            skip,
        )

    def _click_card(self, element) -> str:
        """Scroll *element* into view, click it, and wait for navigation."""
        href = element.get_attribute("href") or ""
        original_url = self.driver.current_url
        self.scroll_to_element(element)
        element.click()
        # Wait until the browser has navigated away from the search page
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: d.current_url != original_url
            )
        except Exception:
            pass
        return href
