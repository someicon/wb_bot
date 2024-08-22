import os
from dotenv import load_dotenv

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command


admin_private_router = Router()

load_dotenv()
admins = [int(admin_id) for admin_id in os.getenv("ADMINS_ID").split(",")]


@admin_private_router.message(Command("admin"))
async def get_admin(message: Message):
    if message.from_user.id in admins:
        await message.answer("Вы админ")
    else:
        await message.answer("Вы не админ")
