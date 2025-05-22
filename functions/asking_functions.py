from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup as InlineMarkup, InlineKeyboardButton as InlineButton

from bot_create import questions, ask_files_message, check_message, last_message, file_types
from functions.write_answers import Writer

FSMQuestions = type("FSMQuestions", (StatesGroup,), {f"q{i}": State() for i in range(len(questions) + 2)})


async def start_asking(message: types.Message):
    query = """
    Вам будут заданы вопросы. Ответами на одни является сообщение в чат, на другие-кнопка под сообщением бота.
    Некоторые вопросы необязательные, их можно пропустить нажав кнопку под сообщением.
    В любой момент вы можете написать /stop, чтобы остановить заполнение формы. Можно будет начать заного через /start
    После всех вопросов вас попросят прикрепить файлы. Когда вы отправите все файлы, нужно будет написать любое сообщение не содержащие файлов.
    """
    await message.answer(query)
    await send_question(message, 0)
    await FSMQuestions.__dict__["q0"].set()


async def send_question(message: types.Message, ind: int):
    if ind == len(questions):
        await message.answer(ask_files_message)
        return
    text = questions[ind]["query"]
    choices = questions[ind]["choice"]
    if questions[ind]["skip"]:
        choices.append("Пропустить")
    if len(choices) == 0:
        await message.answer(text)
        return
    kb = InlineMarkup(row_width=3)
    for i in choices:
        kb.insert(InlineButton(f"{i}", callback_data=f"q{ind} {i}"))
    await message.answer(text, reply_markup=kb)
    if questions[ind]["skip"]:
        choices.pop(-1)


def init_question(ind: int, dp: Dispatcher):
    async def message_handler(message: types.Message, state: FSMContext):
        text = message.text
        if len(text) == 0:
            await message.answer("Вы ввели пустое сообщение, ответьте на вопрос заного. Вы должны ввести текст")
            return
        async with state.proxy() as data:
            if questions[ind]['name'] is not None:
                data[f"{questions[ind]['name']}"] = text
        await send_question(message, ind + 1)
        await FSMQuestions.next()

    async def query_handler(callback: types.CallbackQuery, state: FSMContext):
        text = ' '.join(callback.data.split()[1:])
        if text == "Пропустить":
            text = ""
            await callback.answer("Пропущено")
        else:
            await callback.answer("Принято")
        async with state.proxy() as data:
            if questions[ind]['name'] is not None:
                data[f"{questions[ind]['name']}"] = text
        await send_question(callback.message, ind + 1)
        await FSMQuestions.next()

    if len(questions[ind]["choice"]) != 0 or questions[ind]["skip"]:
        dp.register_callback_query_handler(query_handler, lambda x: x.data and x.data.startswith(f'q{ind} '),
                                           state=FSMQuestions.__dict__[f"q{ind}"])
    if len(questions[ind]["choice"]) == 0:
        dp.register_message_handler(message_handler, state=FSMQuestions.__dict__[f"q{ind}"])


async def get_files(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data.get("cnt", "none") == "none":
            data["cnt"] = "0"
            data["files_id"] = ""
            data["files_size"] = "0.0"
            data["files_names"] = ""
        if int(data["cnt"]) >= 20:
            await message.reply("Файлов не может быть больше 20")
            return
        name: str = message.document.file_name.split(".")[-1]
        if name not in file_types:
            await message.reply(f"Некорректное расширение файла. Должно быть:\n{' '.join(file_types)}")
        if float(data["files_size"]) + message.document.file_size / 1024 / 1024 > 18:
            await message.reply(f"Суммарный размер файлов не более 18МБ")
        data["files_id"] = data["files_id"] + " " + message.document.file_id
        data["files_names"] = data["files_names"] + " " + name
        data["cnt"] = str(int(data["cnt"]) + 1)
        data["files_size"] = str(float(data["files_size"]) + message.document.file_size / 1024 / 1024)


async def stop_get_file(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data.get("cnt","0") == "0":
            await message.answer("Вы не ввели не одного файла. Отправьте файл")
            return
        await message.answer(check_message)
        text = "Ваши ответы:\n"
        for i in range(len(questions)):
            if questions[i]["name"] is None:
                continue
            text += f"{questions[i]['name']}:{data[questions[i]['name']]}\n"
        text += f"Кол-во файлов: {data['cnt']}\nСуммарный размер: {data['files_size']} МБ\n"
        kb = InlineMarkup()
        kb.insert(InlineButton("Подтверждаю", callback_data=f"q{len(questions) + 1} "))
        await message.answer(text, reply_markup=kb)
    await FSMQuestions.next()


async def end_asking(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Начинаю скачивание")
    async with state.proxy() as data:
        await Writer.write(data)
    await callback.message.answer(last_message)
    await state.finish()


def init_asking_functions(dp: Dispatcher):
    dp.register_message_handler(start_asking, state='*', commands=["start"])
    for i in range(len(questions)):
        init_question(i, dp)

    dp.register_message_handler(get_files, state=FSMQuestions.__dict__[f"q{len(questions)}"],
                                content_types=["photo", "document"])
    dp.register_message_handler(stop_get_file, state=FSMQuestions.__dict__[f"q{len(questions)}"])
    dp.register_callback_query_handler(end_asking, lambda x: x.data and x.data.startswith(f'q{len(questions) + 1} '),
                                       state=FSMQuestions.__dict__[f"q{len(questions) + 1}"])
