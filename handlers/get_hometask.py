from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram import Router

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.utils.media_group import MediaGroupBuilder

from keyboards import listKeyboard, listKB_date
from DataBase import DBase


class HometaskGet(StatesGroup):
    choosing_subject = State()
    choosing_date = State()


router = Router()


# Хендлер на команду /hometask
@router.message(StateFilter(None), Command('hometask'))
async def get_hometask(
        message: Message,
        state: FSMContext
):
    db = DBase.Database()
    current_chat = f'{message.from_user.id}'
    group_name = db.get_group_name(current_chat)

    if group_name is None:
        await message.answer(
            'Извините, но мы не знаем, кто вы.\n'
            f'Ваш id: `{current_chat}`\n'
            'Если вы должны быть админом - отправьте его админу этой группы или главному админу!',
            parse_mode='MARKDOWN'
        )
        return
    group_name = group_name[0]
    await state.update_data(group_name=group_name)
    subjects = db.subjects_list(group_name)
    subjects = [item[0] for item in subjects]
    await message.answer(
        'Выберете предмет:',
        reply_markup=listKeyboard.make_list_keyboard(subjects)
    )
    await state.set_state(HometaskGet.choosing_subject)


# Правильный выбор предмета
@router.callback_query(HometaskGet.choosing_subject, listKeyboard.GroupCallbackFactory.filter())
async def subject_chosen(
        callback: CallbackQuery,
        callback_data: listKeyboard.GroupCallbackFactory,
        state: FSMContext
):
    await state.update_data(chosen_subject=callback_data.value)
    data = await state.get_data()
    db = DBase.Database()
    dates = db.date_list(data['group_name'], callback_data.value)
    dates = [item[0] for item in dates]

    await callback.message.answer(
        f'Выбран предмет - {callback_data.value}\n'
        f'Выберите дату из списка:',
        reply_markup=listKB_date.make_list_keyboard(dates)
    )

    await state.set_state(HometaskGet.choosing_date)
    await callback.answer()


# Ошибочный выбор предмета
@router.message(HometaskGet.choosing_subject)
async def subject_chosen_wrong(message: Message):
    await message.answer(
        'Выберите предмет из сообщения выше\n'
        'Если вы хотите прекратить получение задания - введите /cancel'
    )


# Правильный выбор даты
@router.callback_query(HometaskGet.choosing_date, listKB_date.DateCallbackFactory.filter())
async def date_chosen(
        callback: CallbackQuery,
        callback_data: listKB_date.DateCallbackFactory,
        state: FSMContext
):
    data = await state.get_data()

    db = DBase.Database()

    hometask_id = db.get_hometask_id(data['group_name'], data['chosen_subject'], callback_data.value)

    if hometask_id is None:
        await callback.message.answer(
            'К сожалению мы не нашли такое домашнее задание\n'
            'Попробуйте ещё раз'
        )
    else:
        hometask_id = hometask_id[0]
        ht_data = db.get_hometask(hometask_id)
        await send_hometask(callback.message, hometask_id, ht_data)
    await state.clear()
    await callback.answer()


# Ошибочный выбор даты
@router.message(HometaskGet.choosing_date)
async def date_chosen_wrong(message: Message):
    await message.answer(
        'Выберите дату из сообщения выше\n'
        'Если вы хотите прекратить получение задания - введите /cancel'
    )


# Хендлер на команду /hometask_by_id
@router.message(StateFilter(None), Command('hometask_by_id'))
async def get_hometask_id(
        message: Message,
        command: CommandObject
):
    if command.args is None:
        await message.answer(
            'Ошибка: не передан айди домашнего задания'
        )
        return
    hometask_id = f'{command.args}'
    db = DBase.Database()
    ht_data = db.get_hometask(hometask_id)
    await send_hometask(message, hometask_id, ht_data)


async def send_hometask(
        message: Message,
        hometask_id,
        ht_data
):
    await message.answer(
        f'id - {hometask_id}\n'
        f'Группа - {ht_data['group']}\n'
        f'Предмет - {ht_data['subject']}\n'
        f'Дедлайн - {ht_data['date'].strftime('%d.%m.%Y')}\n'
        f'Задание:\n{ht_data['task']}\n'
    )
    images = ht_data['images']
    if len(images) == 0:
        return
    if len(images) == 1:
        await message.answer_photo(images[0], caption='Файл задания:')
        return
    album_builder = MediaGroupBuilder(
        caption="Файлы задания:"
    )
    for image in images:
        album_builder.add_photo(media=image)
    await message.answer_media_group(
        media=album_builder.build()
    )
