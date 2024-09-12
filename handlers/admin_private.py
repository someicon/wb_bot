from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypesFilter, IsAdmin
from keyboards.reply import get_keyboard, admin_kb
from keyboards.inline import get_inline_btns
from database.orm_query import orm_update_status, orm_get_users


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


@admin_private_router.callback_query(F.data.startswith('confirm_'))
async def confirm_cashback(callback: CallbackQuery, bot: Bot):

    user_id = int(callback.data.split("_")[-1])

    await bot.send_message(
        chat_id=user_id,
        text="Мы подтвердили ваш отзыв, нажмите кнопку ответ и укажите банк и реквизиты (номер телефона или карту), чтобы мы могли отправить вам кешбек",
        reply_markup=get_inline_btns(
            btns={
                'Отправить реквизиты': f'answer_{user_id}'
            }
        )
    )

    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.answer("Сообщение отправлено пользователю")

# состояния для кнопки отклонить


class Reject(StatesGroup):
    write_message_state = State()
    send_message_state = State()


@admin_private_router.callback_query(F.data.startswith("reject_"))
async def decline_cashback(callback: CallbackQuery, bot: Bot, state: FSMContext):

    await state.set_state(Reject.write_message_state)

    user_id = int(callback.data.split("_")[-1])

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


# Подтверждение кешбеков
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


@admin_private_router.callback_query(F.data.startswith('cashback_'))
async def confirm_cashback(callback: CallbackQuery, session: AsyncSession, bot: Bot):

    user_id = int(callback.data.split("_")[-1])

    await callback.answer("")
    await bot.send_message(
        chat_id=user_id,
        text="Мы зачислили кешбек на карту",
    )

    await orm_update_status(session, user_id, "received_cashback_state")

    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.answer("Сообщение отправлено пользователю")


# Выход из режима админа
