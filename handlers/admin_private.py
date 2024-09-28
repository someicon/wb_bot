from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypesFilter, IsAdmin
from keyboards.reply import get_keyboard, admin_kb, start_kb
from keyboards.inline import get_inline_btns
from database.orm_query import orm_update_status, orm_get_users, orm_get_user


admin_private_router = Router()
admin_private_router.message.filter(ChatTypesFilter(['private']), IsAdmin())


@admin_private_router.message(Command("admin"))
async def get_admin(message: Message):
    await message.answer(
        f"{message.from_user.full_name} вы перешли в режим администратора", reply_markup=admin_kb
    )


@admin_private_router.message(F.text == "Запросы на кешбек")
async def get_user_list(message: Message, session: AsyncSession):

    for user in await orm_get_users(session, user_status="send_photo_state"):
        await message.answer_photo(
            user.image,
            caption=f"{user.user_name}\n{user.user_full_name}",
            reply_markup=get_inline_btns(
                btns={
                    '✅Подтвердить✅': f'confirm_{user.user_id}',
                    '❌Отклонить❌': f'reject_{user.user_id}'
                }
            )
        )

# Состояния для кнопки Подтвердить


class Confirm(StatesGroup):
    confirm_state = State()


@admin_private_router.callback_query(F.data.startswith('confirm_'))
async def confirm_cashback(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])

    await state.set_state(Confirm.confirm_state)
    await state.update_data(user=user_id)
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(chat_id=callback.message.chat.id)
    await callback.message.answer(
        "Подтвердите пожалуйста еще раз",
        reply_markup=get_keyboard(
            "Подтвердить",
            "Отклонить",
            sizes=(2,)
        )
    )


@admin_private_router.message(Confirm.confirm_state, F.text == "Подтвердить")
async def send_confirmed_cashback(message: Message, bot: Bot, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    await orm_update_status(session, data['user'], "wait_credentials_state")

    await bot.send_message(
        chat_id=data['user'],
        text="Мы подтвердили ваш отзыв, нажмите кнопку ответ и укажите банк и реквизиты (номер телефона или карту), чтобы мы могли отправить вам кешбек",
        reply_markup=get_inline_btns(
            btns={
                'Отправить реквизиты': f'answer_{data['user']}'
            }
        )
    )
    await state.clear()
    await bot.delete_message(chat_id=data['chat_id'], message_id=data['message_id'])
    await message.answer(f"Сообщение отправлено пользователю",
                         reply_markup=admin_kb)


@admin_private_router.message(Confirm.confirm_state, F.text == "Отклонить")
async def back_to_menu(message: Message, state: FSMContext, bot: Bot):
    # data = await state.get_data()

    # await bot.delete_message(chat_id=data['chat_id'], message_id=data['message_id'])
    await state.clear()
    await message.answer("Отменить", reply_markup=admin_kb)


# Состояния для кнопки Отклонить

class Reject(StatesGroup):
    write_message_state = State()
    send_message_state = State()


@admin_private_router.callback_query(F.data.startswith("reject_"))
async def decline_cashback(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])

    await state.set_state(Reject.write_message_state)
    await state.update_data(chat_id=callback.message.chat.id)
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(user_id=user_id)
    await callback.message.answer("Укажите причину отказа", reply_markup=ReplyKeyboardRemove())


@admin_private_router.message(Reject.write_message_state, F.text)
async def write_text(message: Message, state: FSMContext):
    await state.set_state(Reject.send_message_state)
    await state.update_data(admin_message=message.text)

    data = await state.get_data()

    await message.answer(
        f"Проверьте данные\n\n{data["admin_message"]}",
        reply_markup=get_keyboard(
            "Отправить",
            "Изменить"
        )
    )


@admin_private_router.message(Reject.send_message_state, F.text == "Отправить")
async def send_text(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()

    await bot.send_message(
        chat_id=data["user_id"],
        text=data["admin_message"],
    )
    await orm_update_status(session, data["user_id"], "None")
    await bot.delete_message(chat_id=data["chat_id"], message_id=data["message_id"])
    await message.answer("Сообщение отправлено пользователю", reply_markup=admin_kb)

    await state.clear()


@admin_private_router.message(Reject.send_message_state, F.text == "Изменить")
async def change_text(message: Message, state: FSMContext):

    await state.set_state(Reject.write_message_state)
    await message.answer("Введите сообщение еще раз", reply_markup=ReplyKeyboardRemove())


# Отправка пользователю сообщения о его подтвержденном кешбеке


@admin_private_router.message(F.text == "Подтвержденные запросы")
async def get_user_list_cred(message: Message, session: AsyncSession):

    for user in await orm_get_users(session, user_status="send_credentials_state"):
        await message.answer_photo(
            user.image,
            caption=f"{user.user_name}\n{user.credentials}",
            reply_markup=get_inline_btns(
                btns={
                    'Кешбек': f'cashback_{user.user_id}'
                }
            )
        )


class SendCashback(StatesGroup):
    confirm_state = State()


@admin_private_router.callback_query(F.data.startswith('cashback_'))
async def send_notification(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])

    await state.set_state(SendCashback.confirm_state)
    await state.update_data(user=user_id)
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(chat_id=callback.message.chat.id)
    await callback.message.answer(
        "Подтвердите пожалуйста еще раз",
        reply_markup=get_keyboard(
            "Подтвердить",
            "Отклонить",
            sizes=(2,)
        )
    )


@admin_private_router.message(SendCashback.confirm_state, F.text == "Подтвердить")
async def confirm_send_notification(message: Message, bot: Bot, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    await orm_update_status(session, data['user'], "received_cashback_state")

    await bot.send_message(
        chat_id=data['user'],
        text="Мы зачислили вам кешбек, проверьте пожалуйста баланс",
    )

    await state.clear()
    await bot.delete_message(chat_id=data['chat_id'], message_id=data['message_id'])
    await message.answer("Сообщение о отправлено пользователю", reply_markup=admin_kb)


@admin_private_router.message(SendCashback.confirm_state, F.text == "Отклонить")
async def cancel_sending_notification(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменить", reply_markup=admin_kb)


# Отправляют реквизиты

@admin_private_router.message(F.text == "Отправляют реквизиты")
async def get_cashback_history(message: Message, session: AsyncSession):

    for user in await orm_get_users(session, user_status="wait_credentials_state"):
        await message.answer_photo(
            user.image,
            caption=f"{user.user_name}\n{user.user_full_name}",
        )


# История кешбеков

@admin_private_router.message(F.text == "История кешбеков")
async def get_cashback_history(message: Message, session: AsyncSession):

    for user in await orm_get_users(session, user_status="received_cashback_state"):
        await message.answer_photo(
            user.image,
            caption=f"{user.user_name}\n{user.user_full_name}",
        )

# Выход из режима админа

@admin_private_router.message(F.text == "Выйти из режима администратора")
async def exit_admin_menu(message: Message, state: FSMContext):

    await state.clear()
    await message.answer("Вы вышли из режима администратора", reply_markup=start_kb)


# TODO: Если пользователь уже пришло сообщение о запросе реквизитов, ему больше не будут приходить сообщения
