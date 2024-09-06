from ast import Return
from email.mime import image
from tkinter import N
from unittest import result
from winreg import QueryInfoKey
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def orm_create_user(session: AsyncSession, message: Message):
    obj = User(
        user_id=message.from_user.id,
        user_name=message.from_user.username,
        user_full_name=message.from_user.full_name,
        status="None",
        image="None",
        credentials="None"
    )
    session.add(obj)
    await session.commit()


async def orm_check_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    user = result.scalars().first()
    return user is not None


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_get_users(session: AsyncSession, user_status: str):
    query = select(User).where(User.status == user_status)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_update_status(session: AsyncSession, user_id: int, user_status: str):
    query = update(User).where(
        User.user_id == user_id).values(status=user_status)
    await session.execute(query)
    await session.commit()


async def orm_add_photo(session: AsyncSession, user_id: int, user_photo: str):
    query = update(User).where(
        User.user_id == user_id).values(image=user_photo)
    await session.execute(query)
    await session.commit()
