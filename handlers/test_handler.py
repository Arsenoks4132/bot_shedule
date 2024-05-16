from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router, F

router = Router()


@router.message(F.photo)
async def echo(message: Message, ):
    await message.answer(f'{len(message.photo[-1].file_id)}')