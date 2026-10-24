"""Part 1 — API tests against the public Reqres service.

Coverage:
- Happy path (200) with body assertions
- List pagination contract
- Missing resource (404)
- Invalid login payload (400)
"""

import pytest

pytestmark = pytest.mark.api


def test_get_single_user_returns_expected_profile(api_session, reqres_base_url):
    """Successful GET should return HTTP 200 and Janet Weaver's known profile."""
    response = api_session.get(f"{reqres_base_url}/users/2", timeout=15)

    assert response.status_code == 200, response.text
    body = response.json()

    assert "data" in body
    user = body["data"]
    assert user["id"] == 2
    assert user["email"] == "janet.weaver@reqres.in"
    assert user["first_name"] == "Janet"
    assert user["last_name"] == "Weaver"
    assert user["avatar"].startswith("https://")


def test_list_users_returns_paginated_data(api_session, reqres_base_url):
    """Page 2 of /users should include a non-empty data array and paging metadata."""
    response = api_session.get(
        f"{reqres_base_url}/users",
        params={"page": 2},
        timeout=15,
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["page"] == 2
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0
    assert "id" in body["data"][0]
    assert "email" in body["data"][0]


def test_get_missing_user_returns_404(api_session, reqres_base_url):
    """A user id that does not exist should return 404 with an empty body."""
    response = api_session.get(f"{reqres_base_url}/users/23", timeout=15)

    assert response.status_code == 404
    assert response.text in ("", "{}")


def test_login_without_password_returns_400(api_session, reqres_base_url):
    """Login with email only should fail with a clear 'Missing password' error."""
    response = api_session.post(
        f"{reqres_base_url}/login",
        json={"email": "eve.holt@reqres.in"},
        timeout=15,
    )

    assert response.status_code == 400, response.text
    body = response.json()
    assert "error" in body
    assert "password" in body["error"].lower()
