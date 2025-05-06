from playwright.async_api import Browser, BrowserContext

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

VIEWPORT = {"width": 1280, "height": 720}


async def create_stealth_context(browser: Browser) -> BrowserContext:
    """
    Creates a new browser context with spoofed headers and stealth enabled.
    """
    context = await browser.new_context(
        user_agent=DEFAULT_USER_AGENT,
        viewport=VIEWPORT,
        locale="en-US"
    )
    return context
