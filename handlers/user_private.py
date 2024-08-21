from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from loguru import logger


from keyboards.reply import get_keyboard
from misc.user_functions import create_msg

user_private_router = Router()


@user_private_router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        f"Добро пожаловать в чат {message.from_user.full_name}!",
        reply_markup=start_kb
    )

start_kb = get_keyboard(
    "Получить кешбек",
    "Инструкция по подключению",
    "Хрип в наушниках",
    "Другой вопрос",
    placeholder="Выберете пункт меню",
    sizes=(1, 1, 2)
)


@user_private_router.message(F.text == "Инструкция по подключению")
async def send_instruction(message: Message):
    video = FSInputFile(path=r".\files\instruction.MOV",
                        filename="Инструкция.MOV")
    text = create_msg(
        "Выполните 3 простых действия, чтобы подключить наушники к устройству\n\n",
        "1. Включите Bluetooth на вашем устройстве\n",
        "2. Откройте крышку кейса (наушники остаются в кейсе) и нажмите на кнопку на кейсе\n",
        "3. Найдите в списке air pods pro 2, подключите устройство\n"
    )
    await message.answer_video(video, caption=text, width=720, height=1280)


@user_private_router.message(F.text == "Хрип в наушниках")
async def wheeze_headphones(message: Message):
    photo = FSInputFile(r".\files\Photo.png", filename="Фото.png")
    await message.answer_photo(photo=photo)


@user_private_router.message(F.text == "Другой вопрос")
async def ask_question(message: Message):
    await message.answer("Если у вас остались вопросы вы можете написать менеджеру @smart_pods")
