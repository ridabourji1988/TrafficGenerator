import asyncio
from playwright.async_api import async_playwright, Error as PlaywrightError
from stem import Signal
from stem.control import Controller
import socks
import socket
import random
import time
import requests


def get_ip_and_dns():
    try:
        response = requests.get('https://ifconfig.me/all.json', proxies={'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'})
        data = response.json()
        ip = data.get('ip_addr', 'Unknown')
        resolver = socket.gethostbyname('resolver1.opendns.com')
        return ip, resolver
    except Exception as e:
        print(f"Error getting IP and DNS: {e}")
        return 'Unknown', 'Unknown'

def renew_tor_ip():
    print("Attempting to renew Tor IP...")
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            print("Tor IP renewed successfully.")
    except Exception as e:
        print(f"Error renewing Tor IP: {e}")

def set_tor_proxy():
    print("Setting up Tor proxy...")
    try:
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        print("Tor proxy set up completed.")
    except Exception as e:
        print(f"Error setting up Tor proxy: {e}")

async def simulate_user(urls, user_number, semaphore):
    async with semaphore:
        print(f"\n--- Starting simulation for User {user_number} ---")
        renew_tor_ip()
        set_tor_proxy()
        print("Waiting for IP change to take effect...")
        await asyncio.sleep(5)

        ip, dns = get_ip_and_dns()
        print(f"User {user_number} - Current IP: {ip}")
        print(f"User {user_number} - Current DNS: {dns}")

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(proxy={'server': 'socks5://127.0.0.1:9050'})
                page = await browser.new_page()
                
                for url in urls:
                    try:
                        print(f"User {user_number} - Visiting: {url}")
                        await page.goto(url)
                        print(f"User {user_number} - Successfully loaded: {url}")
                        
                        # Simulate scrolling
                        scroll_count = random.randint(1, 5)
                        print(f"User {user_number} - Simulating {scroll_count} scrolls")
                        for _ in range(scroll_count):
                            await page.mouse.wheel(0, random.randint(100, 500))
                            await asyncio.sleep(random.uniform(1, 3))
                        
                        # Simulate reading time
                        read_time = random.uniform(5, 15)
                        print(f"User {user_number} - Simulating reading for {read_time:.2f} seconds")
                        await asyncio.sleep(read_time)
                        
                        # Optionally click on links
                        links = await page.query_selector_all('a')
                        if links:
                            link = random.choice(links)
                            print(f"User {user_number} - Clicking a random link on {url}")
                            await link.click()
                            await asyncio.sleep(random.uniform(5, 10))
                    except Exception as e:
                        print(f"User {user_number} - Error visiting {url}: {e}")
                
                await browser.close()
        except PlaywrightError as e:
            print(f"User {user_number} - Playwright error: {e}")
        except Exception as e:
            print(f"User {user_number} - Error in user simulation: {e}")

        print(f"--- Finished simulation for User {user_number} ---\n")

async def main():
    print("Starting main simulation...")
    urls = [
        "https://www.exponentiel.ai/service/generative-ai-consulting",
        "https://www.exponentiel.ai/insights/what-is-generative-ai-everything-you-need-to-know",
        "https://www.exponentiel.ai/insights/openai-01-model-a-leap-into-the-future-of-ai-reasoning",
        "https://www.exponentiel.ai/service/autonomous-ai-agents",
        "https://www.exponentiel.ai/service/ai-software-development",
        "https://www.exponentiel.ai/insights/how-does-generative-ai-works"
    ]
    total_users = 720
    concurrent_users = 10  # Number of users to simulate concurrently
    batches = total_users // concurrent_users
    semaphore = asyncio.Semaphore(concurrent_users)

    print(f"Simulating {total_users} users in batches of {concurrent_users}")

    for batch in range(batches):
        tasks = []
        for i in range(concurrent_users):
            user_number = batch * concurrent_users + i + 1
            selected_urls = random.sample(urls, k=random.randint(1, len(urls)))
            task = asyncio.create_task(simulate_user(selected_urls, user_number, semaphore))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        print(f"Completed batch {batch + 1} of {batches}")
        
        # Optional: Add a small delay between batches
        await asyncio.sleep(5)

    print("Simulation completed.")

if __name__ == "__main__":
    print("Script started.")
    asyncio.run(main())
    print("Script finished.")