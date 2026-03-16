"""
StreamerPage: represents an individual Twitch channel / stream page.

Responsibilities
----------------
* Dismiss the mature-content gate pop-up when it appears.
* Wait for the video player to finish loading.
* Expose a method to capture the final screenshot.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage
from config.settings import DEFAULT_TIMEOUT


class StreamerPage(BasePage):
    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------
    # Mature-content interstitial
    _MATURE_ACCEPT = (By.CSS_SELECTOR, 'button[data-a-target="player-overlay-mature-accept"]')

    # Video player container – presence signals the player mounted
    _VIDEO_PLAYER = (By.CSS_SELECTOR, 'div[data-a-target="video-player"]')
    _VIDEO_PLAYER_ALT = (By.CSS_SELECTOR, 'video')

    # Generic "close" buttons used by various modals / tooltips
    _GENERIC_CLOSE = (By.XPATH, '//button[@aria-label="Close" or @aria-label="close"]')

    # Cookie / GDPR banner that may re-appear on a channel page
    _CONSENT_ACCEPT = (By.CSS_SELECTOR, 'button[data-a-target="consent-banner-accept"]')

    # Chat loading indicator
    _CHAT_CONTAINER = (By.CSS_SELECTOR, 'div[data-a-target="chat-scroller"]')

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def handle_popups(self) -> "StreamerPage":
        """
        Dismiss all known pop-ups / modals that may appear on a
        channel page before the stream becomes visible.

        The method is intentionally defensive – each step is wrapped in
        a try/except so that a missing overlay never fails the test.
        """
        # 1. Mature-content gate
        self._dismiss_if_present(self._MATURE_ACCEPT)

        # 2. GDPR / cookie banner
        self._dismiss_if_present(self._CONSENT_ACCEPT)

        # 3. Generic close buttons (survey, notification prompt, etc.)
        self._dismiss_if_present(self._GENERIC_CLOSE)

        return self

    def wait_for_player(self, timeout: int = DEFAULT_TIMEOUT) -> "StreamerPage":
        """
        Block until the video player element is present in the DOM.

        Falls back to a plain <video> tag if the Twitch-specific
        data attribute is not found.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self._VIDEO_PLAYER)
            )
        except Exception:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self._VIDEO_PLAYER_ALT)
            )
        # Extra buffer so the player can render its first frame
        time.sleep(2)
        return self

    def capture_screenshot(self, name: str = "streamer_page") -> str:
        """Take and save a screenshot. Returns the saved file path."""
        return self.take_screenshot(name)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _dismiss_if_present(self, locator: tuple) -> None:
        """Click *locator* element only if it is visible within 5 s."""
        if self.is_element_present(locator, timeout=5):
            try:
                self.click(locator)
            except Exception:
                pass
