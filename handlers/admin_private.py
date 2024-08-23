from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from filters.chat_types import ChatTypesFilter, IsAdmin


admin_private_router = Router()
admin_private_router.message.filter(ChatTypesFilter(['private']), IsAdmin())


@admin_private_router.message(Command("admin"))
async def get_admin(message: Message):
    await message.answer(f"{message.from_user.full_name} вы Администратор")

#admin

# test
