from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router, F

rt = Router()


# Хэндлер на команду /start
@rt.message(Command("add_hometask"))
async def cmd_start(message: Message):
    await message.answer("Пока в разработке")
