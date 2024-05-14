from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router, F

from DataBase import DBase

router = Router()


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    db = DBase.Database()
    user_id = str(message.from_user.id)
    group_name = db.student_group(user_id)
    if group_name is None:
        await message.answer(
            'Извините, но мы не знаем, кто вы.\n'
            f'Ваш id: `{user_id}`\n'
            'Если вы староста - отправьте его главному админу!',
            parse_mode='MARKDOWN'
        )
    else:
        await message.answer(f'Ваша группа - {group_name}')
