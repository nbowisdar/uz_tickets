from aiogram.fsm.state import State, StatesGroup


class Menu(StatesGroup):
    main = State()


class Channels(StatesGroup):
    menu = State()


class AddChannel(StatesGroup):
    channel_id = State()
    check = State()
    finish = State()


class DeleteChannel(StatesGroup):
    confirm = State()
