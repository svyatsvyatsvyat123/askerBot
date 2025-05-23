import json

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

with open("settings.json", "r", encoding="UTF8") as f:
    __text = json.JSONDecoder().decode(f.read())
token: str = __text["token"]
questions: list[dict[str, str | list[str] | bool]] = __text["questions"]
ask_files_message = __text["ask_files_message"]
check_message = __text["check_message"]
last_message = __text["last_message"]
file_types = __text["file_types"]
answers_path = __text["answers_path"]
storage = MemoryStorage()
bot = Bot(token)
dp = Dispatcher(bot, storage=storage)
