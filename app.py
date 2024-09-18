import subprocess
import os
from playwright.async_api import async_playwright
import asyncio
import logging
import random
from datetime import datetime
from playwright.async_api import async_playwright, Error as PlaywrightError
import queue

# Ensure Playwright downloads its required browsers if not already installed
if not os.path.exists(os.path.expanduser("~/.cache/ms-playwright")):
    subprocess.run(["playwright", "install", "firefox"], check=True)
    subprocess.run(["playwright", "install", "chromium"], check=True)

# Log file configuration
log_file_path = 'simulation.log'

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler(log_file_path)])

# Global variables for controlling the simulation
is_running = True
semaphore = None
log_queue = queue.Queue()  # Queue for logging

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Pages to visit
INSIGHT_PAGES = [
    "https://www.exponentiel.ai/insights/openai-01-model-a-leap-into-the-future-of-ai-reasoning",
    "https://www.exponentiel.ai/insights/what-is-generative-ai-everything-you-need-to-know",
    "https://www.exponentiel.ai/insights/how-autonomous-agents-are-reshaping-business-strategies",
    "https://www.exponentiel.ai/insights/how-does-generative-ai-works",
    "https://www.exponentiel.ai/insights/preparing-for-artificial-general-intelligence",
    "https://www.exponentiel.ai/insights/autonomous-ai-agents-cant-scale-without-responsible-ai",
]

SERVICE_PAGES = [
    "https://www.exponentiel.ai/service/generative-ai-consulting",
    "https://www.exponentiel.ai/service/ai-software-development",
    "https://www.exponentiel.ai/service/autonomous-ai-agents",
    "https://www.exponentiel.ai/career",
    "https://www.exponentiel.ai/contact-us",
    "https://www.exponentiel.ai/insights"
]

CONTACT_PAGE = "https://www.exponentiel.ai/contact"

LINKEDIN_REFERRERS = [
    "https://www.linkedin.com/",
    "https://www.linkedin.com/feed/",
    "https://www.linkedin.com/in/",
    "https://www.linkedin.com/company/exponentiel-ai/",
    "https://www.linkedin.com/posts/exponentiel-ai_openais-01-model-a-leap-into-the-future-activity-7240316582336360450-zmQK?utm_source=share&utm_medium=member_desktop",
    "https://www.linkedin.com/posts/exponentiel-ai_artificialintelligence-agi-openai-activity-7196045842036731905-r4Pb?utm_source=share&utm_medium=member_desktop",
    "https://www.linkedin.com/posts/exponentiel-ai_ai-agi-artificialintelligence-activity-7196796554781847552-RyYU?utm_source=share&utm_medium=member_mobile",
    "https://www.linkedin.com/posts/exponentiel-ai_ai-openai-chatgpt4o-activity-7196436167993548801-DK_E?utm_source=share&utm_medium=member_desktop",
    "https://www.linkedin.com/posts/redabourji_openai-artificialintelligence-ai-activity-7240732079477473280-RQsX?utm_source=share&utm_medium=member_desktop",
    "https://www.linkedin.com/posts/redabourji_openais-o1-model-a-leap-into-the-future-activity-7240341353065283586-OBcy?utm_source=share&utm_medium=member_desktop",
    "https://www.linkedin.com/posts/redabourji_heres-an-early-preview-of-elevenlabs-music-activity-7194578928479440896--_XP?utm_source=share&utm_medium=member_desktop"
]

# Define a dictionary with user colors
USER_COLORS = {
    1: 'blue', 2: 'yellow', 3: 'green', 4: 'red', 5: 'cyan',
    6: 'magenta', 7: 'orange', 8: 'purple', 9: 'brown', 10: 'pink'
}

# Utility function for logging with color per user
def log_and_print(message, user_number=None):
    color = USER_COLORS.get(user_number, 'white')  # Default to white if user number not specified
    colored_message = f'<span style="color:{color};">{message}</span>'
    log_queue.put(colored_message)
    logging.info(message)  # Also log it in the file

# Function to simulate mouse movements (human-like interaction)
async def simulate_mouse_movement(page):
    movements = random.randint(3, 7)
    log_and_print(f"Simulating {movements} mouse movements")
    for _ in range(movements):
        await page.mouse.move(random.randint(100, 800), random.randint(100, 800))
        await asyncio.sleep(random.uniform(0.5, 2.0))

# Function to simulate scrolling (human-like interaction)
async def simulate_scrolling(page):
    scroll_count = random.randint(3, 8)
    log_and_print(f"Scrolling {scroll_count} times")
    for _ in range(scroll_count):
        await page.evaluate("window.scrollBy(0, {})".format(random.randint(100, 500)))
        await asyncio.sleep(random.uniform(2, 5))

# Function to simulate a user visiting pages using Playwright (mimicking human-like interactions)
async def simulate_user(user_number, semaphore):
    async with semaphore:
        log_and_print(f"\n--- User {user_number} Session Started ---", user_number=user_number)
        user_agent = random.choice(USER_AGENTS)
        linkedin_referrer = random.choice(LINKEDIN_REFERRERS)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(proxy={'server': 'socks5://localhost:9050'})
                context = await browser.new_context(
                    user_agent=user_agent,
                    viewport={'width': random.randint(1024, 1920), 'height': random.randint(768, 1080)}
                )
                page = await context.new_page()

                # Step 1: Visit LinkedIn referrer
                await page.goto(linkedin_referrer, timeout=60000)
                log_and_print(f"User {user_number} - Visiting LinkedIn: {linkedin_referrer}", user_number=user_number)
                await asyncio.sleep(random.uniform(20, 60))  # Simulate time spent on page
                await simulate_mouse_movement(page)
                await simulate_scrolling(page)

                # Step 2: Visit Insight Pages (2-3)
                visited_insights = random.sample(INSIGHT_PAGES, k=random.randint(2, 3))
                for insight_page in visited_insights:
                    log_and_print(f"User {user_number} - Visiting insight page: {insight_page}", user_number=user_number)
                    retry_count = 0
                    max_retries = 3
                    while retry_count < max_retries:
                        try:
                            await page.goto(insight_page, timeout=60000)
                            log_and_print(f"User {user_number} - Successfully visited: {insight_page}", user_number=user_number)
                            await simulate_mouse_movement(page)
                            await simulate_scrolling(page)
                            break
                        except PlaywrightError as e:
                            retry_count += 1
                            log_and_print(f"User {user_number} - Error visiting {insight_page}: {e} (Retry {retry_count}/{max_retries})", user_number=user_number)
                            await asyncio.sleep(2)
                            if retry_count == max_retries:
                                log_and_print(f"User {user_number} - Failed to visit {insight_page} after {max_retries} retries", user_number=user_number)
                    await asyncio.sleep(random.uniform(5*60, 10*60))  # Simulate reading time on insight page

                # Step 3: Visit Service Pages (2-3)
                visited_services = random.sample(SERVICE_PAGES, k=random.randint(2, 3))
                for service_page in visited_services:
                    log_and_print(f"User {user_number} - Visiting service page: {service_page}", user_number=user_number)
                    retry_count = 0
                    max_retries = 3
                    while retry_count < max_retries:
                        try:
                            await page.goto(service_page, timeout=60000)
                            log_and_print(f"User {user_number} - Successfully visited: {service_page}", user_number=user_number)
                            await simulate_mouse_movement(page)
                            await simulate_scrolling(page)
                            break
                        except PlaywrightError as e:
                            retry_count += 1
                            log_and_print(f"User {user_number} - Error visiting {service_page}: {e} (Retry {retry_count}/{max_retries})", user_number=user_number)
                            await asyncio.sleep(2)
                            if retry_count == max_retries:
                                log_and_print(f"User {user_number} - Failed to visit {service_page} after {max_retries} retries", user_number=user_number)
                    await asyncio.sleep(random.uniform(2, 5))  # Simulate time spent on service page

                # Step 4: Visit the Contact Page
                log_and_print(f"User {user_number} - Visiting contact page: {CONTACT_PAGE}", user_number=user_number)
                await page.goto(CONTACT_PAGE, timeout=60000)
                await simulate_mouse_movement(page)
                await simulate_scrolling(page)

                await browser.close()

        except PlaywrightError as e:
            log_and_print(f"User {user_number} - Playwright error: {e}", user_number=user_number)

        log_and_print(f"--- User {user_number} Session Finished ---\n", user_number=user_number)

# Main async function to simulate multiple users
async def main_simulation(total_users=10, concurrent_users=3):
    global semaphore
    semaphore = asyncio.Semaphore(concurrent_users)
    tasks = []

    for user_number in range(1, total_users + 1):
        task = asyncio.create_task(simulate_user(user_number, semaphore))
        tasks.append(task)
        await asyncio.sleep(random.uniform(1, 3))  # Random delay between starting users

    await asyncio.gather(*tasks)

# Function to run the simulation
def run_simulation():
    total_users = 10  # You can adjust this number
    concurrent_users = 3  # You can adjust this number
    logging.info(f"Starting simulation with {total_users} total users and {concurrent_users} concurrent users")
    asyncio.run(main_simulation(total_users, concurrent_users))
    logging.info("Simulation completed.")

if __name__ == "__main__":
    run_simulation()
