from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram import Router

router = Router()


# Хендлер на любое сообщение при отсутствии начатого диалога
@router.message(StateFilter(None))
async def any_message(
        message: Message
):
    await message.answer(
        'Чтобы начать диалог, выберите любую команду из Меню'
    )
