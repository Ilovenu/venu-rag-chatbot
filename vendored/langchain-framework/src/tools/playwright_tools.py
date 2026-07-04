# src/tools/playwright_tools.py
# Playwright browser actions wrapped as LangChain tools
# Built by Venu Madhav Mahadevu | Staff SDET Automation Architect

import asyncio
import base64
from typing import Optional
from langchain.tools import tool
from playwright.async_api import async_playwright, Page, Browser
import logging

logger = logging.getLogger(__name__)

# Global browser instance
_browser: Optional[Browser] = None
_page: Optional[Page] = None

async def get_page() -> Page:
    """Get or create a Playwright page instance."""
    global _browser, _page
    if _browser is None:
        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(headless=False, slow_mo=500)
    if _page is None or _page.is_closed():
        context = await _browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="en-US"
        )
        _page = await context.new_page()
    return _page

async def close_browser():
    """Close browser after tests."""
    global _browser, _page
    if _page:
        await _page.close()
        _page = None
    if _browser:
        await _browser.close()
        _browser = None


# ── LangChain Tools (AI can call these) ──────────────────────────────────────

@tool
async def navigate_to_url(url: str) -> str:
    """Navigate the browser to a given URL.
    Args:
        url: The full URL to navigate to (e.g., https://www.dell.com)
    Returns:
        Success message with current page title
    """
    try:
        page = await get_page()
        await page.goto(url, wait_until="networkidle", timeout=30000)
        title = await page.title()
        logger.info(f"Navigated to {url} | Title: {title}")
        return f"✅ Navigated to {url} | Page title: '{title}'"
    except Exception as e:
        return f"❌ Navigation failed: {str(e)}"


@tool
async def click_element(selector: str) -> str:
    """Click an element on the page using a CSS selector or text.
    Args:
        selector: CSS selector, XPath, or visible text of the element to click
    Returns:
        Success or failure message
    """
    try:
        page = await get_page()
        # Try multiple selector strategies
        strategies = [
            lambda: page.locator(selector).first.click(timeout=5000),
            lambda: page.get_by_text(selector).first.click(timeout=5000),
            lambda: page.get_by_role("button", name=selector).click(timeout=5000),
        ]
        for strategy in strategies:
            try:
                await strategy()
                return f"✅ Clicked element: '{selector}'"
            except:
                continue
        return f"❌ Could not click '{selector}' — element not found"
    except Exception as e:
        return f"❌ Click failed: {str(e)}"


@tool
async def fill_input_field(selector: str, value: str) -> str:
    """Fill a text input field with a value.
    Args:
        selector: CSS selector or label of the input field
        value: Text to type into the field
    Returns:
        Success or failure message
    """
    try:
        page = await get_page()
        strategies = [
            lambda: page.locator(selector).fill(value),
            lambda: page.get_by_label(selector).fill(value),
            lambda: page.get_by_placeholder(selector).fill(value),
        ]
        for strategy in strategies:
            try:
                await strategy()
                return f"✅ Filled '{selector}' with '{value}'"
            except:
                continue
        return f"❌ Could not fill '{selector}'"
    except Exception as e:
        return f"❌ Fill failed: {str(e)}"


@tool
async def extract_text_from_page(selector: str = "body") -> str:
    """Extract text content from the page or a specific element.
    Args:
        selector: CSS selector of element to extract text from (default: entire page)
    Returns:
        Extracted text content (truncated to 2000 chars)
    """
    try:
        page = await get_page()
        if selector == "body":
            text = await page.inner_text("body")
        else:
            text = await page.locator(selector).inner_text()
        return f"✅ Extracted text:\n{text[:2000]}"
    except Exception as e:
        return f"❌ Text extraction failed: {str(e)}"


@tool
async def take_screenshot(filename: str = "screenshot") -> str:
    """Take a screenshot of the current page.
    Args:
        filename: Name for the screenshot file (without extension)
    Returns:
        Path to saved screenshot
    """
    try:
        import os
        os.makedirs("reports/screenshots", exist_ok=True)
        path = f"reports/screenshots/{filename}.png"
        page = await get_page()
        await page.screenshot(path=path, full_page=True)
        return f"✅ Screenshot saved: {path}"
    except Exception as e:
        return f"❌ Screenshot failed: {str(e)}"


@tool
async def get_element_text(selector: str) -> str:
    """Get the text content of a specific element.
    Args:
        selector: CSS selector or role of the element
    Returns:
        Text content of the element
    """
    try:
        page = await get_page()
        text = await page.locator(selector).first.inner_text(timeout=5000)
        return f"✅ Element text: '{text}'"
    except Exception as e:
        return f"❌ Get text failed: {str(e)}"


@tool
async def check_element_visible(selector: str) -> str:
    """Check if an element is visible on the page.
    Args:
        selector: CSS selector of the element to check
    Returns:
        True/False with element details
    """
    try:
        page = await get_page()
        is_visible = await page.locator(selector).first.is_visible(timeout=5000)
        return f"✅ Element '{selector}' is {'VISIBLE' if is_visible else 'NOT VISIBLE'}"
    except Exception as e:
        return f"❌ Visibility check failed: {str(e)}"


@tool
async def wait_for_element(selector: str, state: str = "visible") -> str:
    """Wait for an element to reach a specific state.
    Args:
        selector: CSS selector of the element
        state: State to wait for — 'visible', 'hidden', 'attached', 'detached'
    Returns:
        Success message when element reaches the state
    """
    try:
        page = await get_page()
        await page.locator(selector).wait_for(state=state, timeout=10000)
        return f"✅ Element '{selector}' is now {state}"
    except Exception as e:
        return f"❌ Wait failed: {str(e)}"


@tool
async def get_current_url() -> str:
    """Get the current URL of the browser.
    Returns:
        Current page URL
    """
    try:
        page = await get_page()
        return f"✅ Current URL: {page.url}"
    except Exception as e:
        return f"❌ Failed to get URL: {str(e)}"


@tool
async def scroll_page(direction: str = "down", amount: int = 500) -> str:
    """Scroll the page up or down.
    Args:
        direction: 'up' or 'down'
        amount: Pixels to scroll (default: 500)
    Returns:
        Success message
    """
    try:
        page = await get_page()
        pixels = amount if direction == "down" else -amount
        await page.evaluate(f"window.scrollBy(0, {pixels})")
        return f"✅ Scrolled {direction} by {amount}px"
    except Exception as e:
        return f"❌ Scroll failed: {str(e)}"


@tool
async def select_dropdown_option(selector: str, value: str) -> str:
    """Select an option from a dropdown/select element.
    Args:
        selector: CSS selector of the select element
        value: Value or label of the option to select
    Returns:
        Success message
    """
    try:
        page = await get_page()
        await page.locator(selector).select_option(label=value)
        return f"✅ Selected '{value}' from dropdown '{selector}'"
    except Exception as e:
        try:
            page = await get_page()
            await page.locator(selector).select_option(value=value)
            return f"✅ Selected '{value}' from dropdown '{selector}'"
        except Exception as e2:
            return f"❌ Dropdown selection failed: {str(e2)}"


@tool
async def press_keyboard_key(key: str) -> str:
    """Press a keyboard key.
    Args:
        key: Key to press (e.g., 'Enter', 'Tab', 'Escape', 'ArrowDown')
    Returns:
        Success message
    """
    try:
        page = await get_page()
        await page.keyboard.press(key)
        return f"✅ Pressed key: {key}"
    except Exception as e:
        return f"❌ Key press failed: {str(e)}"


@tool
async def search_on_page(search_text: str) -> str:
    """Search for text within the current page.
    Args:
        search_text: Text to search for on the page
    Returns:
        Whether the text was found and its location
    """
    try:
        page = await get_page()
        content = await page.content()
        found = search_text.lower() in content.lower()
        if found:
            element = page.get_by_text(search_text, exact=False).first
            is_visible = await element.is_visible()
            return f"✅ Text '{search_text}' FOUND on page | Visible: {is_visible}"
        return f"❌ Text '{search_text}' NOT found on page"
    except Exception as e:
        return f"❌ Search failed: {str(e)}"


# All tools list for agent
PLAYWRIGHT_TOOLS = [
    navigate_to_url,
    click_element,
    fill_input_field,
    extract_text_from_page,
    take_screenshot,
    get_element_text,
    check_element_visible,
    wait_for_element,
    get_current_url,
    scroll_page,
    select_dropdown_option,
    press_keyboard_key,
    search_on_page,
]
