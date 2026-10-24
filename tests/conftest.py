"""Shared fixtures: HTTP session for API tests and Playwright setup/teardown for UI tests."""

import os

import pytest
import requests

REQRES_BASE_URL = "https://reqres.in/api"
DAVEAI_BASE_URL = "https://www.iamdave.ai"


@pytest.fixture(scope="session")
def reqres_base_url():
    return REQRES_BASE_URL


@pytest.fixture(scope="session")
def daveai_base_url():
    return DAVEAI_BASE_URL


@pytest.fixture(scope="session")
def api_session():
    """Reuse one HTTP session for all API tests. Closed after the suite finishes."""
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            # Reqres accepts this public demo key; override with REQRES_API_KEY if needed.
            "x-api-key": os.getenv("REQRES_API_KEY", "reqres-free-v1"),
        }
    )
    yield session
    session.close()
