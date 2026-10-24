"""Part 2 — UI tests for https://www.iamdave.ai using Playwright.

These cases target things a visitor actually uses: brand identity, primary
navigation, homepage CTAs, and the Book Demo lead form. The form is filled
but not submitted so we do not create fake leads.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


def _dismiss_cookie_banner(page: Page) -> None:
    """Close common consent banners if they appear; ignore when they do not."""
    for name in ("Accept", "Accept All", "Allow all", "I agree", "Got it"):
        button = page.get_by_role("button", name=re.compile(name, re.I))
        if button.count() and button.first.is_visible():
            button.first.click()
            return


def test_homepage_loads_with_title_and_heading(page: Page, daveai_base_url: str):
    """Homepage should load with the DaveAI title, logo, and main headline."""
    response = page.goto(daveai_base_url, wait_until="domcontentloaded")
    assert response is not None
    assert response.ok, f"Homepage returned HTTP {response.status}"

    _dismiss_cookie_banner(page)

    expect(page).to_have_title(re.compile(r"DaveAI", re.I))
    expect(
        page.get_by_role(
            "heading",
            name="Automotive Intelligence Across Every Function",
        )
    ).to_be_visible()

    logo = page.locator("img[src*='DaveAI_Logo']").locator("visible=true").first
    expect(logo).to_be_visible()


def test_platform_navigation_opens_platform_page(page: Page, daveai_base_url: str):
    """Header Platform link should take the user to /platform with product copy."""
    page.goto(daveai_base_url, wait_until="domcontentloaded")
    _dismiss_cookie_banner(page)

    page.get_by_role("link", name="Platform").first.click()
    page.wait_for_url(re.compile(r"/platform"), timeout=15000)

    expect(page).to_have_url(re.compile(r"iamdave\.ai/platform"))
    expect(
        page.get_by_role("heading", name=re.compile(r"Human-like", re.I))
    ).to_be_visible()


def test_homepage_shows_primary_cta_and_engagement_section(
    page: Page, daveai_base_url: str
):
    """Visitors should see Book Demo and the How We Engage section on the homepage."""
    page.goto(daveai_base_url, wait_until="domcontentloaded")
    _dismiss_cookie_banner(page)

    expect(page.get_by_role("link", name="Book Demo").first).to_be_visible()
    expect(page.get_by_role("heading", name="How We Engage")).to_be_visible()
    expect(page.get_by_role("link", name=re.compile(r"See DaveAI in Action", re.I))).to_be_visible()


def test_book_demo_form_accepts_input(page: Page, daveai_base_url: str):
    """Book Demo should expose a lead form; fill fields without submitting."""
    page.goto(daveai_base_url, wait_until="domcontentloaded")
    _dismiss_cookie_banner(page)

    page.get_by_role("link", name="Book Demo").first.click()
    page.wait_for_url(re.compile(r"/book-demo"), timeout=15000)

    name = page.locator("#form-field-name_free_audit")
    email = page.locator("#form-field-email")

    expect(name).to_be_visible(timeout=15000)
    expect(email).to_be_visible(timeout=15000)

    name.fill("QA Candidate")
    email.fill("qa.candidate@example.com")

    expect(name).to_have_value("QA Candidate")
    expect(email).to_have_value("qa.candidate@example.com")
