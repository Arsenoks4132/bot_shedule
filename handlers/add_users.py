from aiogram.types import Message
from aiogram.filters.command import Command, CommandObject
from aiogram import Router, F

from DataBase import DBase

router = Router()


@router.message(Command('add_student'))
async def new_student(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            'Ошибка: не переданы айди и название группы'
        )
        return
    try:
        student_chat_id, student_group_name = command.args.split(' ', maxsplit=1)
    except ValueError:
        await message.answer(
            'Ошибка: неправильный формат команды. Пример:\n'
            '/add_student <id> <group_name>'
        )
        return

    db = DBase.Database()
    current_chat = f'{message.from_user.id}'

    if not db.is_powered(student_group_name, current_chat):
        await message.answer(
            'У вас недостаточно прав, чтобы добавлять студентов в эту группу!'
        )
        return

    execution_code = db.add_student(student_group_name, student_chat_id)

    if execution_code < 0:
        await message.answer(
            'Что-то пошло не так, попробуйте ещё раз!'
        )
        return

    if execution_code == 0:
        await message.answer(
            'Этот студент уже был добавлен ранее!'
        )
        return

    await message.answer(
        'Студент добавлен!'
    )


@router.message(Command('add_admin'))
async def new_admin(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            'Ошибка: не переданы айди и название группы'
        )
        return
    try:
        admin_chat_id, admin_group_name = command.args.split(' ', maxsplit=1)
    except ValueError:
        await message.answer(
            'Ошибка: неправильный формат команды. Пример:\n'
            '/add_admin <id> <group_name>'
        )
        return

    db = DBase.Database()
    current_chat = f'{message.from_user.id}'
    if not db.is_powered(admin_group_name, current_chat):
        await message.answer(
            'У вас недостаточно прав, чтобы добавлять админов в эту группу!'
        )
        return

    execution_code = db.add_admin(admin_group_name, admin_chat_id)

    if execution_code < 0:
        await message.answer(
            'Неправильные id пользователя или название группы!'
        )
        return

    if execution_code == 0:
        await message.answer(
            'Этот админ уже был добавлен ранее!'
        )
        return

    await message.answer(
        'Админ добавлен!'
    )
