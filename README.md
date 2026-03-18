# WAP_QA — Automated Test Framework

> **Two test suites in one repository:**
> 1. **WAP** — Twitch mobile-browser end-to-end tests (Selenium + Chrome emulation)
> 2. **REST API** — REST Countries public API tests (pytest + requests)

---

## Demo

> *Add a GIF here showing the test running locally.*
> Record with [ScreenToGif](https://www.screentogif.com/) or [ShareX](https://getsharex.com/),
> then drop the `.gif` into this repo and update the path below.*

![WAP test demo](screenshots/demo.gif)

---

## Repository Structure

```
WAP_QA/
│
├── config/                         # Centralised settings — change once, works everywhere
│   ├── settings.py                 # URLs, timeouts, directories
│   └── mobile_profiles.py          # Chrome DevTools mobile device profiles
│
├── wap_tests/                      # Twitch WAP (mobile) test suite
│   ├── conftest.py                 # mobile_driver fixture + --mobile-profile CLI flag
│   ├── pages/                      # Page Object Model (POM)
│   │   ├── base_page.py            # Shared helpers: wait, click, scroll, screenshot
│   │   ├── home_page.py            # Twitch home — load, dismiss banners, open search
│   │   ├── search_page.py          # Search page — type query, scroll, select card
│   │   └── streamer_page.py        # Streamer page — dismiss pop-ups, wait for player
│   ├── tests/
│   │   └── test_twitch_wap.py      # TC-WAP-001 → TC-WAP-003
│   └── utils/
│       └── helpers.py              # CI / headless detection helpers
│
├── api_tests/                      # REST Countries API test suite
│   ├── conftest.py                 # countries_client fixture
│   ├── utils/
│   │   └── api_client.py           # Thin requests.Session wrapper
│   └── tests/
│       └── test_rest_countries.py  # TC-API-001 → TC-API-006 (30+ parametrized cases)
│
├── screenshots/                    # Auto-created; stores evidence PNGs
├── reports/                        # Auto-created; HTML report output
│
├── conftest.py                     # Root hooks: dir creation, fail-screenshot on WAP tests
├── pytest.ini                      # Discovery, markers, logging config
├── requirements.txt
└── .gitignore
```

---

## Prerequisites

| Tool | Minimum version |
|------|-----------------|
| Python | 3.9 |
| Google Chrome | latest stable |
| ChromeDriver | auto-managed by `webdriver-manager` |

---

## Setup

```bash
# 1. Clone
git clone <your-repo-url>
cd WAP_QA

# 2. Create and activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running Tests

### Run everything

```bash
pytest
```

### Run only WAP tests

```bash
pytest wap_tests/tests -m wap -v
# or simply
pytest wap_tests/tests/
```

### Run only API tests

```bash
pytest api_tests/tests/ -v
```

### Change mobile device profile

```bash
pytest wap_tests/tests/ --mobile-profile=Galaxy_S20
```

Available profiles are defined in `config/mobile_profiles.py`:
- `Pixel_5` *(default)*
- `Galaxy_S20`
- `Custom_Mobile`

### Headless mode (CI / no display)

```bash
# Windows PowerShell
$env:HEADLESS="1"; pytest wap_tests/tests/

# macOS / Linux
HEADLESS=1 pytest wap_tests/tests/
```

### Generate HTML report

```bash
pytest --html=reports/report.html --self-contained-html
```

---

## WAP Test Cases

| ID | Title | Steps | Expected Result |
|----|-------|-------|-----------------|
| TC-WAP-001 | Search StarCraft II and open streamer | 1. Open Twitch mobile · 2. Click page body · 3. Click search icon · 4. Type "StarCraft II" · 5. Scroll ×2 · 6. Select one streamer · 7. On the streamer page wait until all is loaded and take a screenshot | URL is a channel page (not /search); screenshot saved |
| TC-WAP-002 | Search results not empty | Steps 1–5 of TC-WAP-001 | ≥1 stream card visible after search + scroll |
| TC-WAP-003 | Pop-up handler robustness | Steps 1–7 of TC-WAP-001 | `handle_popups()` completes without exception; screenshot saved |

---

## REST API Test Cases

**API:** [REST Countries](https://restcountries.com/v3.1) — found in [public-apis/public-apis](https://github.com/public-apis/public-apis)

### Validation strategy

| Validation type | Why it was chosen |
|---|---|
| **HTTP status code** | The primary API contract; immediately identifies server-side failures |
| **Response body type** | Confirms the API returns the documented structure (array vs object) |
| **Required field presence** | Detects silent schema changes without a version bump |
| **Value type assertion** | e.g. `population` must be `int`; prevents consumers from receiving wrong types |
| **Business-logic assertion** | Returned data must match the query (region == "Europe"); catches data routing bugs |
| **Error payload structure** | 404 bodies must contain `message`/`status`; validates error handling contracts |

### Test case table

| ID | Class | Description | Type | Parametrized |
|----|-------|-------------|------|--------------|
| TC-API-001a | `TestGetAllCountries` | `/all` returns HTTP 200 | Positive | No |
| TC-API-001b | `TestGetAllCountries` | Response is a JSON array | Positive | No |
| TC-API-001c | `TestGetAllCountries` | Returns >200 countries | Positive | No |
| TC-API-001d | `TestGetAllCountries` | Each item has name, region, cca2 | Schema | No |
| TC-API-002a | `TestGetCountryByValidName` | Valid name → HTTP 200 | Positive | ✓ (5 countries) |
| TC-API-002b | `TestGetCountryByValidName` | Response is a JSON array | Positive | ✓ |
| TC-API-002c | `TestGetCountryByValidName` | Returned name matches query | Business | ✓ |
| TC-API-002d | `TestGetCountryByValidName` | Has name, population (int) | Schema | ✓ |
| TC-API-003a | `TestGetCountryByInvalidName` | Invalid name → HTTP 404 | Negative | ✓ (4 names) |
| TC-API-003b | `TestGetCountryByInvalidName` | 404 body has message/status | Negative | ✓ |
| TC-API-004a | `TestGetCountriesByRegion` | Valid region → HTTP 200 | Positive | ✓ (5 regions) |
| TC-API-004b | `TestGetCountriesByRegion` | Result count ≥ minimum expected | Business | ✓ |
| TC-API-004c | `TestGetCountriesByRegion` | All results belong to queried region | Business | ✓ |
| TC-API-005a | `TestGetCountriesByInvalidRegion` | Invalid region → HTTP 404 | Negative | ✓ (4 values) |
| TC-API-006a | `TestGetCountryByAlphaCode` | Valid alpha code → HTTP 200 | Positive | ✓ (5 codes) |
| TC-API-006b | `TestGetCountryByAlphaCode` | Returned country matches code | Business | ✓ |
| TC-API-006c | `TestGetCountryByAlphaCode` | Invalid alpha code → HTTP 404 | Negative | ✓ (4 codes) |

---

## Design Decisions

### Page Object Model (POM)
Every page is a class with its own locators and action methods.  Tests never touch raw Selenium calls — they call high-level methods like `search.scroll_results(times=2)`.  When Twitch updates its DOM, only the relevant page object changes.

### BasePage
All shared Selenium logic (explicit waits, scroll, screenshot) lives in `BasePage`.  Each page object inherits from it, removing duplication and enforcing consistent wait strategies.

### Fixture design
- `mobile_driver` scope is `function` — fresh browser for each WAP test; no state bleed.
- `countries_client` scope is `session` — one HTTP session reused for all API tests; efficient.

### Headless / CI toggle
`HEADLESS=1` environment variable activates headless Chrome automatically, making it trivial to run in any CI pipeline without touching test code.

### `--mobile-profile` CLI flag
The mobile device profile is a runtime parameter, not a hardcoded value.  CI matrix builds can test against multiple devices in parallel by passing different `--mobile-profile` values.

### pytest.mark.parametrize
The API test suite uses parametrize extensively.  A single test function covers 5 country names, 5 regions, 5 alpha codes, and their negative counterparts — giving 30+ assertions with minimal code.

---

## License

MIT
