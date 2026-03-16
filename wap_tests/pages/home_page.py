"""
HomePage: represents https://www.twitch.tv on a mobile viewport.

Responsibilities
----------------
* Accept / dismiss cookie / consent banners.
* Navigate to the page.
* Provide the entry-point action: clicking the search icon.
"""

from selenium.webdriver.common.by import By

from .base_page import BasePage
from config.settings import TWITCH_BASE_URL


class HomePage(BasePage):
    # ------------------------------------------------------------------
    # Locators  (kept private to the page object)
    # ------------------------------------------------------------------
    _SEARCH_ICON = (By.CSS_SELECTOR, 'a[href="/search"]')
    _SEARCH_ICON_ALT = (By.XPATH, '//a[contains(@href,"/search")]')

    # Consent / cookie banner locators (Twitch shows these in some regions)
    _CONSENT_ACCEPT = (By.CSS_SELECTOR, 'button[data-a-target="consent-banner-accept"]')
    _CONSENT_CLOSE = (By.XPATH, '//button[contains(@aria-label,"Close") and contains(@class,"consent")]')

    # "Start watching" / mature-content gate that sometimes appears
    _MATURE_ACCEPT = (By.CSS_SELECTOR, 'button[data-a-target="player-overlay-mature-accept"]')

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def load(self) -> "HomePage":
        """Open Twitch home and dismiss any initial banners."""
        self.open(TWITCH_BASE_URL)
        self.wait_for_page_load()
        self._dismiss_consent_banner()
        return self

    def click_search(self) -> None:
        """Click the search icon to navigate to the search page."""
        try:
            self.click(self._SEARCH_ICON)
        except Exception:
            # Fallback: some mobile layouts use a slightly different structure
            self.click(self._SEARCH_ICON_ALT)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _dismiss_consent_banner(self) -> None:
        """Dismiss GDPR / cookie consent banner if it appears."""
        for locator in (self._CONSENT_ACCEPT, self._CONSENT_CLOSE):
            if self.is_element_present(locator, timeout=5):
                try:
                    self.click(locator)
                except Exception:
                    pass
                break
