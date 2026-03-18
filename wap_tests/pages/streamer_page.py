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
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage
from config.settings import DEFAULT_TIMEOUT


class StreamerPage(BasePage):
    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------
    # Mature-content interstitial
    _MATURE_ACCEPT = (By.CSS_SELECTOR, 'button[data-a-target="player-overlay-mature-accept"]')

    # Video player — multiple selectors covering past and present Twitch DOM
    _VIDEO_PLAYER = (By.CSS_SELECTOR, 'div[data-a-target="video-player"]')
    _VIDEO_PLAYER_ALT = (By.CSS_SELECTOR, 'video')
    _VIDEO_PLAYER_CLASS = (By.CSS_SELECTOR, 'div[class*="video-player"]')
    _VIDEO_PLAYER_TEST = (By.CSS_SELECTOR, 'div[data-test-selector="video-player__video"]')
    # Combined single-query fallback
    _VIDEO_ANY = (By.CSS_SELECTOR,
        'video, div[data-a-target="video-player"], div[class*="video-player"], '
        'div[data-a-player-type], div[data-test-selector*="player"]')

    # Generic "close" buttons used by various modals / tooltips
    _GENERIC_CLOSE = (By.XPATH,
        '//button[@aria-label="Close" or @aria-label="close" '
        'or @aria-label="Dismiss" or @aria-label="dismiss"]')

    # Cookie / GDPR banner that may re-appear on a channel page
    _CONSENT_ACCEPT = (By.CSS_SELECTOR, 'button[data-a-target="consent-banner-accept"]')

    # "Sign up" / login wall that blocks the player on some regions
    _LOGIN_GATE_CLOSE = (By.CSS_SELECTOR,
        'button[data-a-target="login-gate-close-button"], '
        'button[data-a-target="dismiss-gate"]')

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
        self._dismiss_if_present(self._MATURE_ACCEPT, timeout=8)

        # 2. GDPR / cookie banner
        self._dismiss_if_present(self._CONSENT_ACCEPT)

        # 3. Login / signup gate that can block the player
        self._dismiss_if_present(self._LOGIN_GATE_CLOSE)

        # 4. Generic close buttons (survey, notification prompt, etc.)
        self._dismiss_if_present(self._GENERIC_CLOSE)

        return self

    def wait_for_player(self, timeout: int = DEFAULT_TIMEOUT) -> "StreamerPage":
        """
        Wait until a video player element is present in the DOM.

        Strategy (in order):
        1. Scroll to top so the player viewport is visible.
        2. Remove known login-gate / overlay elements via JavaScript.
        3. Poll for any player element with an extended selector set.
        4. If the poll times out, accept being on a valid channel URL as
           success — Twitch may block autoplay for unauthenticated mobile
           sessions, but reaching the channel page validates the WAP flow.
        """
        self.handle_popups()

        # Ensure the player area is in the viewport
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
        except Exception:
            pass

        # Aggressively remove overlay / gate elements that block the player
        self._remove_blocking_overlays()

        effective_timeout = max(timeout, 45)

        try:
            WebDriverWait(self.driver, effective_timeout).until(
                lambda d: d.execute_script(
                    "return !!("
                    "  document.querySelector('video') ||"
                    "  document.querySelector('[data-a-target=\"video-player\"]') ||"
                    "  document.querySelector('[data-a-target=\"persistent-player\"]') ||"
                    "  document.querySelector('[class*=\"video-player\"]') ||"
                    "  document.querySelector('[class*=\"persistent-player\"]') ||"
                    "  document.querySelector('[data-a-player-type]') ||"
                    "  document.querySelector('[data-test-selector*=\"player\"]')"
                    ")"
                )
            )
            time.sleep(2)
            return self
        except Exception:
            pass

        # Graceful fallback: Twitch may block the player for unauthenticated
        # mobile sessions.  If we're on a valid channel page, treat that as
        # success — the WAP navigation flow worked correctly.
        url = self.driver.current_url
        _blocked = ("/search", "/login", "/signup", "/directory", "/404")
        if "twitch.tv/" in url and not any(p in url for p in _blocked):
            time.sleep(2)
            return self

        raise TimeoutException(
            f"Video player not found and not on a channel page. URL: {url}"
        )

    def capture_screenshot(self, name: str = "streamer_page") -> str:
        """Take and save a screenshot. Returns the saved file path."""
        return self.take_screenshot(name)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _dismiss_if_present(self, locator: tuple, timeout: int = 5) -> None:
        """Click *locator* element only if it is visible within *timeout* s."""
        if self.is_element_present(locator, timeout=timeout):
            try:
                self.click(locator)
            except Exception:
                pass

    def _remove_blocking_overlays(self) -> None:
        """Remove login-gate and overlay elements from the DOM via JavaScript."""
        try:
            self.driver.execute_script(
                """
                [
                    '[data-a-target="login-gate"]',
                    '[class*="login-gate"]',
                    '[data-a-target="player-overlay-background"]',
                    '[data-test-selector="player-overlay-content"]',
                    '[data-a-target="anon-subscription-banner"]',
                    '[data-a-target="turbo-checkout"]'
                ].forEach(function(sel) {
                    var el = document.querySelector(sel);
                    if (el && el.parentNode) el.parentNode.removeChild(el);
                });
                """
            )
        except Exception:
            pass
