"""
Chrome DevTools mobile emulation profiles.
Add or modify profiles here to test against different devices
without touching any test code.
"""

MOBILE_PROFILES = {
    # Explicit metrics avoid relying on Chrome's built-in device registry,
    # which varies across Chrome versions and does not always include newer devices.
    "Pixel_5": {
        "deviceMetrics": {"width": 393, "height": 851, "pixelRatio": 2.75},
        "userAgent": (
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.91 Mobile Safari/537.36"
        ),
    },
    "Galaxy_S20": {
        "deviceMetrics": {"width": 412, "height": 915, "pixelRatio": 3.5},
        "userAgent": (
            "Mozilla/5.0 (Linux; Android 10; SM-G981B) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/80.0.3987.162 Mobile Safari/537.36"
        ),
    },
    # Generic mobile viewport
    "Custom_Mobile": {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": (
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.91 Mobile Safari/537.36"
        ),
    },
}

# Which profile to use by default in tests
DEFAULT_MOBILE_PROFILE = "Pixel_5"
