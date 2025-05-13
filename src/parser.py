import asyncio
import uuid
from pprint import pprint

import httpx
from playwright.async_api import async_playwright

from src.utils import convert_booking_url_to_api_url


class Parser:
    def __init__(self, url: str):
        self.url = url
        self.api_url = convert_booking_url_to_api_url(url)
        self.headers = {
            "accept": "application/json",
            "accept-language": "en,uk;q=0.9,en-US;q=0.8,ru;q=0.7",
            "origin": "https://booking.uz.gov.ua",
            "priority": "u=1, i",
            "referer": "https://booking.uz.gov.ua/",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "x-client-locale": "uk",
            "x-user-agent": "UZ/2 Web/1 User/guest",
        }
        self.api_interval = 5
        self.is_active = False

    async def update_headers(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # Generate a new session ID for each run
            session_id = str(uuid.uuid4())
            self.headers["x-session-id"] = session_id

            async def capture_cookies(response):
                if "api/v3" in response.url:
                    self.headers.update(
                        {
                            "cookie": "; ".join(
                                [
                                    f"{c['name']}={c['value']}"
                                    for c in await context.cookies()
                                ]
                            )
                        }
                    )

            page.on("response", capture_cookies)

            try:
                await page.goto(self.url, timeout=10_000)
                await page.wait_for_load_state("networkidle")
            except Exception as e:
                print(f"Error navigating to page: {e}")
            finally:
                await browser.close()

    async def get_api(self):
        async with httpx.AsyncClient(
            http2=True, timeout=httpx.Timeout(10.0), follow_redirects=True
        ) as client:
            try:
                response = await client.get(self.api_url, headers=self.headers)

                if response.status_code == 401:
                    print("Unauthorized - updating headers...")
                    await self.update_headers()
                    return

                print(f"HTTPX Request Status: {response.status_code}")
                try:
                    data = response.json()
                    pprint(data)
                except ValueError:
                    print("Received non-JSON response:", response.text[:200])

                return data

            except httpx.HTTPError as e:
                print(f"HTTPX request failed: {str(e)}")
                return None

    async def start(self):
        self.is_active = True
        await self.update_headers()
        print("Headers initialized")

        while self.is_active:
            try:
                await self.get_api()
                await asyncio.sleep(self.api_interval)
            except KeyboardInterrupt:
                self.is_active = False
                print("Parser stopped")


async def main():
    url = "https://booking.uz.gov.ua/search-trips/2200001/2210700/list?startDate=2025-05-16"
    parser = Parser(url)
    await parser.start()


if __name__ == "__main__":
    asyncio.run(main())
