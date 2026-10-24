# QA Engineer assignment — DaveAI

Automated API and UI tests for the DaveAI QA take-home: Reqres API coverage plus Playwright checks on [iamdave.ai](https://www.iamdave.ai).

## Prerequisites

- Python 3.10+
- Chrome/Chromium (installed automatically by Playwright)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Optional: if Reqres starts rate-limiting the shared demo key, export your own key:

```bash
export REQRES_API_KEY="your-key"
```

## How to run the tests

All tests:

```bash
pytest
```

API only:

```bash
pytest tests/api_tests.py
```

UI only:

```bash
pytest tests/ui_tests.py
```

Headed browser (useful when explaining the UI flow in an interview):

```bash
pytest tests/ui_tests.py --headed --slowmo 300
```

## Locust (optional bonus)

Stay under the assignment cap of **100 API calls per day**. The script stops after 40 requests by default.

```bash
locust -f load_test.py --headless -u 5 -r 1 --run-time 20s
```

| Item | Plan |
| --- | --- |
| Endpoint | `GET https://reqres.in/api/users?page=1` |
| Users | 5 concurrent |
| Spawn rate | 1 user/second |
| Think time | 1–2 seconds |
| Cap | 40 requests (`LOCUST_MAX_REQUESTS`) |

## Project layout

```
tests/conftest.py     # HTTP session + URLs (setup/teardown)
tests/api_tests.py    # Reqres functional tests
tests/ui_tests.py     # Playwright tests for iamdave.ai
load_test.py          # Locust script
requirements.txt
```

Playwright’s `page` fixture opens Chromium before each UI test and closes it afterward.

## Test design choices

**API.** Cases follow STLC-style coverage: one happy path with field-level assertions, a list/pagination contract, a missing resource (404), and a negative login (missing password). These are the failures that actually break clients. A shared `requests.Session` keeps headers (including Reqres’ `x-api-key`) consistent and is closed after the suite.

**UI.** Selectors prefer accessible roles (`get_by_role`) over CSS, so tests stay closer to how a visitor uses the page. Cases check:

1. Homepage load — title, logo, and the main headline (broken branding is immediately visible).
2. Platform navigation — the primary product path from the header.
3. Homepage CTAs — Book Demo and How We Engage must be present or the site cannot convert.
4. Book Demo form fill — navigates to `/book-demo/`, fills Name and Work Email, and **does not submit**, so we do not pollute CRM data.

Cookie banners are dismissed when present so they cannot hide the header.

**Load.** One GET endpoint, 5 users, hard stop well below 100 calls so the public API is not abused.

## Interview notes

- API assertions check both status and payload, not just `== 200`.
- UI tests wait on URL/heading rather than fixed sleeps except for a short wait after the in-page Book Demo scroll.
- Failures print the HTTP body (`response.text`) to speed up debugging.
