from aiogram import executor

from bot_create import dp, bot
from functions import init_functions
from functions.write_answers import Writer


def init_all_functions():
    init_functions(dp)


async def on_startup(*_, **__):
    await Writer.open(bot)
    print("Запуск прошел успешно")


async def on_shutdown(*_, **__):
    await Writer.close()
    print("Бот отключен")


if __name__ == '__main__':
    init_all_functions()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup,
                           on_shutdown=on_shutdown) #TODO: заменить на нормальную вещь
