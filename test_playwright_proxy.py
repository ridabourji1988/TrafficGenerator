# test_playwright_proxy.py

import asyncio
from playwright.async_api import async_playwright, Error as PlaywrightError

async def test_playwright_proxy():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(proxy={'server': 'socks5://localhost:9050'})
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto('https://check.torproject.org/')
            title = await page.title()
            print(f"Page title: {title}")
            await browser.close()
    except PlaywrightError as e:
        print(f"Playwright error: {e}")

if __name__ == "__main__":
    asyncio.run(test_playwright_proxy())
