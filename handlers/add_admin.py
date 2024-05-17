from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from DataBase import DBase
from keyboards import listKeyboard


class AdminAdd(StatesGroup):
    entering_Group_Name = State()
    entering_Chat_Id = State()


router = Router()


# Хендлер на команду /add_admin
@router.message(StateFilter(None), Command('add_admin'))
async def new_admin(
        message: Message,
        state: FSMContext
):
    db = DBase.Database()
    current_chat = f'{message.from_user.id}'
    groups = db.subordinate_groups(current_chat)
    if groups is None:
        await message.answer(
            'У вас нет групп, в которые вы могли бы добавить админа'
        )
        return

    group_list = [item[0] for item in groups]
    await message.answer(
        'Выберите группу для добавления админа:\n'
        'Если нужной группы нет в списке - отправьте её название сообщением',
        reply_markup=listKeyboard.make_list_keyboard(group_list)
    )
    await state.set_state(AdminAdd.entering_Group_Name)


# Правильный выбор группы
@router.callback_query(AdminAdd.entering_Group_Name, listKeyboard.GroupCallbackFactory.filter())
async def admin_group(
        callback: CallbackQuery,
        callback_data: listKeyboard.GroupCallbackFactory,
        state: FSMContext
):
    await state.update_data(chosen_group=callback_data.value)

    await callback.message.answer(
        f'Выбрана группа - {callback_data.value}\n'
        'Отправьте id админа, которого нужно зарегистрировать'
    )

    await state.set_state(AdminAdd.entering_Chat_Id)
    await callback.answer()


# Ввод группы сообщением
@router.message(AdminAdd.entering_Group_Name, F.text)
async def admin_group_text(
        message: Message,
        state: FSMContext
):
    admin_group_name = f'{message.text}'
    db = DBase.Database()
    current_chat = f'{message.from_user.id}'
    if not db.is_powered(admin_group_name, current_chat):
        await message.answer(
            'У вас недостаточно прав, чтобы добавлять админов в эту группу!'
        )
        return
    await message.answer(
        f'Выбрана группа - {admin_group_name}\n'
        'Отправьте id админа, которого нужно зарегистрировать'
    )
    await state.update_data(chosen_group=admin_group_name)
    await state.set_state(AdminAdd.entering_Chat_Id)


# Ошибочный выбор группы
@router.message(AdminAdd.entering_Group_Name)
async def admin_group_wrong(message: Message):
    await message.answer(
        'Выберите группу из сообщения выше или введите её название\n'
        'Если вы хотите прекратить добавление админа - введите /cancel'
    )


# Ввод айди админа
@router.message(AdminAdd.entering_Chat_Id, F.text)
async def admin_id(
        message: Message,
        state: FSMContext
):
    data = await state.get_data()
    admin_group_name = data['chosen_group']
    admin_chat_id = f'{message.text}'

    db = DBase.Database()
    execution_code = db.add_admin(admin_group_name, admin_chat_id)

    if execution_code < 0:
        await message.answer(
            'Что-то пошло не так, попробуйте ещё раз!'
        )
        return
    if execution_code == 0:
        await message.answer(
            'Этот админ уже был добавлен ранее!'
        )
        return
    await message.answer(
        f'Админ с айди "{admin_chat_id}" '
        f'добавлен в группу {admin_group_name}!'
    )

    await state.clear()


# Ошибочный ввод айди студента
@router.message(AdminAdd.entering_Chat_Id)
async def student_id_wrong(message: Message):
    await message.answer(
        'Введите id админа\n'
        'Если вы хотите прекратить добавление админа - введите /cancel'
    )
