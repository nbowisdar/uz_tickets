import asyncio
import uuid
import random
from pprint import pprint

from src.utils import convert_booking_url_to_api_url
from playwright.async_api import async_playwright

class Parser:
    def __init__(self, url: str):
        self.url = url
        self.api_url = convert_booking_url_to_api_url(url)
        self.base_headers = {
            "accept": "application/json",
            "accept-language": self._generate_accept_language(),
            "origin": "https://booking.uz.gov.ua",
            "priority": "u=1, i",
            "referer": "https://booking.uz.gov.ua/",
            "sec-ch-ua": self._generate_sec_ch_ua(),
            "sec-ch-ua-mobile": random.choice(["?0", "?1"]),
            "sec-ch-ua-platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": self._generate_user_agent(),
            "x-client-locale": random.choice(["uk", "en", "ru"]),
            "x-user-agent": "UZ/2 Web/1 User/guest",
        }
        self.headers = self.base_headers.copy()
        self.api_interval = 5
        self.is_active = False
        self.browser = None
        self.context = None
        self.page = None

    def _generate_user_agent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
        ]
        return random.choice(user_agents)

    def _generate_accept_language(self):
        languages = ["en,uk;q=0.9,en-US;q=0.8,ru;q=0.7", "uk,en;q=0.9,ru;q=0.8", "en-US,en;q=0.9,uk;q=0.8"]
        return random.choice(languages)

    def _generate_sec_ch_ua(self):
        brands = [
            '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            '"Firefox";v="129", "Not.A/Brand";v="8"',
            '"Chromium";v="135", "Google Chrome";v="135", "Not.A/Brand";v="24"',
        ]
        return random.choice(brands)

    async def update_headers(self):
        # Update headers with new random values
        self.headers = self.base_headers.copy()
        self.headers["x-session-id"] = str(uuid.uuid4())
        self.headers["accept-language"] = self._generate_accept_language()
        self.headers["sec-ch-ua"] = self._generate_sec_ch_ua()
        self.headers["sec-ch-ua-mobile"] = random.choice(["?0", "?1"])
        self.headers["sec-ch-ua-platform"] = random.choice(['"Windows"', '"macOS"', '"Linux"'])
        self.headers["user-agent"] = self._generate_user_agent()
        self.headers["x-client-locale"] = random.choice(["uk", "en", "ru"])

        async def capture_cookies(response):
            if "api/v3" in response.url:
                self.headers.update(
                    {
                        "cookie": "; ".join(
                            [
                                f"{c['name']}={c['value']}"
                                for c in await self.context.cookies()
                            ]
                        )
                    }
                )

        self.page.on("response", capture_cookies)

        try:
            await self.page.goto(self.url, timeout=10_000)
            await self.page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Error navigating to page: {e}")

    async def initialize_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def get_api(self):
        # Update headers with new random values for each request
        await self.update_headers()

        try:
            # Reload the page to fetch new data
            response = await self.page.reload( timeout=10_000)
            
            if response.status == 401:
                print("Unauthorized - updating headers...")
                await self.update_headers()
                return None

            print(f"Playwright Request Status: {response.status}")
            try:
                data = await response.json()
                pprint(data)
                return data
            except ValueError:
                print("Received non-JSON response:", (await response.text())[:200])
                return None

        except Exception as e:
            print(f"Playwright request failed: {str(e)}")
            return None

    async def start(self):
        self.is_active = True
        await self.initialize_browser()
        await self.update_headers()
        print("Headers initialized and browser started")

        while self.is_active:
            try:
                await self.get_api()
                await asyncio.sleep(self.api_interval)
            except KeyboardInterrupt:
                self.is_active = False
                print("Parser stopped")
            finally:
                if self.is_active is False and self.browser:
                    await self.browser.close()

async def main():
    url = "https://booking.uz.gov.ua/search-trips/2210700/2208001/list?startDate=2025-09-09"
    parser = Parser(url)
    await parser.start()

if __name__ == "__main__":
    asyncio.run(main())