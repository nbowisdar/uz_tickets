import asyncio
import json
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand, FSInputFile
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

BOT_TOKEN = "5669290917:AAHKN1qhFXt-F9fzCz8w-UvUQMoH7PTk68g"
TELEGRAM_CHAT_ID = "-4936367981"
CHECK_INTERVAL = 10

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
is_monitoring = False


# ========= PLAYWRIGHT =========
async def fetch_page(page, url: str) -> str:
    await page.goto(url, wait_until="load")
    await asyncio.sleep(5)
    content = await page.content()
    return content


async def monitor_loop():
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        while True:
            if not is_monitoring:
                await asyncio.sleep(CHECK_INTERVAL)
                continue
            for url in list(state["urls"].keys()):
                try:
                    html: str = await fetch_page(page, url)
                    print(f"Checked {url}")

                    if "потяг від" in html:
                        print(f"Change detected at {url}")
                        state["snapshots"][url] = html
                        save_data(state)
                        await bot.send_message(
                            state["urls"][url]["owner"], f"🔄 Change detected at {url}"
                        )
                except Exception as e:
                    print(f"Error checking {url}: {e}")
                    # Browser will be relaunched on next fetch due to fetch_page logic
            await asyncio.sleep(CHECK_INTERVAL)


# ========= TELEGRAM HANDLERS =========
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
*Welcome to the Website Monitoring Bot!* 🚀

Here are the available commands:
- `/help` - Show this help message
- `/add <url>` - Start tracking a website
- `/rm <url>` - Stop tracking a website
- `/ls` - List all tracked websites
- `/get <url>` - Get the latest snapshot of a website
- `/start` - Start monitoring
- `/stop` - Stop monitoring

Use the menu button below to access these commands easily!
"""
    await message.answer(help_text, parse_mode="Markdown")


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


@dp.message(Command("rm"))
async def cmd_remove(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Usage: /rm <url>")
        return
    url = parts[1].strip()
    if url not in state["urls"]:
        await message.answer("⚠️ Not tracking this URL.")
        return
    del state["urls"][url]
    state["snapshots"].pop(url, None)
    save_data(state)
    await message.answer(f"🗑 Removed {url}.")


@dp.message(Command("ls"))
async def cmd_list(message: types.Message):
    icon = "🚀" if is_monitoring else "⛔️"
    status = f"Active: {icon} | Interval: {CHECK_INTERVAL} seconds"
    if not state["urls"]:
        msg = "📭 No URLs being tracked."
    else:
        urls = "\n".join(state["urls"].keys())
        msg = f"📌 Tracked URLs:\n{urls}"
    await message.answer(status + "\n\n" + msg)


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


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    global is_monitoring
    is_monitoring = False
    await message.answer("⛔️ Monitoring stopped.")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global is_monitoring
    is_monitoring = True
    await message.answer("🚀 Monitoring started.")


# ========= MAIN =========
async def main():
    # Set up bot menu commands
    commands = [
        BotCommand(command="/help", description="Show help message"),
        BotCommand(command="/add", description="Add a URL to track"),
        BotCommand(command="/rm", description="Remove a URL from tracking"),
        BotCommand(command="/ls", description="List tracked URLs"),
        BotCommand(command="/get", description="Get a URL's snapshot"),
        BotCommand(command="/start", description="Start monitoring"),
        BotCommand(command="/stop", description="Stop monitoring"),
    ]
    await bot.set_my_commands(commands)

    asyncio.create_task(monitor_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
