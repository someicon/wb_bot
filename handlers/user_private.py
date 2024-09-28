import logging

from aiogram import F, Bot, Router
from aiogram.types import Message, FSInputFile, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from credentials.admins import admins_list
from keyboards.reply import get_keyboard, start_kb, cashback_kb, send_credentials_kb
from filters.chat_types import ChatTypesFilter
from database.orm_query import  (orm_create_user, orm_check_user, orm_update_credentials,
                                 orm_update_status, orm_add_photo, orm_get_user)



user_private_router = Router()
user_private_router.message.filter(ChatTypesFilter(['private']))

@user_private_router.message(Command('status'))
async def cmd_get_status(message: Message, state:FSMContext):
    status = await state.get_state()
    await message.answer(text=f"{status}")


@user_private_router.message(Command('start'))
async def cmd_start(message: Message, session: AsyncSession, state:FSMContext):
    await message.answer(
        f"Добро пожаловать в чат {message.from_user.full_name}!",
        reply_markup=start_kb
    )

    user = await orm_get_user(session, message.from_user.id)
    user_exist = await orm_check_user(session, message.from_user.id)

    if user_exist:
        logging.info(f"Пользователь {message.from_user.username} уже существует в БД")
        await state.set_state(user.status)
    else:
        await orm_create_user(session, message)


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
3. Найдите в списке air pods pro 2, подключите устройство~
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
    request_cashback_state = State()    # Меню выбора оставил / не оставил кешбек
    yes_review_state = State()          # Пользователь выбрал кнопку "оставил кешбек"
    send_photo_state = State()          # Пользователь отправил фото с отзывом
    user_write_credentials = State()    # Состояние пользователь при вводе реквизитов
    send_credentials_state = State()    # Пользователь отправил реквизиты
    received_cashback_state = State()   # Менеджер отправил кешек пользователю


@user_private_router.message(StateFilter("*"), F.text == "Получить кешбек")
async def get_cashback(message: Message, state: FSMContext, session: AsyncSession):

    user = await orm_get_user(session, message.from_user.id)

    if user.status == "send_photo_state":
        await message.answer(
            "Вы уже отправили запрос на кешбек, пожалуйста дождитесь ответа менеджера",
            reply_markup=start_kb
        )
    elif user.status == "wait_credentials_state":
        await message.answer(
            "Вы уже отправили запрос на кешбек, отправьте пожалуйста свои реквизиты",
            reply_markup=start_kb
        )
    elif user.status == "send_credentials_state":
        await message.answer(
            "Вы уже отправили реквизиты, когда кешбек будет зачислен мы отправим вам сообщение",
            reply_markup=start_kb
        )
    elif user.status == "received_cashback_state":
        await message.answer(
            "Вы уже получили кешбек"
        )
    else:
        await message.answer(
            "Чтобы получить кешбек нужно поставить 5 звезд и отправить нам скриншот из личного кабинета\
            \n\nВы уже оставили отзыв ?",
            reply_markup=cashback_kb
        )
        await state.set_state(Cashback.request_cashback_state) # 1 состояние


@user_private_router.message(StateFilter('*'), F.text == "Назад")
async def cancel_handler(message: Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state == Cashback.request_cashback_state:
        await message.answer("Вы вернулись в главное меню", reply_markup=start_kb)
    if current_state == Cashback.yes_review_state:
        await message.answer("Назад", reply_markup=cashback_kb)
        await state.set_state(Cashback.request_cashback_state)  # 2 состояние


@user_private_router.message(Cashback.request_cashback_state, F.text == "Еще не оставил отзыв")
async def no_review(message: Message, state: FSMContext):
    await message.answer(
        "<b>Чтобы оставить отзыв, выполните следующие шаги:</b>\
1. Шаг первый - описание шага.\
2. Шаг второй - описание шага.\
3. Шаг третий - описание шага.\
\nБлагодарим за ваш отзыв!",
        reply_markup=start_kb
    )
    await state.clear()


@user_private_router.message(Cashback.request_cashback_state, F.text == "Уже оставил отзыв")
async def yes_review(message: Message, state: FSMContext):

    await message.answer(
        text="Пожалуйста отправьте в чат скриншот с отзывом из <b>личного кабинета</b>",
        reply_markup=get_keyboard("Назад")
    )

    await state.set_state(Cashback.yes_review_state)


@user_private_router.message(Cashback.yes_review_state, F.photo)
async def send_photo(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):

    photo = message.photo[-1].file_id

    try:
        await state.set_state(Cashback.send_photo_state)    # 3 состояние
        await orm_update_status(session, message.from_user.id, "send_photo_state")
        await orm_add_photo(session, message.from_user.id, photo)
    except Exception as e:
        logging.error(f"Ошибка при занесении пользователя в базу: {e}")
        await message.answer("Ошибка при отправке фото, попробуйте еще раз", reply_markup=cashback_kb)
    else:
        await message.answer(
            "Фото отправлено. Когда менеджер подтвердит отзыв, запросим реквизиты для начисления кешбека.",
            reply_markup=start_kb
        )

        for admin in admins_list:
            try:
                await bot.send_message(admin, f"Пользователь @{message.from_user.username} отправил запрос на кешбек")
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения админу: {e}")


# Тут включается состояние когда пользователь вводит свои реквизиты

@user_private_router.callback_query(Cashback.send_photo_state, F.data.startswith('answer_'))
async def get_user_credentials(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):

    await state.set_state(Cashback.user_write_credentials)    #4 состояние
    await orm_update_status(session, message.from_user.id, "user_write_credentials")
    await bot.send_message(
        chat_id=message.from_user.id,
        text="Ниже укажите реквизиты как в одном из примеров указаных ниже:\
        \nСбербанк - номер карты 111 111 222 444 555\
        \nВТБ - номер телефона +79291234567",
        reply_markup=ReplyKeyboardRemove()
    )




@user_private_router.message(Cashback.user_write_credentials,  F.text)
async def user_write_credentials(message: Message, state:FSMContext, session:AsyncSession):
    await orm_update_credentials(session,message.from_user.id, message.text)
    await message.answer(
        f"Проверьте правильность введнных данных\n{message.text}",
        reply_markup=send_credentials_kb
        )

    await state.set_state(Cashback.send_credentials_state)    # 5 состояние



@user_private_router.message(Cashback.send_credentials_state, F.text == "Отправить реквизиты")
async def send_credentials(message: Message,session: AsyncSession, state:FSMContext, bot: Bot):

    await orm_update_status(session, message.from_user.id, "send_credentials_state")

    await message.answer(
        text="Ваши данные отправлены, мы отправим вам сообщение, когда кешбек будет зачислен на карту",
        reply_markup=start_kb
    )

    await state.clear()

    for admin in admins_list:
            try:
                await bot.send_message(admin, f"Пользователь @{message.from_user.username} отправил реквизиты")
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения админу: {e}")


@user_private_router.message(Cashback.send_credentials_state, F.text == "Ввести реквизиты заново")
async def send_credentials_again(message: Message, state: FSMContext, session: AsyncSession):

    await state.set_state(Cashback.user_write_credentials)
    await orm_update_status(session, message.from_user.id, "user_write_credentials")
    await message.answer("Введите реквизиты заново", reply_markup=ReplyKeyboardRemove())

# TODO: Разделить состояния
