import asyncio
from aiogram import Bot, Dispatcher
from config_reader import config

from handlers import new_student, add_users, test_handler, add_hometask, get_hometask


# Запуск процесса поллинга новых апдейтов
async def main():
    # Получение токена и создание бота
    bot = Bot(token=config.bot_token.get_secret_value())
    # Диспетчер
    dp = Dispatcher()
    dp.include_routers(add_hometask.router, test_handler.router, new_student.router, add_users.router, get_hometask.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())