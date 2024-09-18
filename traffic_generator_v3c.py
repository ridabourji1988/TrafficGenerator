import streamlit as st
import asyncio
import time
import threading
import logging
import random
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Error as PlaywrightError
from stem import Signal
from stem.control import Controller

# Log file configuration
log_file_path = 'simulation.log'

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler(log_file_path)])

# Global flag to control the simulation
is_running = False
semaphore = None  # Will be initialized later for limiting concurrent users

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

# Function to simulate a user visiting pages using Playwright
async def simulate_user(user_number, semaphore):
    async with semaphore:
        log_and_print(f"\n--- User {user_number} Session Started ---")
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

                await page.goto(linkedin_referrer, timeout=60000)
                log_and_print(f"User {user_number} - Visiting LinkedIn: {linkedin_referrer}")
                await asyncio.sleep(random.uniform(2, 5))  # Simulate time spent on page

                for _ in range(random.randint(2, 3)):
                    service_page = random.choice(SERVICE_PAGES)
                    log_and_print(f"User {user_number} - Visiting service page: {service_page}")

                    retry_count = 0
                    max_retries = 3

                    while retry_count < max_retries:
                        try:
                            await page.goto(service_page, timeout=60000)
                            log_and_print(f"User {user_number} - Successfully visited: {service_page}")
                            break  # Exit the retry loop on success
                        except PlaywrightError as e:
                            retry_count += 1
                            log_and_print(f"User {user_number} - Error visiting {service_page}: {e} (Retry {retry_count}/{max_retries})")
                            await asyncio.sleep(2)  # Backoff before retrying
                            if retry_count == max_retries:
                                log_and_print(f"User {user_number} - Failed to visit {service_page} after {max_retries} retries")

                    await asyncio.sleep(random.uniform(2, 5))  # Simulate time spent on page

                await browser.close()

        except PlaywrightError as e:
            log_and_print(f"User {user_number} - Playwright error: {e}")

        log_and_print(f"--- User {user_number} Session Finished ---\n")


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
        st.success("Simulation completed.")
    else:
        st.warning("Simulation is already running!")


# Streamlit UI
st.title("Web Scraping Simulation with Streamlit")
st.write("Start or stop the simulation, and view the logs in real time.")

# Input parameters for simulation
total_users = st.number_input("Total users", min_value=1, max_value=1000, value=10)
concurrent_users = st.number_input("Concurrent users", min_value=1, max_value=100, value=3)

# Create start/stop buttons for simulation control
start_button = st.button("Start Simulation")
stop_button = st.button("Stop Simulation")

# Handle button clicks
if start_button:
    threading.Thread(target=start_simulation, args=(total_users, concurrent_users), daemon=True).start()

if stop_button:
    is_running = False
    st.warning("Stopping simulation...")

# Function to read logs from the log file
def read_logs():
    """Read the last 100 lines from the log file."""
    try:
        with open(log_file_path, 'r') as f:
            logs = f.readlines()
        return ''.join(logs[-100:])  # Limit to last 100 lines for display
    except FileNotFoundError:
        return "Log file not found."

# Display logs with periodic refresh
st.write("### Logs:")
log_placeholder = st.empty()

# Periodically update the logs in the main thread (every 3 seconds)
log_key = 0
while True:
    logs = read_logs()  # Read logs from the file
    log_placeholder.text_area("Log Output", logs, height=300, key=f"log_area_{log_key}")  # Unique key for each update
    log_key += 1  # Increment the key for the next iteration
    time.sleep(3)  # Sleep for 3 seconds before updating again
