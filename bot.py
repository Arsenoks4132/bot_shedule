import asyncio
import logging
from aiogram import Bot, Dispatcher
from config_reader import config

from handlers import base_commands, add_admin, add_hometask, add_student, get_hometask, anything


# Запуск процесса поллинга новых апдейтов
async def main():
    # Включение логирования
    logging.basicConfig(level=logging.INFO)
    # Получение токена и создание бота
    bot = Bot(token=config.bot_token.get_secret_value())
    # Диспетчер
    dp = Dispatcher()

    dp.include_router(base_commands.router)
    dp.include_router(add_admin.router)
    dp.include_router(add_student.router)
    dp.include_router(add_hometask.router)
    dp.include_router(get_hometask.router)
    dp.include_router(anything.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
