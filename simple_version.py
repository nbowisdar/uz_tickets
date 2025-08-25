import asyncio
import json
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

BOT_TOKEN = "5669290917:AAHKN1qhFXt-F9fzCz8w-UvUQMoH7PTk68g"
TELEGRAM_CHAT_ID = "-4936367981"
CHECK_INTERVAL = 5


# ========== CONFIG ==========
DATA_FILE = Path("tracked_urls.json")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ========= STORAGE =========
def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"urls": {}, "snapshots": {}}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


state = load_data()


# ========= PLAYWRIGHT =========
async def fetch_page(url: str) -> str:
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="load")
        print(f"Loaded {url}")
        await asyncio.sleep(5)
        content = await page.content()
        await browser.close()
    return content


async def monitor_loop():
    while True:
        for url in list(state["urls"].keys()):
            try:
                html = await fetch_page(url)
                print(f"Checked {url}")
                # new_hash = hashlib.sha256(html.encode()).hexdigest()
                # old_hash = state["urls"][url].get("hash")

                # TODO check if
                if "Прямих рейсів не знайшлося" not in html:
                    print(f"Change detected at {url}")
                    # state["urls"][url]["hash"] = new_hash
                    state["snapshots"][url] = html
                    save_data(state)
                    await bot.send_message(
                        state["urls"][url]["owner"], f"🔄 Change detected at {url}"
                    )
            except Exception as e:
                print(f"Error checking {url}: {e}")
        await asyncio.sleep(CHECK_INTERVAL)


# ========= TELEGRAM HANDLERS =========
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Hello! Use /add <url> to track websites.")


@dp.message(Command("add"))
async def cmd_add(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Usage: /add <url>")
        return
    url = parts[1].strip()
    if url in state["urls"]:
        await message.answer("⚠️ Already tracking this URL.")
        return
    state["urls"][url] = {"owner": message.chat.id, "hash": None}
    save_data(state)
    await message.answer(f"✅ Added {url} for tracking.")


@dp.message(Command("remove"))
async def cmd_remove(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Usage: /remove <url>")
        return
    url = parts[1].strip()
    if url not in state["urls"]:
        await message.answer("⚠️ Not tracking this URL.")
        return
    del state["urls"][url]
    state["snapshots"].pop(url, None)
    save_data(state)
    await message.answer(f"🗑 Removed {url}.")


@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    if not state["urls"]:
        await message.answer("📭 No URLs being tracked.")
        return
    urls = "\n".join(state["urls"].keys())
    await message.answer(f"📌 Tracked URLs:\n{urls}")


@dp.message(Command("get"))
async def cmd_get(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Usage: /get <url>")
        return
    url = parts[1].strip()
    html = state["snapshots"].get(url)
    if not html:
        await message.answer("⚠️ No snapshot available yet.")
        return
    path = Path("snapshot.html")
    path.write_text(html, encoding="utf-8")
    await message.answer_document(FSInputFile(path))
    path.unlink()


# ========= MAIN =========
async def main():
    asyncio.create_task(monitor_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
