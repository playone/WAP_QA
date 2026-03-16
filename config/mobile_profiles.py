"""
Chrome DevTools mobile emulation profiles.
Add or modify profiles here to test against different devices
without touching any test code.
"""

MOBILE_PROFILES = {
    "Pixel_5": {
        "deviceName": "Pixel 5",
    },
    "Galaxy_S20": {
        "deviceName": "Samsung Galaxy S20 Ultra",
    },
    # Custom profile for generic mobile viewport
    "Custom_Mobile": {
        "width": 390,
        "height": 844,
        "pixelRatio": 3.0,
        "userAgent": (
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.91 Mobile Safari/537.36"
        ),
    },
}

# Which profile to use by default in tests
DEFAULT_MOBILE_PROFILE = "Pixel_5"
