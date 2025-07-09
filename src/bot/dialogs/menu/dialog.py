from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Url
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.menu.controllers import get_menu_data
from bot.states import Menu

menu_dialog = Dialog(
    Window(
        Const("🏠Main menu"),
        Url(Const("Aiogram"), Format("{aiogram_link}")),
        Url(Const("Aiogram Dialog"), Format("{aiogram_dialog_link}")),
        state=Menu.main,
        getter=get_menu_data,
    )
)
