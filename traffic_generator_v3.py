import asyncio
from playwright.async_api import async_playwright, Error as PlaywrightError
import random
import time
import logging
from datetime import datetime, timedelta
import requests
import socket
import sys
from stem import Signal
from stem.control import Controller

async def check_ip(page):
    await page.goto("https://check.torproject.org/")
    tor_status = await page.text_content("body")
    if "Congratulations" in tor_status:
        logging.info("Tor is working correctly")
    else:
        logging.warning("Tor is NOT working")


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('simulation.log')])

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Pages to visit
INSIGHT_PAGES = [
    "https://www.exponentiel.ai/insights/what-is-generative-ai-everything-you-need-to-know",
    "https://www.exponentiel.ai/insights/openai-01-model-a-leap-into-the-future-of-ai-reasoning",
    "https://www.exponentiel.ai/insights/how-does-generative-ai-works"
]

SERVICE_PAGES = [
    "https://www.exponentiel.ai/service/generative-ai-consulting",
    "https://www.exponentiel.ai/service/autonomous-ai-agents",
    "https://www.exponentiel.ai/service/ai-software-development"
]

LINKEDIN_REFERRERS = [
    "https://www.linkedin.com/",
    "https://www.linkedin.com/feed/",
    "https://www.linkedin.com/in/",
    "https://www.linkedin.com/company/exponentiel-ai/"
]

def log_and_print(message):
    logging.info(message)

def get_residential_proxy():
    # Dummy proxy function, not in use since we're using Tor
    return f"http://{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}:8080"

async def get_tor_ip(page):
    try:
        await page.goto("https://check.torproject.org/")
        content = await page.text_content("body")
        if "Congratulations" in content:
            ip_element = await page.query_selector("strong")
            ip_address = await ip_element.text_content()
            return ip_address
        else:
            log_and_print("Tor is NOT working for this session")
            return 'Tor not working'
    except PlaywrightError as e:
        log_and_print(f"Error fetching Tor IP: {e}")
        return 'Unknown'


def get_dns():
    try:
        return socket.gethostbyname('resolver1.opendns.com')
    except:
        return 'Unknown'

async def simulate_mouse_movement(page):
    movements = random.randint(3, 7)
    log_and_print(f"Simulating {movements} mouse movements")
    for _ in range(movements):
        await page.mouse.move(random.randint(100, 800), random.randint(100, 800))
        await asyncio.sleep(random.uniform(0.5, 2.0))

async def visit_page(page, url, user_number, is_insight=False):
    log_and_print(f"User {user_number} - Visiting: {url}")
    try:
        await page.goto(url, wait_until="networkidle", timeout=120000)
        log_and_print(f"User {user_number} - Successfully loaded: {url}")
        
        await simulate_mouse_movement(page)

        scroll_count = random.randint(3, 8)
        log_and_print(f"User {user_number} - Scrolling {scroll_count} times")
        for _ in range(scroll_count):
            await page.evaluate("window.scrollBy(0, {})".format(random.randint(100, 500)))
            await asyncio.sleep(random.uniform(2, 5))

        # Set read_time between 5 and 10 minutes for insight pages, else a shorter duration for non-insight pages
        if is_insight:
            read_time = random.uniform(5 * 60, 10 * 60)  # 5 to 10 minutes in seconds
        else:
            read_time = random.uniform(15, 30)  # For non-insight pages

        log_and_print(f"User {user_number} - Reading for {read_time / 60:.2f} minutes")
        await asyncio.sleep(read_time)  # Simulate reading time

    except PlaywrightError as e:
        log_and_print(f"User {user_number} - Error loading page: {e}")
        return  # Skip further actions if the page couldn't be loaded successfully

    # If 70% chance to click a link
    if random.random() < 0.7:
        links = await page.query_selector_all('a')
        if links:
            link = random.choice(links)
            href = await link.get_attribute('href')
            log_and_print(f"User {user_number} - Clicking link: {href}")
            try:
                await link.click(timeout=30000)
                await asyncio.sleep(random.uniform(5, 10))
            except PlaywrightError as e:
                log_and_print(f"User {user_number} - Error clicking link: {e}")


def change_tor_circuit():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password='16:4C8928327D96E1A560DA795CF68F3139C1BB12903D0E4E3B495159E763')  # Use the password you set in torrc
            controller.signal(Signal.NEWNYM)
            log_and_print("Tor circuit renewed")
    except Exception as e:
        log_and_print(f"Error renewing Tor circuit: {e}")

async def simulate_user(user_number, semaphore):
    async with semaphore:
        log_and_print(f"\n--- User {user_number} Session Started ---")
        user_agent = random.choice(USER_AGENTS)
        linkedin_referrer = random.choice(LINKEDIN_REFERRERS)

        try:
            async with async_playwright() as p:
                # Close previous browser instance and open a new one
                browser = await p.firefox.launch(proxy={'server': 'socks5://localhost:9050'})
                context = await browser.new_context(
                    user_agent=user_agent,
                    viewport={'width': random.randint(1024, 1920), 'height': random.randint(768, 1080)}
                )
                page = await context.new_page()

                # Get Tor IP
                tor_ip = await get_tor_ip(page)
                log_and_print(f"User {user_number} - IP: {tor_ip}")

                await page.set_extra_http_headers({"Referer": linkedin_referrer})
                
                log_and_print(f"User {user_number} - Simulating LinkedIn browsing")
                await visit_page(page, linkedin_referrer, user_number)
                
                pages_to_visit = random.randint(2, 3)
                visited_insights = random.sample(INSIGHT_PAGES, k=min(pages_to_visit-1, len(INSIGHT_PAGES)))
                
                for url in visited_insights:
                    await visit_page(page, url, user_number, is_insight=True)
                
                service_page = random.choice(SERVICE_PAGES)
                await visit_page(page, service_page, user_number)

                await browser.close()
                
        except PlaywrightError as e:
            log_and_print(f"User {user_number} - Playwright error: {e}")
        except Exception as e:
            log_and_print(f"User {user_number} - Simulation error: {e}")

        log_and_print(f"--- User {user_number} Session Finished ---\n")


async def main():
    log_and_print("Starting main simulation...")
    total_users = 1000
    concurrent_users = 3
    semaphore = asyncio.Semaphore(concurrent_users)

    log_and_print(f"Simulating {total_users} users with max concurrency of {concurrent_users}")

    start_time = datetime.now()
    end_time = start_time + timedelta(hours=24)  # Simulate for 24 hours

    tasks = []
    for user_number in range(1, total_users + 1):
        task = asyncio.create_task(simulate_user(user_number, semaphore))
        tasks.append(task)

        delay = random.uniform(10, 30)
        log_and_print(f"Waiting {delay:.2f} seconds before starting next session")
        await asyncio.sleep(delay)

        if datetime.now() >= end_time:
            log_and_print("Reached end of simulation period")
            break

    await asyncio.gather(*tasks)
    log_and_print("Simulation completed.")

if __name__ == "__main__":
    log_and_print("Script started.")
    asyncio.run(main())
    log_and_print("Script finished.")
