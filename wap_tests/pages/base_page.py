"""
BasePage: shared helpers used by every Page Object.

Design goals
------------
* Keep all explicit-wait logic in one place so individual page classes
  stay declarative (locators + actions only).
* Provide scroll / screenshot helpers that any page can call without
  duplicating code.
"""

import os
import time
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import DEFAULT_TIMEOUT, SCREENSHOT_DIR


class BasePage:
    """Shared behaviour for all Page Object classes."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------
    def open(self, url: str) -> None:
        """Navigate to *url*."""
        self.driver.get(url)

    # ------------------------------------------------------------------
    # Element interaction helpers
    # ------------------------------------------------------------------
    def find(self, locator: tuple):
        """Return the first element that matches *locator* (with wait)."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator: tuple):
        """Wait until element is clickable and return it."""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def find_visible(self, locator: tuple):
        """Wait until element is visible and return it."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: tuple) -> list:
        """Return all elements matching *locator* (with presence wait)."""
        self.wait.until(EC.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)

    def click(self, locator: tuple) -> None:
        """Wait for element to be clickable, then click it."""
        self.find_clickable(locator).click()

    def type_text(self, locator: tuple, text: str) -> None:
        """Clear field and type *text* into it."""
        element = self.find_clickable(locator)
        element.clear()
        element.send_keys(text)

    def is_element_present(self, locator: tuple, timeout: int = 5) -> bool:
        """Return True if element appears within *timeout* seconds."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------
    # Scroll helpers
    # ------------------------------------------------------------------
    def scroll_down(self, pixels: int = 800) -> None:
        """Scroll the page down by *pixels*."""
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(0.8)  # brief pause so content can load after scroll

    def scroll_to_element(self, element) -> None:
        """Scroll until *element* is in view."""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)

    # ------------------------------------------------------------------
    # Screenshot helpers
    # ------------------------------------------------------------------
    def take_screenshot(self, name: str = "screenshot") -> str:
        """
        Save a PNG screenshot.

        Returns the absolute path of the saved file.
        """
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        self.driver.save_screenshot(filepath)
        return filepath

    # ------------------------------------------------------------------
    # Wait helpers
    # ------------------------------------------------------------------
    def wait_for_page_load(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Block until document.readyState == 'complete'."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for_url_contains(self, partial_url: str) -> None:
        """Wait until the current URL contains *partial_url*."""
        self.wait.until(EC.url_contains(partial_url))
