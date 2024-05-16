from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router, F

from DataBase import DBase

router = Router()


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    db = DBase.Database()
    current_chat = f'{message.from_user.id}'
    student_id = db.get_student_id(current_chat)
    if current_chat == '622603789' and student_id is None:
        db.start()
        student_id = 1

    if student_id is None:
        await message.answer(
            'Извините, но мы не знаем, кто вы.\n'
            f'Ваш id: `{current_chat}`\n'
            'Если вы должны быть админом - отправьте его админу этой группы или главному админу!',
            parse_mode='MARKDOWN'
        )
    else:
        await message.answer(f'Доброго времени суток!')
