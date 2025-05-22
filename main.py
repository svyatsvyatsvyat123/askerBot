from aiogram import executor

from bot_create import dp, bot
from functions import init_functions
from functions.write_answers import Writer


def init_all_functions():
    init_functions(dp)


if __name__ == '__main__':
    init_all_functions()
    executor.start_polling(dp, skip_updates=True, on_startup=lambda *_, **__: Writer.open(bot),
                           on_shutdown=Writer.close)
