import asyncio
from playwright.async_api import async_playwright  # This is necessary
import random
async def check_tor_connection(page):
    await page.goto("https://check.torproject.org/")
    content = await page.text_content("body")
    if "Congratulations" in content:
        print("Tor is working correctly")
    else:
        print("Tor is NOT working")

async def main():
    async with async_playwright() as p:
        # Launch Firefox with Tor proxy
        browser = await p.firefox.launch(
            proxy={'server': 'socks5://localhost:9050'}
        )
        context = await browser.new_context()
        page = await context.new_page()

        # Test Tor connection
        await check_tor_connection(page)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
