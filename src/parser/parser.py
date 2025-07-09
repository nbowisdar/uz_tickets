import asyncio
import uuid
from typing import Awaitable, Callable

import httpx
from fake_useragent import UserAgent
from playwright.async_api import async_playwright

from src.parser.models import Transfer
from src.parser.utils import convert_booking_url_to_api_url

ua = UserAgent()


def get_headers() -> dict:
    return {
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
        "user-agent": ua.random,
        "x-client-locale": "uk",
        "x-user-agent": "UZ/2 Web/1 User/guest",
    }


class Parser:
    def __init__(self, url: str):
        self.url = url
        self.api_url = convert_booking_url_to_api_url(url)
        self.api_interval = 5
        self.is_active = False
        self.headers = get_headers()
        self.prev_transfer: Transfer = None
        self.cb: Awaitable[Callable] = None

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

    async def get_api(self) -> Transfer:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_url, headers=self.headers)

            if response.status_code == 401:
                print("Unauthorized - updating headers...")
                await self.update_headers()
                return

            print(f"HTTPX Request Status: {response.status_code}")
            return Transfer(**response.json())

    async def get_info_once(self) -> Transfer:
        await self.update_headers()
        print("Headers initialized")
        return await self.get_api()

    async def start(self):
        self.is_active = True
        await self.update_headers()
        print("Headers initialized")

        while self.is_active:
            try:
                self.prev_transfer = await self.get_api()
                if self.cb:
                    await self.cb(self.prev_transfer)
                await asyncio.sleep(self.api_interval)
            except KeyboardInterrupt:
                self.is_active = False
                print("Parser stopped")

    def stop(self):
        self.is_active = False


async def main():
    url = "https://booking.uz.gov.ua/search-trips/2210700/2200001/list?startDate=2025-07-08"
    parser = Parser(url)
    await parser.start()


if __name__ == "__main__":
    asyncio.run(main())
