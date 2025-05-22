from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext


async def stop_FSM(message: types.Message, state: FSMContext):
    if state is not None:
        await state.finish()
        await message.answer("Успешно отменено.")
    else:
        await message.answer("на данный момент отменять нечего")


def init_other(dp: Dispatcher):
    dp.register_message_handler(stop_FSM, commands=["stop"], state="*")
