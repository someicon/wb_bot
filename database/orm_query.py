from unittest import result
from winreg import QueryInfoKey
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def orm_add_user(session: AsyncSession, state: FSMContext, message: Message):
    obj = User(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        user_name=message.from_user.full_name,
        status=await state.get_state(),
        image=message.photo[-1].file_id
    )
    session.add(obj)
    await session.commit()


async def orm_check_user(session: AsyncSession, status: str):
    query = select(User).where(User.status == status)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_status(session: AsyncSession, user_id: int, user_status: str):
    query = update(User).where(User.user_id == user_id).values(status = user_status)
    await session.execute(query)
    await session.commit()
