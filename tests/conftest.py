"""Pytest configuration and fixtures for pyvista-wasm tests.

This module provides common fixtures for testing, including Playwright
fixtures for browser-based testing.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

import pytest


def extract_scene_data(html: str) -> dict:
    """Extract and parse the JSON scene data from generated HTML.

    Parameters
    ----------
    html : str
        HTML string containing a ``<script type="application/json" id="scene-data">``
        block.

    Returns
    -------
    dict
        Parsed scene configuration dictionary.

    """
    match = re.search(
        r'<script type="application/json" id="scene-data">\s*(.*?)\s*</script>',
        html,
        re.DOTALL,
    )
    if match is None:
        msg = "No scene-data JSON block found in HTML"
        raise ValueError(msg)
    return json.loads(match.group(1))


def extract_scene_data_from_js(js: str) -> dict:
    """Extract and parse the JSON scene data from generated JavaScript.

    The JS contains ``var __pvjsSceneData = {...};`` with the JSON object.

    Parameters
    ----------
    js : str
        JavaScript string from ``_generate_render_js()``.

    Returns
    -------
    dict
        Parsed scene configuration dictionary.

    """
    match = re.search(r"var __pvjsSceneData\s*=\s*(\{.*?\})\s*;", js, re.DOTALL)
    if match is None:
        msg = "No __pvjsSceneData found in JS"
        raise ValueError(msg)
    return json.loads(match.group(1))


if TYPE_CHECKING:
    from collections.abc import Generator

    from playwright.sync_api import Browser, BrowserContext, Page, Playwright


@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict[str, bool]:
    """Configure Playwright browser launch arguments.

    By default, launches browser in headless mode for CI/automated testing.
    Set PLAYWRIGHT_HEADLESS=0 environment variable to run in headed mode
    for debugging.

    Returns
    -------
    dict
        Browser launch arguments dictionary.

    """
    return {
        "headless": True,  # Always headless for CI and automated testing
    }


@pytest.fixture(scope="session")
def browser_context_args() -> dict[str, dict[str, int]]:
    """Configure Playwright browser context arguments.

    Returns
    -------
    dict
        Browser context arguments including viewport size.

    """
    return {
        "viewport": {"width": 1200, "height": 800},
    }


@pytest.fixture
def playwright_browser(
    playwright: Playwright,
    browser_type_launch_args: dict,
) -> Generator[Browser, None, None]:
    """Provide a Playwright browser instance for testing.

    This fixture creates a Chromium browser instance in headless mode
    by default. The browser is automatically closed after each test.

    Parameters
    ----------
    playwright : Playwright
        The Playwright instance provided by pytest-playwright.
    browser_type_launch_args : dict
        Browser launch arguments.

    Yields
    ------
    Browser
        A Playwright Browser instance.

    """
    browser = playwright.chromium.launch(**browser_type_launch_args)
    yield browser
    browser.close()


@pytest.fixture
def browser_context(
    playwright_browser: Browser,
    browser_context_args: dict,
) -> Generator[BrowserContext, None, None]:
    """Provide a Playwright browser context for testing.

    Parameters
    ----------
    playwright_browser : Browser
        The Playwright browser instance.
    browser_context_args : dict
        Browser context arguments.

    Yields
    ------
    BrowserContext
        A Playwright BrowserContext instance.

    """
    context = playwright_browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """Provide a Playwright page for testing.

    This fixture creates a new page in the browser context and automatically
    closes it after the test completes.

    Parameters
    ----------
    browser_context : BrowserContext
        The Playwright browser context.

    Yields
    ------
    Page
        A Playwright Page instance for browser automation.

    Examples
    --------
    >>> def test_with_playwright(page):
    ...     page.goto("https://example.com")
    ...     assert page.title() == "Example Domain"

    """
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def check_cdn_access(playwright: Playwright) -> bool:
    """Check if CDN (unpkg.com) is accessible for loading vtk.js.

    This fixture checks once per test session whether the test environment
    has access to external CDNs. Tests requiring CDN access can skip if
    this returns False.

    Parameters
    ----------
    playwright : Playwright
        The Playwright instance.

    Returns
    -------
    bool
        True if CDN is accessible, False otherwise.

    """
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        # Try to access unpkg.com
        response = page.goto("https://unpkg.com/", timeout=5000, wait_until="domcontentloaded")
        accessible = response is not None and response.ok
    except Exception:  # noqa: BLE001
        accessible = False
    finally:
        browser.close()

    return accessible
