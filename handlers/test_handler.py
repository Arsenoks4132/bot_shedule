from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router, F

rt = Router()


# Хэндлер на команду /start
@rt.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hello!")


# Хэндлер на команду /do_smth
@rt.message(Command("do_smth"))
async def cmd_dice(message: Message):
    await message.answer_dice(emoji="🎲")


@rt.message(F.text)
async def echo(message: Message):
    await message.answer(str(message.from_user.username))
