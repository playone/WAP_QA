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
    # Multiple candidates in priority order — Twitch updates the DOM regularly
    _SEARCH_ICON = (By.CSS_SELECTOR, 'a[href="/search"]')
    _SEARCH_ICON_ALT = (By.XPATH, '//a[contains(@href,"/search")]')
    _SEARCH_BTN = (By.CSS_SELECTOR, 'button[data-a-target="header-search-button"]')
    _SEARCH_BTN_ALT = (By.CSS_SELECTOR, '[data-a-target="nav-search-button"]')
    _SEARCH_BTN_ARIA = (By.XPATH, '//button[contains(translate(@aria-label,"SEARCH","search"),"search")]')
    _SEARCH_INPUT_DIRECT = (By.CSS_SELECTOR, 'input[type="search"], input[data-a-target="tw-input"]')

    # Consent / cookie banner locators (Twitch shows these in some regions)
    _CONSENT_ACCEPT = (By.CSS_SELECTOR, 'button[data-a-target="consent-banner-accept"]')
    _CONSENT_CLOSE = (By.XPATH, '//button[contains(@aria-label,"Close") and contains(@class,"consent")]')

    # "Start watching" / mature-content gate that sometimes appears
    _MATURE_ACCEPT = (By.CSS_SELECTOR, 'button[data-a-target="player-overlay-mature-accept"]')

    # Ordered list of all search-entry-point locators to try before falling back
    _SEARCH_LOCATORS = (
        _SEARCH_ICON,
        _SEARCH_BTN,
        _SEARCH_BTN_ALT,
        _SEARCH_ICON_ALT,
        _SEARCH_BTN_ARIA,
        _SEARCH_INPUT_DIRECT,
    )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def load(self) -> "HomePage":
        """Open Twitch home and dismiss any initial banners."""
        self.open(TWITCH_BASE_URL)
        self.wait_for_page_load()
        self._dismiss_consent_banner()
        return self

    def tap_page(self) -> None:
        """Click the page body to ensure the viewport is focused and interactive."""
        try:
            self.driver.execute_script("document.body.click();")
        except Exception:
            pass

    def click_search(self) -> None:
        """
        Navigate to the Twitch search page.

        Taps the page body first to ensure focus, then tries every known
        locator in priority order.  If none resolves within the short probe
        timeout, falls back to a direct URL navigation so tests are not
        blocked by nav-bar DOM changes.
        """
        self.tap_page()
        for locator in self._SEARCH_LOCATORS:
            if self.is_element_present(locator, timeout=4):
                try:
                    self.click(locator)
                    return
                except Exception:
                    continue
        # Final fallback: navigate directly — avoids total failure when
        # Twitch restructures its navigation bar.
        self.open(TWITCH_BASE_URL + "/search")
        self.wait_for_page_load()

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
