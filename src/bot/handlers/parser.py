from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from dishka.integrations.aiogram import FromDishka
from sqlmodel import Session
from parser.models import Transfer
from src.bot.core.config import get_config
from src.bot.utils.command import find_command_argument
from src.parser.parser import Parser

config = get_config()
router = Router()


class SG(StatesGroup):
    info = State()


@router.message(Command("check_ride"))
async def _(message: Message, state: FSMContext) -> None:
    link = find_command_argument(message.text)

    # await state.set_state(SG.uz_link)
    parser = Parser(link)
    transfer = await parser.get_info_once()
    await message.answer(transfer.show_message())


@router.message(Command("new_order"))
async def _(message: Message, state: FSMContext) -> None:
    link = find_command_argument(message.text)
    await state.update_data(link=link)
    await state.set_state(SG.info)
    
    await message.answer(
        "Send Train number and min price (separated by space)\nExample: 220К 600"
    )


@router.message(SG.info)
async def _(message: Message, state: FSMContext, session: FromDishka[Session]) -> None:
    train, price = message.text.split(" ")
    price = int(price) * 100
    # url = "https://booking.uz.gov.ua/search-trips/2210700/2200001/list?startDate=2025-07-08"
    await state.update_data(train=train, price=price)
    
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


@router.message(SG.info, F.text.casefold() == "no")
async def process_dont_like_write_bots(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Not bad not terrible.\nSee you soon.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(SG.info, F.text.casefold() == "yes")
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    
    
    async def callback(transfer: Transfer) -> None:
        for t in transfer.direct:
            for wc in t.train.wagon_classes:
                if wc.free_seats > 0:
                    if wc.price <= data["price"] and wc.train.number == data["train"]:
                        # TODO: Track event. Don't repeat notification!!!            
                        await message.answer(
                            f"Notification!!! New ticket is available !!! For train, open link: {data["link"]}",
                            reply_markup=ReplyKeyboardRemove(),
                        )
    
    parser = Parser(data["link"], cb=callback)
    await parser.start()
    
    
    
    await message.reply(
        "Start parsing...",
        reply_markup=ReplyKeyboardRemove(),
    )