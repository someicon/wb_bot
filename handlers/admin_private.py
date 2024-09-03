from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypesFilter, IsAdmin
from keyboards.reply import admin_kb
from keyboards.inline import get_inline_btns
from database.orm_query import orm_add_user, orm_check_user, orm_get_user, orm_update_status


admin_private_router = Router()
admin_private_router.message.filter(ChatTypesFilter(['private']), IsAdmin())


@admin_private_router.message(Command("admin"))
async def get_admin(message: Message):
    await message.answer(
        f"{message.from_user.full_name} вы перешли в режим администратора", reply_markup=admin_kb
    )


@admin_private_router.message(F.text == "Запросы на кешбек")
async def get_user_list(message: Message, session: AsyncSession):
    for product in await orm_check_user(session, status="Cashback:send_photo_state"):
        await message.answer_photo(
            product.image,
            caption=f"{message.from_user.id}\n{message.from_user.full_name}",
            reply_markup=get_inline_btns(
                btns={
                    '✅Подтвердить✅': f'confirm_{product.user_id}',
                    '❌Отклонить❌': f'reject_{product.user_id}'
                }
            )
        )

@admin_private_router.message(F.text == "Подтвержденные запросы")
async def confirmed_user_cashback(message: Message, session: AsyncSession):
    for product in await orm_check_user(session, status="Cashback:received_cashback_state"):
        await message.answer_photo


@admin_private_router.callback_query(F.data.startswith('confirm_'))
async def confirm_cashback(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    user_id = callback.data.split("_")[-1]
    user = await orm_get_user(session, user_id)

    await callback.answer("")
    await orm_update_status(session, user.user_id, "Cashback:received_cashback_state")
    await bot.send_message(
        chat_id=user.user_id,
        text="Мы подтвердили ваш отзыв, нажмите кнопку ответ и укажите банк и реквизиты (номер телефона или карту), чтобы мы могли отправить вам кешбек",
        reply_markup=get_inline_btns(
            btns = {
                'Ответить': f'answer_{user.user_id}'
            }
        )
    )





#TODO: Добавить проверку по состоянию из бд и запись состояния в БД
