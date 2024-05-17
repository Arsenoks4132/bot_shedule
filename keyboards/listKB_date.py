from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

from datetime import date


class DateCallbackFactory(CallbackData, prefix="date_fab"):
    value: date
    txt_date: str


def make_list_keyboard(items: list[date]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        date_text = item.strftime('%d.%m.%Y')
        builder.button(
            text=date_text,
            callback_data=DateCallbackFactory(value=item, txt_date=date_text)
        )
    builder.adjust(1)
    return builder.as_markup()
