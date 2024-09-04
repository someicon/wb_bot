import logging

from aiogram import F, Bot, Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.reply import get_keyboard, start_kb, cashback_kb
from filters.chat_types import ChatTypesFilter
from database.orm_query import orm_add_user, orm_create_testuser


user_private_router = Router()
user_private_router.message.filter(ChatTypesFilter(['private']))


@user_private_router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        f"Добро пожаловать в чат {message.from_user.full_name}!",
        reply_markup=start_kb
    )
    await orm_create_testuser(session,state=await state.get_state(), message=message)


@user_private_router.message(F.text == "Инструкция по подключению")
async def send_instruction(message: Message):
    video = FSInputFile(
        path=r".\files\instruction.MOV",
        filename="Инструкция.MOV"
    )

    await message.answer_video(
        video=video,
        width=720,
        height=1280,
        caption="""
<b>Выполните 3 простых действия, чтобы подключить наушники к устройству</b>

1. Включите Bluetooth на вашем устройстве
2. Откройте крышку кейса (наушники остаются в кейсе) и нажмите на кнопку на кейсе
3. Найдите в списке air pods pro 2, подключите устройство
     """
    )


@user_private_router.message(F.text == "Хрип в наушниках")
async def wheeze_headphones(message: Message):
    photo = FSInputFile(r".\files\Photo.png", filename="Фото.png")
    await message.answer_photo(photo=photo)


@user_private_router.message(F.text == "Другой вопрос")
async def ask_question(message: Message):
    await message.answer("Если у вас остались вопросы вы можете написать менеджеру @smart_pods")


# Тут включаются состояния

class Cashback(StatesGroup):
    request_cashback_state = State()
    yes_review_state = State()
    send_photo_state = State()
    received_cashback_state = State()


# @user_private_router.message(StateFilter(None), F.text == "Получить кешбек")

# @user_private_router.message(~StateFilter(Cashback.received_cashback_state), F.text == "Получить кешбек")
# async def get_cashback(message: Message, state: FSMContext):
#     current_state = await state.get_state()
#
#     if current_state == Cashback.send_photo_state:
#         await message.answer(
#             "Вы уже отправили запрос на кешбек, пожалуйста дождитесь ответа менеджера",
#             reply_markup=start_kb
#         )
#     elif current_state == Cashback.received_cashback_state:
#         await message.answer(
#             "Вы уже воспользовались кешбеком",
#             reply_markup=start_kb
#         )
#     else:
#         await message.answer(
#             """
# Чтобы получить кешбек нужно поставить 5 звезд и отправить нам скриншот из личного кабинета
# Вы уже оставили отзыв ?
#         """,
#             reply_markup=cashback_kb
#         )
#         await state.set_state(Cashback.request_cashback_state)


# @user_private_router.message(StateFilter('*'), F.text == "Назад")
# async def cancel_handler(message: Message, state: FSMContext):
#
#     current_state = await state.get_state()
#
#     if current_state == Cashback.request_cashback_state:
#         await message.answer("Вы вернулись в главное меню", reply_markup=start_kb)
#     if current_state == Cashback.yes_review_state:
#         await message.answer("Назад", reply_markup=cashback_kb)
#         await state.set_state(Cashback.request_cashback_state)
#
#
# @user_private_router.message(Cashback.request_cashback_state, F.text == "Еще не оставил отзыв")
# async def no_review(message: Message, state: FSMContext):
#     await message.answer(
#         """
# <b>Чтобы оставить отзыв, выполните следующие шаги:</b>
#
# 1. Шаг первый - описание шага.
# 2. Шаг второй - описание шага.
# 3. Шаг третий - описание шага.
#
# Благодарим за ваш отзыв!
#         """,
#         reply_markup=start_kb
#     )
#     await state.clear()
#
#
# @user_private_router.message(Cashback.request_cashback_state, F.text == "Уже оставил отзыв")
# async def yes_review(message: Message, state: FSMContext):
#     await message.answer(
#         text="Пожалуйста отпавьте скриншот с отзывом из <b>личного кабинета</b>",
#         reply_markup=get_keyboard("Назад")
#     )
#     await state.set_state(Cashback.yes_review_state)
#
#
# @user_private_router.message(Cashback.yes_review_state, F.photo)
# async def send_photo(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
#     for admin in admins_list:
#         try:
#             await bot.send_photo(chat_id=admin, photo=message.photo[-1].file_id)
#             await message.answer(
#                 "Фото отправлено, когда админ подтвердит отзыв мы запросим у вас рквизиты карты\
#                 , чтобы мы могли отправить вам кешбек",
#                 reply_markup=start_kb
#             )
#             await state.set_state(Cashback.send_photo_state)
#         except Exception as e:
#             logging.error(f"Ошибка при отправке сообщения: {e}")
#
#     await orm_add_user(session, state, message)

# cashback
