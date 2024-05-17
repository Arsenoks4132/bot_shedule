from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram import Router, F
from aiogram.utils.media_group import MediaGroupBuilder

from DataBase import DBase

router = Router()


# Хендлер на комманду /hometask_by_id
@router.message(Command('hometask_by_id'))
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
    await message.answer(
        f'id - {hometask_id}\n'
        f'Группа - {ht_data['group']}\n'
        f'Предмет - {ht_data['subject']}\n'
        f'Дедлайн - {ht_data['dl_day']}.{ht_data['dl_month']}.{ht_data['dl_year']}\n'
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