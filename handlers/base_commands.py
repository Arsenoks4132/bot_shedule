from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from DataBase import DBase

router = Router()


# Хендлер на команду /start
@router.message(StateFilter(None), Command("start"))
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
            'Отправьте его админу этой группы или главному админу!',
            parse_mode='MARKDOWN'
        )
    else:
        await message.answer(
            'Доброго времени суток!\n'
            'Выберите любую команду из Меню чтобы запустить диалог!'
        )


# Хендлер команды отмены всех диалогов
@router.message(Command('cancel'))
async def cancel_all(
        message: Message,
        state: FSMContext
):
    await state.clear()
    await message.answer(
        'Действие прервано!\n'
        'Выберите любую команду из Меню чтобы начать новый диалог',
        reply_markup=ReplyKeyboardRemove()
    )