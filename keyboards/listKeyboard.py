from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData


class GroupCallbackFactory(CallbackData, prefix="group_fab"):
    value: str


def make_list_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(
            text=item,
            callback_data=GroupCallbackFactory(value=item)
        )
    builder.adjust(1)
    return builder.as_markup()
