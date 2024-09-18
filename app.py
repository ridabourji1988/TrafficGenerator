import streamlit as st
import asyncio
import time
import threading
import logging
import random
from datetime import datetime
from playwright.async_api import async_playwright, Error as PlaywrightError
import queue

# Log file configuration
log_file_path = 'simulation.log'

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler(log_file_path)])

# Global variables for controlling the simulation
is_running = False
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
    1: 'blue',
    2: 'yellow',
    3: 'green',
    4: 'red',
    5: 'cyan',
    6: 'magenta',
    7: 'orange',
    8: 'purple',
    9: 'brown',
    10: 'pink'
}

# Utility function for logging with color per user
def log_and_print(message, user_number=None):
    # Assign color based on user number
    color = USER_COLORS.get(user_number, 'white')  # Default to white if user number not specified
    # Wrap the log message in a span with the color
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
                browser = await p.firefox.launch(proxy={'server': 'socks5://localhost:9050'})
                context = await browser.new_context(
                    user_agent=user_agent,
                    viewport={'width': random.randint(1024, 1920), 'height': random.randint(768, 1080)}
                )
                page = await context.new_page()

                # Step 1: Visit LinkedIn referrer
                await page.goto(linkedin_referrer, timeout=60000)
                log_and_print(f"User {user_number} - Visiting LinkedIn: {linkedin_referrer}", user_number=user_number)
                await asyncio.sleep(random.uniform(20, 60))  # Simulate time spent on page

                # Simulate mouse movements and scrolling like a real user
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

                            # Simulate mouse and scroll behavior after loading the page
                            await simulate_mouse_movement(page)
                            await simulate_scrolling(page)

                            break  # Exit the retry loop on success
                        except PlaywrightError as e:
                            retry_count += 1
                            log_and_print(f"User {user_number} - Error visiting {insight_page}: {e} (Retry {retry_count}/{max_retries})", user_number=user_number)
                            await asyncio.sleep(2)  # Backoff before retrying
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

                            # Simulate mouse and scroll behavior after loading the page
                            await simulate_mouse_movement(page)
                            await simulate_scrolling(page)

                            break  # Exit the retry loop on success
                        except PlaywrightError as e:
                            retry_count += 1
                            log_and_print(f"User {user_number} - Error visiting {service_page}: {e} (Retry {retry_count}/{max_retries})", user_number=user_number)
                            await asyncio.sleep(2)  # Backoff before retrying
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

# Function to start the simulation in a background thread
def start_simulation(total_users, concurrent_users):
    global is_running
    if not is_running:
        is_running = True
        asyncio.run(main_simulation(total_users, concurrent_users))
        is_running = False
        log_and_print("Simulation completed.")
    else:
        log_and_print("Simulation is already running!")

# Streamlit UI
st.title("Web Scraping Simulation with Streamlit")
st.write("Start or stop the simulation, and view the logs in real time.")

# Input parameters for simulation
total_users = st.number_input("Total users", min_value=1, max_value=10000, value=10)  # No limit on users now
concurrent_users = st.number_input("Concurrent users", min_value=1, max_value=100, value=3)

# Create start/stop buttons for simulation control
start_button = st.button("Start Simulation")
stop_button = st.button("Stop Simulation")

# Handle button clicks
if start_button:
    threading.Thread(target=start_simulation, args=(total_users, concurrent_users), daemon=True).start()

if stop_button:
    is_running = False
    log_and_print("Stopping simulation...")

# Custom CSS for log styling
st.write("""
    <style>
        .log-output {
            background-color: black;
            color: white;
            width: 100%;
            padding: 10px;
            border-radius: 5px;
        }
        .stTextArea [data-testid="stTextArea"] {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Display logs in a text area with black background and colored user messages
st.write("### Logs:")
log_placeholder = st.empty()

# Modified read_logs to return colored logs in HTML format
def read_logs():
    """Read the logs from the log queue (most recent on top)."""
    logs = list(log_queue.queue)[-100:]  # Keep the last 100 logs
    logs.reverse()  # Reverse for most recent on top
    return '<br>'.join(logs)

# Periodically update the logs in the main thread (every 3 seconds)
log_key = 0
while True:
    logs_html = read_logs()  # Read logs and format them as HTML
    log_placeholder.markdown(f'<div class="log-output">{logs_html}</div>', unsafe_allow_html=True)  # Display logs
    log_key += 1  # Increment the key for the next iteration
    time.sleep(3)  # Sleep for 3 seconds before updating again
