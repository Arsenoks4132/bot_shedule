from aiogram.types import Message
from aiogram.filters.command import Command, CommandObject
from aiogram import Router, F

from DataBase import DBase

router = Router()


# Хэндлер на команду /add_admin
@router.message(Command("add_admin"))
async def new_admin(message: Message, command: CommandObject):
    # Если не переданы никакие аргументы
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы айди и название группы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        admin_chat_id, admin_group_name = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/add_admin <id> <group_name>"
        )
        return

    db = DBase.Database()
    user_id = db.student_id(str(message.from_user.id))
    user_rule = db.admin_rule_type(user_id)
    if user_rule != 'main':
        await message.answer('У вас недостаточно прав, чтобы добавлять админов')
        return

    admin_id = db.student_id(admin_chat_id)
    if admin_id == -1:
        admin_id = db.add_student(admin_chat_id, admin_group_name)

    if admin_id == -1:
        await message.answer("Что-то пошло не так, попробуйте ещё раз!")
        return

    admin_rule = db.admin_rule_type(admin_id)
    if admin_rule != 'regular_user':
        await message.answer("Пользователь уже админ!")
        return

    db.add_admin(admin_id, admin_group_name)
    await message.answer("Админ добавлен!")


# Хэндлер на команду /add_user
@router.message(Command("add_student"))
async def new_student(message: Message, command: CommandObject):
    # Если не переданы никакие аргументы
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы айди и название группы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        student_chat_id, student_group_name = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/add_student <id> <group_name>"
        )
        return

    db = DBase.Database()
    user_id = db.student_id(str(message.from_user.id))
    user_rule = db.admin_rule_type(user_id)
    if user_rule not in ('main', student_group_name):
        await message.answer('У вас недостаточно прав, чтобы добавлять студентов в эту группу!')
        return

    student_id = db.student_id(student_chat_id)
    if student_id == -1:
        student_id = db.add_student(student_chat_id, student_group_name)
    else:
        await message.answer("Студент уже добавлен!")
        return

    if student_id == -1:
        await message.answer("Что-то пошло не так, попробуйте ещё раз!")
        return

    await message.answer("Студент добавлен!")