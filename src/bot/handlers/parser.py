import asyncio
from uuid import uuid4

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from dishka.integrations.aiogram import FromDishka
from sqlmodel import Session

from src.bot.core.config import get_config
from src.bot.utils.command import find_command_argument
from src.parser.models import Transfer
from src.parser.parser import Parser

config = get_config()
router = Router()


class SG(StatesGroup):
    info = State()
    price = State()
    confirm = State()


tasks = {}


@router.message(Command("check_ride"))
async def _(message: Message, state: FSMContext) -> None:
    link = find_command_argument(message.text)
    parser = Parser(link)
    transfer = await parser.get_info_once()
    await message.answer(transfer.show_message())


@router.message(Command("new_order"))
async def _(message: Message, state: FSMContext) -> None:
    link = find_command_argument(message.text)
    await state.update_data(link=link)
    await state.set_state(SG.info)

    await message.answer("Send Trains number (separated by space)\nExample: 220К 701К")


@router.message(SG.info)
async def _(message: Message, state: FSMContext, session: FromDishka[Session]) -> None:
    try:
        trains = message.text.casefold().split(" ")
    except Exception as e:
        await state.clear()
        return await message.reply(str(e))
    # url = "https://booking.uz.gov.ua/search-trips/2210700/2200001/list?startDate=2025-07-08"
    await state.update_data(trains=trains)
    await state.set_state(SG.price)

    await message.answer("Send min price")


@router.message(SG.price)
async def _(message: Message, state: FSMContext, session: FromDishka[Session]) -> None:
    try:
        price = int(message.text) * 100
    except Exception as e:
        await state.clear()
        return await message.reply(str(e))
    await state.update_data(price=price)
    await state.set_state(SG.confirm)

    await message.answer(
        "Confirm ?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Yes"),
                    KeyboardButton(text="No"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@router.message(SG.confirm, F.text.casefold() == "no")
async def no(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "No! 👎",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(SG.confirm, F.text.casefold() == "yes")
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    async def callback(transfer: Transfer) -> bool:
        for transfer in transfer.direct:
            for wc in transfer.train.wagon_classes:
                if wc.free_seats > 0:
                    if (
                        wc.price <= data["price"]
                        and transfer.train.number.casefold() in data["trains"]
                    ):
                        # TODO: Track event. Don't repeat notification!!!
                        await message.answer(
                            f"Notification!!! New ticket is available !!! For train, open link: {data["link"]}",
                            reply_markup=ReplyKeyboardRemove(),
                        )
                        return True

        return False

    parser = Parser(data["link"], callback=callback)
    parsing_task = asyncio.create_task(parser.start())

    task_id = f"{message.from_user.id}-{str(uuid4())}"
    tasks[task_id] = parsing_task

    await message.reply(
        "Start parsing...",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Cancel ❌", callback_data=f"cancel_parsing|{task_id}"
                    ),
                ]
            ],
        ),
    )


@router.callback_query(F.data.startswith("cancel_parsing|"))
async def callbacks_num(callback: CallbackQuery):
    action = callback.data.split("|")[1]

    msg = "Nothing to cancel 📛"
    task = tasks.pop(action)
    if task is not None and not task.done():
        task.cancel()
        msg = "Cancelled 👌"

    await callback.message.answer(
        msg,
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command("show_active_tasks"))
async def show_active_tasks(message: Message):
    t_count = 0
    for k, v in tasks.items():
        if message.from_user.id in k:
            t_count += 1

    await message.answer(f"My Active tasks: {t_count}")
