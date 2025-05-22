from aiogram import Dispatcher

from .asking_functions import init_asking_functions
from .other import init_other


def init_functions(dp: Dispatcher):
    init_other(dp)
    init_asking_functions(dp)
