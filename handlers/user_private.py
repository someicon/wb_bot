from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from keyboards.reply import get_keyboard

user_private_router = Router()


@user_private_router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Добро пожаловать в чат!", reply_markup=get_keyboard(
        "Написать в поддержку"
    ))
