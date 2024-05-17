from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from DataBase import DBase
from keyboards import listKeyboard, replyListKB

from datetime import datetime

router = Router()


@router.message(Command('cancel'))
async def cancel_all(
        message: Message,
        state: FSMContext
):
    await state.clear()
    await message.answer(
        'Действие прервано!'
    )


class HometaskAdd(StatesGroup):
    choosing_group = State()
    entering_subject = State()
    entering_date = State()
    entering_text = State()
    sending_image = State()


# Хэндлер на команду /add_hometask
@router.message(StateFilter(None), Command("add_hometask"))
async def start_hometask(message: Message, state: FSMContext):
    db = DBase.Database()
    current_chat = f'{message.from_user.id}'
    groups = db.subordinate_groups(current_chat)
    if groups is None:
        await message.answer(
            'У вас нет групп, в которые вы могли бы добавить задание'
        )
        return

    group_list = [item[0] for item in groups]
    await message.answer(
        'Выберите группу для добавления задания:',
        reply_markup=listKeyboard.make_list_keyboard(group_list)
    )
    await state.set_state(HometaskAdd.choosing_group)


# Правильный выбор группы
@router.callback_query(HometaskAdd.choosing_group, listKeyboard.GroupCallbackFactory.filter())
async def group_chosen(
        callback: CallbackQuery,
        callback_data: listKeyboard.GroupCallbackFactory,
        state: FSMContext
):
    await state.update_data(chosen_group=callback_data.value)

    db = DBase.Database()
    subjects = db.subjects_list(callback_data.value)
    subjects = [item[0] for item in subjects]

    await callback.message.answer(
        f'Выбрана группа - {callback_data.value}\n'
        f'Выберите предмет из списка, или введите название нового предмета',
        reply_markup=replyListKB.make_reply_keyboard(subjects)
    )

    await state.set_state(HometaskAdd.entering_subject)
    await callback.answer()


# Ошибочный выбор группы
@router.message(HometaskAdd.choosing_group)
async def grope_chosen_wrong(message: Message):
    await message.answer(
        'Выберите группу из сообщения выше\n'
        'Если вы хотите прекратить добавление задания - введите /cancel'
    )


# Правильный выбор предмета
@router.message(HometaskAdd.entering_subject, F.text)
async def subject_entered(
        message: Message,
        state: FSMContext
):
    await state.update_data(entered_subject=message.text)
    await message.answer(
        f'Выбран предмет - {message.text}\n'
        'Введите дату, на которую задано задание\n'
        'Формат: дд.мм.гггг',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(HometaskAdd.entering_date)


# Ошибочный выбор предмета
@router.message(HometaskAdd.entering_subject)
async def subject_entered_wrong(
        message: Message
):
    await message.answer(
        'Введите предмет задания.\n'
        'Если вы хотите прекратить добавление задания - введите /cancel'
    )


# Выбор даты
@router.message(HometaskAdd.entering_date, F.text)
async def date_entered(
        message: Message,
        state: FSMContext
):
    try:
        date = datetime.strptime(message.text, '%d.%m.%Y')
        day = date.day
        month = date.month
        year = date.year
    except ValueError:
        await message.answer(
            'Вы ввели несуществующую дату либо ввели дату в неверном формате.\n'
            'Укажите реальную дату в формате дд.мм.гггг'
        )
        return

    await state.update_data(entered_date=[day, month, year])
    await message.answer(
        f'Дата сохранена!\n'
        'Введите текст домашнего задания'
    )
    await state.set_state(HometaskAdd.entering_text)


# Ошибочный выбор даты
@router.message(HometaskAdd.entering_date)
async def date_entered_wrong(
        message: Message
):
    await message.answer(
        'Введите дату задания.\n'
        'Если вы хотите прекратить добавление задания - введите /cancel'
    )


# Правильный ввод текста
@router.message(HometaskAdd.entering_text, F.text)
async def text_entered(
        message: Message,
        state: FSMContext
):
    await state.update_data(entered_text=f'{message.text}')
    await message.answer(
        f'Текст сохранён!\n'
        'Если вы хотите добавить изображения к заданию - отправляйте их по одному, но не больше 10-и штук\n'
        'Завершение создания закончится, когда вы отправите что угодно кроме изображения'
    )
    await state.set_state(HometaskAdd.sending_image)


# Ошибочный ввод текста
@router.message(HometaskAdd.entering_text)
async def text_entered_wrong(
        message: Message
):
    await message.answer(
        'Введите текст задания.\n'
        'Если вы хотите прекратить добавление задания - введите /cancel'
    )


@router.message(HometaskAdd.sending_image, F.photo)
async def image_sent(
        message: Message,
        state: FSMContext
):
    hometask_data = await state.get_data()
    if 'sent_images' not in hometask_data:
        hometask_data['sent_images'] = [f'{message.photo[-1].file_id}']
    else:
        hometask_data['sent_images'].append(f'{message.photo[-1].file_id}')

    await state.update_data(sent_images=hometask_data['sent_images'])
    await message.answer(
        f'Изображение сохранено!\n'
        f'Количество - {len(hometask_data["sent_images"])}'
    )
    if len(hometask_data) >= 10:
        await hometask_done(message, state)


@router.message(HometaskAdd.sending_image)
async def hometask_done(
        message: Message,
        state: FSMContext
):
    db = DBase.Database()
    ht_data = await state.get_data()
    hometask_id = db.add_hometask(dict(ht_data))
    if hometask_id <= 0:
        await message.answer(
            'Что-то пошло не так, попробуйте добавить задание ещё раз'
        )
        return
    await message.answer(
        'Домашнее задание добавлено!\n'
        f'Его айди - `{hometask_id}`',
        parse_mode='MARKDOWN'
    )
    await state.clear()
